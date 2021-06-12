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
        return ""
