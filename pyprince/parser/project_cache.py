import io
import json
from typing import Optional
from pyprince.error import PyPrinceException
from pyprince.parser import constants
from pyprince.parser.project import Module, ModuleIdentifier, Project


class ProjectCache:
    def __init__(self) -> None:
        self.project = Project()

    def find_in_cache(self, module_id: ModuleIdentifier) -> Optional[Module]:
        if self.project.has_module(module_id.name):
            return self.project.get_module(module_id.name)
        return None

    def serialize(self, stream: io.IOBase):
        std_package = self.project.get_package(constants.STDLIB_PACKAGE_NAME)
        if std_package is None:
            return

        save_content = {}
        std_save_content = {}
        for module_name in std_package.modules:
            module = self.project.get_module(module_name)
            if module is None:
                raise PyPrinceException(f"Module '{module_name}' was in project packages, but not in modules")
            std_save_content[module.name] = {"name": module_name, "path": module.path}
        save_content[constants.STDLIB_PACKAGE_NAME] = std_save_content
        json.dump(save_content, stream)
