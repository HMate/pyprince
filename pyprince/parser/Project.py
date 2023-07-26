from __future__ import annotations

from dataclasses import dataclass, field
from types import ModuleType
from typing import Iterable, Optional, Union
import inspect

import libcst


@dataclass
class Module:
    name: str
    path: Union[str, None]  # None means we dont know the physical location of the module
    syntax_tree: Union[libcst.Module, None]  # None means the module could not be parsed
    submodules: list[str] = field(default_factory=list)


@dataclass
class Project:
    # The mapping of aliases to importLocations
    _loaded_modules: Optional[ModuleType] = None
    _root_modules: list[str] = field(default_factory=list)
    _modules: dict[str, Module] = field(default_factory=dict)
    _syntax_trees: dict[str, libcst.Module] = field(default_factory=dict)

    def add_root_module(self, module_name: str):
        self._root_modules.append(module_name)

    def get_root_modules(self) -> list[str]:
        return self._root_modules

    def add_module(self, module: Module):
        self._modules[module.name] = module

    def has_module(self, module_name: str) -> bool:
        return module_name in self._modules

    def get_module(self, module_name: str) -> Optional[Module]:
        return self._modules.get(module_name, None)

    def get_modules(self):
        return self._modules.keys()

    def add_syntax_tree(self, module_name: str, st: libcst.Module):
        self._syntax_trees[module_name] = st

    def get_syntax_tree(self, module_name: str) -> Optional[libcst.Module]:
        if module_name not in self._syntax_trees:
            return None
        return self._syntax_trees[module_name]

    def set_loaded_modules_root(self, module: Optional[ModuleType]):
        self._loaded_modules = module
        return self

    def get_loaded_modules(self) -> Optional[ModuleType]:
        return self._loaded_modules

    def clone(self) -> Project:
        cl = Project().set_loaded_modules_root(self._loaded_modules)
        cl._syntax_trees = self._syntax_trees.copy()
        return cl

    def iter_loaded_modules(self) -> Iterable[ModuleType]:
        if not self._loaded_modules:
            return
        visited = []
        yield from self._recursively_enumerate_submodules(self._loaded_modules, visited)

    def _recursively_enumerate_submodules(self, mod: ModuleType, visited: list[ModuleType]) -> Iterable[ModuleType]:
        visited.append(mod)
        yield mod
        subs: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.ismodule)
        for name, sub in subs:
            if sub not in visited:
                yield from self._recursively_enumerate_submodules(sub, visited)

    def has_function(self, func_name: str) -> bool:
        return self.get_function(func_name) is not None

    def get_function(self, func_name: str):
        name, module = self.find_module_for_function(func_name)
        if not module:
            return None
        for node in module.children:
            if isinstance(node, libcst.FunctionDef) and node.name.value == func_name:
                return node
        else:
            return None

    def find_module_for_function(self, func_name: str) -> tuple[Optional[str], Optional[libcst.Module]]:
        functions: list[tuple[str, function]] = inspect.getmembers(self._loaded_modules, inspect.isfunction)
        for name, func in functions:
            if name == func_name:
                return func.__module__, self.get_syntax_tree(func.__module__)
        return None, None

    # TODO: Split to classes:
    # - CodeGenerator - generate code for project/module/function
    # - CodeTransformer - Expands function calls, substitute variables, adds/removes new code nodes
    #     Xpand single function call
    #     Xpand all functions calls one level in single function
    #     Xpand all functions calls until possible for a single function
    #     Xpand all functions calls until possible in whole module (remove unused functions?)
    # - Project/Module/Function - Own AST wrappers? So searching, modifiying is easier
    #     These should also store the structure of the original source, provide mapping between the two

    # TODO: AST optimization
    # - optimize variable usages, remove duplicated usages (asd = 7; rar = asd; => rar = 7)
    # - group together code with matching dependencies

    # TODO: explore data/control dependencies
    # for a given function/variable, provide in a list the chains of all dependencies up until user input locations

    # TODO: Choosable base constructs
    # while <-> for
    # functional/OO/structural

    # TODO: Create a code format that is syntax independent.
    # - parameters are order independent
    # - statements and expression are dependent on their actual dependencies, constructing a graph
