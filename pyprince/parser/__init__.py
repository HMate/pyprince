import inspect
import traceback
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional
import importlib, importlib.util

import libcst
import libcst.matchers as cstm

from pyprince.parser.Project import Project, Module
import pyprince.logger as logger


def parse_project(entry_file: Path) -> Project:
    return parse_project_new(entry_file)
    # return parse_project_by_imports(entry_file)


def parse_project_new(entry_file: Path) -> Project:
    proj = Project()
    root = parse_modules_recursively(proj, entry_file)
    if root is not None:
        proj.add_root_module(root)

    return proj


def parse_modules_recursively(proj: Project, entry_file: Path) -> Optional[Module]:
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
        print(f"Error in _parse_module for {entry_file}: {e}\n{traceback.format_exc()}")
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
        print(cst.code_for_node(import_expr))
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
        if module_name == "main":
            print("debug")
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


def parse_project_by_imports(entry_file: Path) -> Project:
    modules = import_modules_recursively(entry_file)

    proj = Project(modules)

    for mod in proj.iter_modules():
        # TODO: __path__ checking conflicts with unittests for code inject and import resolve,
        #  because most normal modules do not have path. Experiment why is this check needed.
        # if not hasattr(mod, "__path__"):
        #     logger.log(f"Skipping syntax tree of {mod.__name__}, no __path__ in it")
        #     continue  # Module is builtin, we dont have the source
        if not hasattr(mod, "__file__"):
            # logger.log(f"Skipping syntax tree of {mod.__name__}, no __file__ in it")
            continue  # TODO: This is for frozen modules, like zipimport. Why no source?
        if mod.__file__ is None:
            continue  # This case if entry_file is a directory
        if mod.__file__.endswith(".pyd"):
            logger.log(f"Skipping syntax tree of {mod.__name__}, it is .pyd file")
            continue  # Module is in binary form, we dont have the source
        if mod.__file__.endswith(".so"):
            logger.log(f"Skipping syntax tree of {mod.__name__}, it is .so file")
            continue  # Module is in binary form, we dont have the source
        module_path = Path(mod.__file__)
        content = module_path.read_text(encoding="UTF8")
        cst: libcst.Module = libcst.parse_module(content)
        proj.add_syntax_tree(mod.__name__, cst)

    return proj


def import_modules_recursively(entry_file: Path) -> Optional[ModuleType]:
    """
    Recursively gathers all imported and defined modules and contained declarations.
    Currently this executes module level statements. In the future that should be fixed, as it is a security liability.
    """
    module_name = entry_file.stem
    mod = _import_module(entry_file, module_name)

    if mod is not None:
        # Modules that are implicitly loaded from "from statements" are not stored by importlib.import_module
        # So we load them ourselves
        _load_missing_modules(entry_file, mod)
    return mod


def _import_module(entry_file: Path, module_name: str):
    sys.path = [str(entry_file.parent)] + sys.path
    try:
        mod = importlib.import_module(module_name)
        return mod
    except Exception as e:
        # TODO: When run with debugger, it brings in additional imports, that should not be seen.
        # They hog down parsing + make false project nodes + fails to import some nodes: ModuleNotFoundError: No module named '<unknown>'
        print(f"Error while parse_modules for {entry_file}: {e}\n{traceback.format_exc()}")
    finally:
        sys.path = sys.path[1:]
    return None


def _load_missing_modules(entry_file: Path, mod: ModuleType, visited=None, debug_path=None):
    if visited == None:
        visited = []

    # This is for debbugging, to see we arrived here on which module include path
    if debug_path == None:
        debug_path = []
    current_debug_path = list(debug_path)
    current_debug_path.append(mod)

    if mod in visited:
        return
    visited.append(mod)
    builtins: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.isbuiltin)
    functions: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.isfunction)
    classes: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.isclass)

    names_seen = []
    names_seen.append(get_module_name(mod))

    def _import_and_load(sub: str):
        if sub in names_seen:
            return
        names_seen.append(sub)
        sub_mod = _import_module(entry_file, sub)
        if sub_mod is not None:
            if not hasattr(mod, sub):
                setattr(mod, sub, sub_mod)

    for name, func in builtins:
        if func.__module__:  # builtin functions may not have a module
            _import_and_load(func.__module__)
    for name, func in functions:
        _import_and_load(func.__module__)
    for name, cls in classes:
        _import_and_load(cls.__module__)

    subs: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.ismodule)
    for name, sub in subs:
        # Modules are singletons, so extending one will extend nested modules too.
        _load_missing_modules(entry_file, sub, visited, current_debug_path)


def get_module_name(mod: ModuleType) -> str:
    if hasattr(mod, "__spec__") and mod.__spec__ is not None:
        return mod.__spec__.name
    if hasattr(mod, "_spec__") and mod._spec__ is not None:
        return mod._spec__.name
    return mod.__name__
