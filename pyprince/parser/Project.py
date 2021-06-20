from __future__ import annotations

from dataclasses import dataclass, field
from types import ModuleType
from typing import Iterable, Optional
import inspect

import libcst


@dataclass
class Project:
    # The mapping of aliases to importLocations
    modules: Optional[ModuleType]
    syntax_trees: dict[str, tuple[ModuleType, libcst.Module]] = field(default_factory=dict)

    def add_syntax_tree(self, module: ModuleType, st: libcst.Module):
        self.syntax_trees[module.__name__] = (module, st)

    def get_syntax_tree(self, module_name: str):
        if module_name not in self.syntax_trees:
            return None
        return self.syntax_trees[module_name][1]

    def iter_modules(self) -> Iterable[ModuleType]:
        if not self.modules:
            return
        visited = []
        yield from self._recursively_enumerate_submodules(self.modules, visited)

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
        module_name = self._find_module_for_function(func_name)
        if not module_name:
            return None
        root_cst = self.get_syntax_tree(module_name)
        for node in root_cst.children:
            if isinstance(node, libcst.FunctionDef) and node.name.value == func_name:
                return node
        else:
            return None

    def _find_module_for_function(self, func_name: str) -> Optional[str]:
        functions: list[tuple[str, function]] = inspect.getmembers(self.modules, inspect.isfunction)
        for name, func in functions:
            if name == func_name:
                return func.__module__
        return None

    # TODO: Split to classes:
    # - CodeGenerator - generate code for project/module/function
    # - CodeTransformer - Expands function calls, substitute variables, adds/removes new code nodes
    #     Xpand single function call
    #     Xpand all functions calls one level in single function
    #     Xpand all functions calls until possible in a single function
    #     Xpand all functions calls until possible in whole module (remove unused functions?)
    # - Project/Module/Function - Own AST wrappers? So searching, modifiying is easier
    #     These should also store the structure of the original source, provide mapping between the two

    # TODO: def code generators:
    # - full expand a function
    # - expand one level

    # TODO: AST alteration
    # - optimize variable usages, remove duplicated usages (asd = 7; rar = asd; => rar = 7)
    # - create variable-function dependency graph
    # - group together code with matching dependencies
