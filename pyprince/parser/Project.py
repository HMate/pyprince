from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Iterable, Optional
import inspect

import libcst


@dataclass
class ImportLocation:
    # the fully qualified import name of the parent package
    parent_name: str
    # name of the module/function/class to import
    name: str


class CSTFunctionInjector(libcst.CSTTransformer):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project

    def leave_Call(self, node: libcst.Call, updated_node: libcst.CSTNode):
        return updated_node


@dataclass
class Project:
    # The mapping of aliases to importLocations
    modules: Optional[ModuleType]
    syntax_trees: dict[str, tuple[ModuleType, libcst.Module]] = field(default_factory=dict)
    imports: dict[str, ImportLocation] = field(default_factory=dict)

    def add_import(self, name: str, node: ImportLocation):
        self.imports[name] = node

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

    def generate_code(self):
        # TODO: Extract this method to its own CodeGenerator class
        root_cst = self.get_syntax_tree(self.modules.__name__)
        return root_cst.code

    def generate_code_one_level_expanded(self, entry_func_name):
        # TODO: Extract this method to its own CodeGenerator class
        root_cst = self.get_syntax_tree(self.modules.__name__)
        for node in root_cst.children:
            if isinstance(node, libcst.FunctionDef) and node.name.value == entry_func_name:
                entry = node
                break
        else:
            return ""

        # TODO: Find places where functions are called. Remove function call node
        # Find the called function ast.
        # Replace original call with ast. Substitute func arguments into the ast.
        # In the injected ast, replace every "return" with the assignment, if there was an assignment.
        # if func call is nested inside another func call, or an other expression,
        # move result to a variable.
        # Mind indentation
        injector = CSTFunctionInjector(self)
        entry.visit(injector)

        return root_cst.code_for_node(entry)

    # TODO: def code geenrators:
    # - full expand a function
    # - expand one level

    # TODO: AST alteration
    # - optimize variable usages, remove duplicated usages (asd = 7; rar = asd; => rar = 7)
    # - create variable-function dependency graph
    # - group together code with matching dependencies
