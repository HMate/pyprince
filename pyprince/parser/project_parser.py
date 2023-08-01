import sys
import os
from pathlib import Path
from typing import Optional, Union
import importlib, importlib.util

import libcst
import libcst.matchers as cstm

import pyprince.parser.module_finder as module_finder
from pyprince.parser.Project import ModuleIdentifier, Project, Module
from pyprince.logger import logger


def parse_project_new(entry_file: Path) -> Project:
    logger.info(f"Parsing started from {entry_file.absolute()}")
    # We need to set this, because native parser can segfault without throwing an exception
    # Also the native parser will fail when running multiple testcases,
    # because then it tries to initialize it multiple times.
    # See: https://github.com/Instagram/LibCST/issues/980
    os.environ["LIBCST_PARSER_TYPE"] = "pure"

    proj = Project()
    # For the root file of the project, it may not be in the sys.path, so we add it so importlib can find it
    sys.path = [str(entry_file.parent)] + sys.path
    root_name = entry_file.stem
    root: Module = _parse_module(ModuleIdentifier(root_name))
    if root is None:
        sys.path = sys.path[1:]
        return proj

    proj.add_root_module(root.name)
    proj.add_module(root)

    if root.syntax_tree is not None:
        proj.add_syntax_tree(root.name, root.syntax_tree)
    remaining_modules = set(root.submodules)

    while len(remaining_modules) > 0:
        next_module: ModuleIdentifier = remaining_modules.pop()
        mod = _parse_module(next_module)
        if mod is None:
            continue
        proj.add_module(mod)
        if mod.syntax_tree is not None:
            proj.add_syntax_tree(mod.name, mod.syntax_tree)
        for sub in mod.submodules:
            if not proj.has_module(sub.name):
                remaining_modules.add(sub)
    sys.path = sys.path[1:]
    logger.success(f"Parsing finished for {entry_file.absolute()}")
    return proj


def _parse_module(module_id: ModuleIdentifier) -> Module:
    try:
        return _parse_module_unchecked(module_id)
    except Exception as e:
        logger.exception(f"Error in _parse_module for module {module_id.name}")
    mod = Module(module_id.name, None, None)
    return mod


def _parse_module_unchecked(module_id: ModuleIdentifier) -> Module:
    logger.debug(f"Parsing module {module_id.name}")
    spec = _find_module(module_id.name) if module_id.spec is None else module_id.spec

    if spec is None or spec.origin is None:
        # I guess there can be multiple reasons.
        # One reason is when the import is platform specific. For example pwd is unix only
        mod = Module(module_id.name, None, None)
        return mod
    if (
        (spec.origin in ["built-in", "frozen"])
        or (spec.origin.endswith(".pyd"))
        or (spec.origin.endswith(".pyc"))
        or (spec.origin.endswith(".pyo"))
    ):
        mod = Module(module_id.name, spec.origin, None)
        return mod

    if module_id.name == "pydoc_data.topics":
        # TODO: Right now libcst crashes on this file when parsing or when enumerating imports.
        # For now it does not affect us if we just skip the file.
        # In the future we may want to switch to parso/ast module, or hope it gets fixed.
        mod = Module(module_id.name, spec.origin, None)
        return mod

    content = Path(spec.origin).read_bytes()  # TODO: DI FileLoader
    cst: libcst.Module = libcst.parse_module(content)
    mod = Module(spec.name, spec.origin, cst)
    assert mod.path is not None

    submodules = _extract_module_import_names(cst)
    parent_path = Path(mod.path).parent
    for sub in submodules:
        sub_spec = _find_module(sub, parent_path)
        if sub_spec is None:
            mod.submodules.append(ModuleIdentifier(sub))
            logger.warning(f"Could not resolve path to submodule {sub} from module {module_id.name}({parent_path})")
            continue
        mod.submodules.append(ModuleIdentifier(sub_spec.name, sub_spec))
    return mod


def _find_module(module_name: str, parent_path: Optional[Path] = None):
    # TODO: Relative imports can complicate module names, we have to resolve them
    # If a module is relative, or a true child of the current module, we have to resolve its name by keeping track of the current module name
    # Maybe importlib.util.find_spec can help? It seems to rely on import for relative names, so probably not :(
    # see importlib.machinery.PathFinder or iterate htrough sys.meta_path?

    # First see if the module exists under the parent path. This handles shadowed and relative imports.
    if parent_path is not None:
        spec = module_finder.find_module(module_name, [str(parent_path)])
        if spec is not None:
            return spec

    try:
        # I was debating doing the full resolution in module_finder to avoid running unknown code for security reasons.
        # Unforunately that is very complicated. For submodule imports, python relies on interpreting the code of
        # the parent module, because the subpackage may be defined as a variable. Interpreting that is complicated.
        # So now lets just use the builtin module finder, and accept the risk of running unknown code.
        return importlib.util.find_spec(module_name)

    except (ModuleNotFoundError, ValueError) as e:
        # ModuleNotFoundError happens for org.python.core in pickle.py
        # ValueError happens for builtins, because it does not have a spec
        logger.debug(f"Could not find module {module_name} - {e}")
        return None


def _extract_module_import_names(root_cst: libcst.Module):
    # go through all the import statements and parse out the modules
    submodules: list[str] = []
    import_exprs = cstm.findall(root_cst, cstm.OneOf(cstm.Import(), cstm.ImportFrom()))
    for import_expr in import_exprs:
        logger.debug(f"- {root_cst.code_for_node(import_expr)}")
        # get module name. Right now we dont use the module alias name, so we dont save it.
        # TODO(0.0.3): Lets handle full import names - see modules like __main__, _bootstrap in different subfolders.
        if cstm.matches(import_expr, cstm.Import()):
            assert isinstance(import_expr, libcst.Import)
            for alias in import_expr.names:
                import_name = alias.evaluated_name
                if import_name not in submodules:
                    submodules.append(import_name)
        if cstm.matches(import_expr, cstm.ImportFrom()):
            # cases:
            # If module is None and relative is none, that cannot happen. -> log error
            # - from . or ..  -> module is None, and relative is not empty
            # - from .foo -> module is a Name and relative is not empty
            # - from foo -> module is a Name and relative is empty
            # - from foo.bar -> module is an Attribute and relative is empty
            assert isinstance(import_expr, libcst.ImportFrom)
            import_name = None
            if isinstance(import_expr.module, libcst.Attribute):
                import_name = root_cst.code_for_node(import_expr.module)
            elif isinstance(import_expr.module, libcst.Name):
                import_name = import_expr.module.value
            else:
                logger.warning(f"Could not find import name - {import_expr}")
            if import_name and (import_name not in submodules):
                submodules.append(import_name)
    return submodules
