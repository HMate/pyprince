import inspect
import traceback
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional, Sequence
import importlib, importlib.util

from pyprince.parser.Project import ImportLocation, Project
from pyprince.parser.ImportResolver import ImportResolver

import libcst
from libcst.tool import dump


class CSTImportResolver(libcst.CSTTransformer):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project

    def visit_Import(self, node: libcst.Import):
        """The whole of: import mod"""
        print(f"myvisit: {[nm.evaluated_name for nm in node.names]}")
        for name in node.names:
            alias = name.evaluated_alias
            if alias is None:
                alias = name.evaluated_name
            self.project.add_import(alias, ImportLocation("", name.evaluated_name))

    def visit_ImportFrom(self, node: libcst.ImportFrom):
        """The whole of: from pack import mod"""
        package = ""
        # None==node.module means we are importing relatively from own package
        # ie. from . import mod
        if node.module is not None:
            package = f"{node.module.value}."
        print(f"import from: {package}")
        if isinstance(node.names, Sequence):
            for name in node.names:
                alias = name.evaluated_alias
                if alias is None:
                    alias = name.evaluated_name
                self.project.add_import(alias, ImportLocation("", f"{package}{name.evaluated_name}"))


def parse_project(entry_file: Path) -> Project:

    # Want to: recursively inject ast from imported module in the place of module/class/function references
    # - collect all files we need ast for
    # - parse ast of files
    # - map imports to asts
    # - map module/class/function reference to ast node
    modules = parse_modules_recursively(entry_file)

    proj = Project(modules)

    for mod in proj.iter_modules():
        if (not hasattr(mod, "__path__")) and mod.__spec__.origin == "built-in":
            continue  # Module is builtin, we dont have the source
        module_path = Path(mod.__file__)
        content = module_path.read_text(encoding="UTF8")
        cst: libcst.Module = libcst.parse_module(content)
        proj.add_syntax_tree(mod, cst)

    resolver = CSTImportResolver(proj)
    # cst.visit(resolver)

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
        print(f"Error while parse_modules for {entry_file}: {e}\n{traceback.format_exc()}")
    finally:
        sys.path = sys.path[1:]
    return None


def _load_missing_modules(entry_file: Path, mod: ModuleType, visited=None):
    if visited == None:
        visited = []
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
        _import_and_load(func.__module__)
    for name, func in functions:
        _import_and_load(func.__module__)
    for name, cls in classes:
        _import_and_load(cls.__module__)

    subs: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.ismodule)
    for name, sub in subs:
        # Modules are singletons, so extending one will extend nested modules too.
        _load_missing_modules(entry_file, sub, visited)
