import traceback
import sys
from pathlib import Path
from typing import Optional
import importlib, importlib.util

import libcst
import libcst.matchers as cstm

from pyprince.parser.Project import Project, Module
import pyprince.logger as logger


def parse_project_new(entry_file: Path) -> Project:
    proj = Project()
    root = _parse_modules_recursively(proj, entry_file)
    if root is not None:
        proj.add_root_module(root)

    return proj


def _parse_modules_recursively(proj: Project, entry_file: Path) -> Optional[Module]:
    """
    Recursively gathers all imported and defined modules and contained declarations.
    """
    module_name = entry_file.stem
    mod = _parse_root_module(proj, entry_file, module_name)
    return mod


def _parse_root_module(proj: Project, entry_file: Path, module_name: str):
    # For the root file of the project, it may not be in the sys.path, so we add it so importlib can find it
    sys.path = [str(entry_file.parent)] + sys.path
    try:
        root = _parse_module(proj, module_name)
        return root
    except Exception as e:
        # TODO: When run with debugger, it brings in additional imports, that should not be seen. Check if still true.
        # They hog down parsing + make false project nodes + fails to import some nodes: ModuleNotFoundError: No module named '<unknown>'
        logger.log(f"Error in _parse_module for {entry_file}: {e}\n{traceback.format_exc()}")
    finally:
        sys.path = sys.path[1:]
    return None


def _parse_module(
    proj: Project, module_name: str, module_cache: Optional[dict[str, Module]] = None, import_path: Optional[str] = None
):
    if module_cache is None:
        module_cache = {}
    if import_path is None:
        import_path = module_name
    # print(f"Parsing module {module_name}")
    system_modules = sys.modules
    spec = _find_module(module_name)

    if spec is None or spec.origin is None:
        # I guess there can be multiple reasons.
        # One reason is when the import is platform specific. For example pwd is unix only
        mod = Module(module_name, None, None)
        module_cache[module_name] = mod
        return mod
    if (
        (spec.origin == "built-in")
        or (spec.origin.endswith(".pyd"))
        or (spec.origin.endswith(".pyc"))
        or (spec.origin.endswith(".pyo"))
    ):
        mod = Module(module_name, spec.origin, None)
        module_cache[module_name] = mod
        return mod

    content = Path(spec.origin).read_bytes()  # TODO: DI FileLoader
    cst: libcst.Module = libcst.parse_module(content)
    mod = Module(spec.name, spec.origin, cst)
    proj.add_syntax_tree(spec.name, cst)
    module_cache[spec.name] = mod
    # go through all the import statements and parse out the modules
    submodules = []
    import_exprs = cstm.findall(cst, cstm.OneOf(cstm.Import(), cstm.ImportFrom()))
    for import_expr in import_exprs:
        logger.log(cst.code_for_node(import_expr))
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
                import_name = cst.code_for_node(import_expr.module)
            elif isinstance(import_expr.module, libcst.Name):
                import_name = import_expr.module.value
            if import_name and (import_name not in submodules):
                submodules.append(import_name)
    for sub in submodules:
        sub_spec = _find_module(sub)
        if (sub_spec is not None) and (sub_spec.name in module_cache):
            mod.submodules.append(module_cache[sub_spec.name])
            continue
        sub_mod = _parse_module(proj, sub, module_cache, f"{import_path} - {sub}")
        mod.submodules.append(sub_mod)
    return mod


def _find_module(module_name: str):
    # TODO: Relative imports can complicate module names, we have to resolve them
    # If a module is relative, or a true child of the current module, we have to resolve its name by keeping track of the current module name
    # Maybe importlib.util.find_spec can help? It seems to rely on import for relative names, so probably not :(
    # see importlib.machinery.PathFinder or iterate htrough sys.meta_path?
    try:
        return importlib.util.find_spec(module_name)
    except ModuleNotFoundError:
        # For example this error happens for org.python.core in pickle.py
        return None
