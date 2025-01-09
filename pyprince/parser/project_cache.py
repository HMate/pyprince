import io
import json
from typing import Optional
from pyprince.error import PyPrinceException
from pyprince.parser import constants
from pyprince.logger import logger
from pyprince.parser.project import Module, ModuleIdentifier, Package, PackageType, Project


class ProjectCache:
    def __init__(self) -> None:
        self.project = Project()

    def find_in_cache(self, module_id: ModuleIdentifier) -> Optional[Module]:
        if self.project.has_module(module_id.name):
            return self.project.get_module(module_id.name)
        return None

    def serialize(self, stream: io.IOBase):
        logger.info("Saving cache")
        std_package = self.project.get_package(constants.STDLIB_PACKAGE_NAME)
        if std_package is None:
            logger.warning(f"{constants.STDLIB_PACKAGE_NAME} was empty, exit from saving.")
            return

        save_content = {}
        std_save_content = {}
        for module_name in std_package.modules:
            module = self.project.get_module(module_name)
            if module is None:
                raise PyPrinceException(f"Module '{module_name}' was in project packages, but not in modules")
            std_save_content[module.name] = {"name": module_name, "path": module.path}
        save_content[constants.STDLIB_PACKAGE_NAME] = std_save_content
        logger.info(f"Saving {len(std_save_content)} modules in cache for {constants.STDLIB_PACKAGE_NAME}")
        json.dump(save_content, stream)

    def load_stream(self, stream: io.IOBase):
        logger.info("Loading cache")
        saved_content = json.loads(stream.read())
        if not isinstance(saved_content, dict):
            logger.warning("Cache was not dict, stop loading")
            return
        for package_name, modules in saved_content.items():
            logger.info(f"Loading package '{package_name}' in cache")
            package = Package(package_name, None, PackageType.Unknown)
            self.project.add_package(package)
            for module_name, module_info in modules.items():
                module = Module(ModuleIdentifier(module_name, None), module_info["path"], None)
                self.project.add_module(module)
                package.add_module(module)
