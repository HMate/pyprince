import traceback
import sys
import os
from pathlib import Path
from typing import Optional
import importlib, importlib.util

import libcst
import libcst.matchers as cstm

from pyprince.parser.Project import Project, Module
import pyprince.logger as logger


def parse_project_new(entry_file: Path) -> Project:
    # We need to set this, because native parser can segfault without throwing an exception
    # See: https://github.com/Instagram/LibCST/issues/980
    os.environ["LIBCST_PARSER_TYPE"] = "pure"

    proj = Project()
    # For the root file of the project, it may not be in the sys.path, so we add it so importlib can find it
    sys.path = [str(entry_file.parent)] + sys.path
    root_name = entry_file.stem
    root = _parse_module(proj, root_name)
    if root is None:
        sys.path = sys.path[1:]
        return proj

    proj.add_root_module(root.name)
    proj.add_module(root)

    remaining_modules = set(root.submodules)

    while len(remaining_modules) > 0:
        next_module: str = remaining_modules.pop()
        mod = _parse_module(proj, next_module)
        if mod is None:
            continue
        proj.add_module(mod)
        for sub in mod.submodules:
            if not proj.has_module(sub):
                remaining_modules.add(sub)
    sys.path = sys.path[1:]
    return proj


def _parse_module(proj: Project, module_name: str) -> Module:
    try:
        return _parse_module_unchecked(proj, module_name)
    except Exception as e:
        logger.log(f"Error in _parse_module for module {module_name}: {e}\n{traceback.format_exc()}")
    mod = Module(module_name, None, None)
    return mod


def _parse_module_unchecked(proj: Project, module_name: str) -> Module:
    print(f"Parsing module {module_name}")
    spec = _find_module(module_name)

    if spec is None or spec.origin is None:
        # I guess there can be multiple reasons.
        # One reason is when the import is platform specific. For example pwd is unix only
        mod = Module(module_name, None, None)
        return mod
    if (
        (spec.origin in ["built-in", "frozen"])
        or (spec.origin.endswith(".pyd"))
        or (spec.origin.endswith(".pyc"))
        or (spec.origin.endswith(".pyo"))
    ):
        mod = Module(module_name, spec.origin, None)
        return mod

    if module_name == "pydoc_data.topics":
        # TODO: Right now libcst crashes on this file when parsing or when enumerating imports.
        # For now it does not affect us if we just skip the file.
        # In the future we may want to switch to parso/ast module, or hope it gets fixed.
        mod = Module(module_name, spec.origin, None)
        return mod

    content = Path(spec.origin).read_bytes()  # TODO: DI FileLoader
    cst: libcst.Module = libcst.parse_module(content)
    mod = Module(spec.name, spec.origin, cst)
    proj.add_syntax_tree(spec.name, cst)

    submodules = _extract_module_import_names(cst)
    for sub in submodules:
        sub_spec = _find_module(sub)
        if sub_spec is not None:
            mod.submodules.append(sub_spec.name)
            continue
        mod.submodules.append(sub)
    return mod


def _find_module(module_name: str):
    # TODO: Relative imports can complicate module names, we have to resolve them
    # If a module is relative, or a true child of the current module, we have to resolve its name by keeping track of the current module name
    # Maybe importlib.util.find_spec can help? It seems to rely on import for relative names, so probably not :(
    # see importlib.machinery.PathFinder or iterate htrough sys.meta_path?
    try:
        return importlib.util.find_spec(module_name)
    except (ModuleNotFoundError, ValueError):
        # ModuleNotFoundError happens for org.python.core in pickle.py
        # ValueError happens for builtins, because it does not have a spec
        return None


def _extract_module_import_names(root_cst: libcst.Module):
    # go through all the import statements and parse out the modules
    submodules: list[str] = []
    import_exprs = cstm.findall(root_cst, cstm.OneOf(cstm.Import(), cstm.ImportFrom()))
    for import_expr in import_exprs:
        logger.log(f"- {root_cst.code_for_node(import_expr)}")
        # get module name. Right now we dont use the module alias name, so we dont save it.
        if cstm.matches(import_expr, cstm.Import()):
            assert isinstance(import_expr, libcst.Import)
            for alias in import_expr.names:
                import_name = alias.evaluated_name
                if import_name not in submodules:
                    submodules.append(import_name)
        if cstm.matches(import_expr, cstm.ImportFrom()):
            assert isinstance(import_expr, libcst.ImportFrom)
            import_name = None  # TODO: Would like to log errors
            if isinstance(import_expr.module, libcst.Attribute):
                import_name = root_cst.code_for_node(import_expr.module)
            elif isinstance(import_expr.module, libcst.Name):
                import_name = import_expr.module.value
            if import_name and (import_name not in submodules):
                submodules.append(import_name)
    return submodules
