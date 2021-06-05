from dataclasses import dataclass, field
from pathlib import Path

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
    imports: dict[str, ImportLocation] = field(default_factory=dict)

    def add_import(self, name: str, node: ImportLocation):
        self.imports[name] = node
