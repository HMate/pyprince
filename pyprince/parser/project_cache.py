import io
import json
from typing import Optional
from pyprince.utils.error import PyPrinceException
from pyprince.parser import constants
from pyprince.utils import logger
from pyprince.parser.project import Module, ModuleIdentifier, Package, PackageType, Project


class ProjectCache:
    SAVE_VERSION = "1.0"

    PACKAGE_NAME_TAG = "name"
    PACKAGE_PATH_TAG = "path"
    PACKAGE_SUBMODULES_TAG = "submodules"

    def __init__(self) -> None:
        self._project = Project()

    def find_in_cache(self, module_id: ModuleIdentifier) -> Optional[Module]:
        if self._project.has_module(module_id.name):
            return self._project.get_module(module_id.name)
        return None

    def serialize(self, stream: io.IOBase, project: Project):
        logger.info("Saving cache")
        std_package = project.get_package(constants.STDLIB_PACKAGE_NAME)
        if std_package is None:
            # TODO: We should save even if there is no stdlib package
            logger.warning(f"{constants.STDLIB_PACKAGE_NAME} was empty, exit from saving.")
            return

        std_save_content = self._serialize_package(project, std_package)

        save_content = {constants.VERSION_TAG: ProjectCache.SAVE_VERSION, constants.PACKAGE_TAG: {}}
        save_content[constants.PACKAGE_TAG][constants.STDLIB_PACKAGE_NAME] = std_save_content
        logger.info(f"Saving {len(std_save_content)} modules in cache for {constants.STDLIB_PACKAGE_NAME}")
        json.dump(save_content, stream, indent=4)

    def _serialize_package(self, project: Project, package: Package):
        package_content = {}
        for module_name in package.modules:
            module = project.get_module(module_name)
            if module is None:
                raise PyPrinceException(f"Module '{module_name}' was in project packages, but not in modules")
            package_content[module.name] = {
                ProjectCache.PACKAGE_NAME_TAG: module_name,
                ProjectCache.PACKAGE_PATH_TAG: module.path,
            }
            submodules = [sub.name for sub in module.submodules]
            if len(submodules) > 0:
                package_content[module.name][ProjectCache.PACKAGE_SUBMODULES_TAG] = submodules
        return package_content

    def load_stream(self, stream: io.IOBase):
        logger.info("Loading cache")
        content = stream.read()
        if len(content) > 0:
            saved_content = json.loads(content)
        else:
            return

        if not isinstance(saved_content, dict):
            logger.warning("Cache was not dict, stop loading")
            return

        if constants.VERSION_TAG not in saved_content:
            logger.warning("Cache is missing version, stop loading")
            return

        logger.info(f"Loading cache version: {saved_content[constants.VERSION_TAG]}")
        for package_name, modules in saved_content[constants.PACKAGE_TAG].items():
            logger.info(f"Loading package '{package_name}' in cache")
            package = Package(package_name, None, PackageType.Unknown)
            self._project.add_package(package)
            for module_name, module_info in modules.items():
                module = Module(ModuleIdentifier(module_name, None), module_info[ProjectCache.PACKAGE_PATH_TAG], None)
                self._project.add_module(module)
                package.add_module(module)

                if ProjectCache.PACKAGE_SUBMODULES_TAG in module_info:
                    for sub in module_info[ProjectCache.PACKAGE_SUBMODULES_TAG]:
                        sub_module = self._project.get_module(sub)
                        if sub_module != None:
                            module.add_submodule(sub_module)
                        else:
                            module.add_submodule(ModuleIdentifier(sub, None))
