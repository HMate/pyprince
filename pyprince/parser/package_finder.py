from pathlib import Path
import sys
import sysconfig

from pyprince.parser import constants
from pyprince.parser.project import Module, Package, PackageType, Project


class PackageFinder:
    STDLIB_PACKAGE = Package(constants.STDLIB_PACKAGE_NAME, sys.base_prefix, PackageType.StandardLib)

    def __init__(self, project: Project) -> None:
        self.proj = project

    def find_package(self, module: Module) -> Package:
        if self._is_part_of_stdlib(module):
            return self.STDLIB_PACKAGE

        if module.path is None:
            raise RuntimeError(f"There was no path for non-std module: {module.name}")
        module_path = Path(module.path)
        package_type = PackageType.Unknown

        module_parts = module.name.split(".")
        if len(module_parts) > 1:
            package_name = module_parts[0]
        elif module_path.is_relative_to(self.get_site_packages_path()):
            package_name = module.name
            package_type = PackageType.Site
        else:
            package_name = module_path.parent.stem
            package_type = PackageType.Local

        if self.proj.has_package(package_name):
            return self.proj.get_package(package_name)  # pyright: ignore
        return Package(package_name, str(module_path), package_type)

    def _is_part_of_stdlib(self, module: Module):
        if module.path is None or module.path in [constants.BUILTIN, constants.FROZEN]:
            return True
        module_path = Path(module.path)

        if module_path.is_relative_to(sys.prefix) or module_path.is_relative_to(sys.base_prefix):
            if module_path.is_relative_to(self.get_site_packages_path()):
                return False
            return True
        return False

    @staticmethod
    def get_site_packages_path():
        return sysconfig.get_path("platlib")
