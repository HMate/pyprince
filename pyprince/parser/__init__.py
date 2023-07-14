import inspect
import traceback
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional
import importlib, importlib.util

from pyprince.parser.Project import Project
import pyprince.logger as logger

import libcst


def parse_project(entry_file: Path) -> Project:
    modules = parse_modules_recursively(entry_file)

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


def parse_modules_recursively(entry_file: Path) -> Optional[ModuleType]:
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

    # This is for debbugging, to see which on which module include path did we arrive here
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
