from typing import Optional
from pyprince.parser.project import Module, ModuleIdentifier, Project


class ProjectCache:
    def __init__(self) -> None:
        self.project = Project()

    def find_in_cache(self, module_id: ModuleIdentifier) -> Optional[Module]:
        if self.project.has_module(module_id.name):
            return self.project.get_module(module_id.name)
        return None
