import queue
import sys
import os
from pathlib import Path
from typing import Optional, Tuple, Union, List

import libcst

from pyprince.parser import constants
from pyprince.parser.import_handler import ImportHandler
from pyprince.parser.module_finder import ModuleFinder
from pyprince.parser.package_finder import PackageFinder
from pyprince.parser.project import ModuleIdentifier, Package, PackageType, Project, Module
from pyprince.logger import logger
from pyprince.parser.project_cache import ProjectCache


def parse_project(
    entry_file: Path,
    project_cache: Optional[ProjectCache] = None,
    shallow_stdlib: bool = False,
    shallow_site_packages: bool = False,
) -> Project:
    """
    Parses in all the module files starting from an entry_file.
    If project_cache is not None, modules will be loaded from there, instead of parsing them in from the filesystem.

    When 'shallow_stdlib' param is true, we wont include the whole stdlib,
    just the surface modules that other modules include.
    When 'shallow_site_packages' is true, we include only the surface modules of packages that are in site-packages.
    """
    parser = ProjectParser(project_cache, shallow_stdlib, shallow_site_packages)
    return parser.parse_project_from_entry_script(entry_file)


class ProjectParser:
    def __init__(self, project_cache: Optional[ProjectCache], shallow_stdlib: bool, shallow_site_packages: bool):
        self.proj = Project()
        self.finder = ModuleFinder()
        self.package_finder = PackageFinder(self.proj)
        self.import_handler = ImportHandler(self.finder)

        self.project_cache = project_cache or ProjectCache()
        self.shallow_stdlib = shallow_stdlib
        self.shallow_site_packages = shallow_site_packages

    def parse_project_from_entry_script(self, entry_file: Path) -> Project:
        logger.info(f"Parsing started from {entry_file.absolute()}")

        # We need to set this, because native parser can segfault without throwing an exception
        # Also the native parser will fail when running multiple testcases,
        # because then it tries to initialize it multiple times.
        # See: https://github.com/Instagram/LibCST/issues/980
        os.environ["LIBCST_PARSER_TYPE"] = "pure"

        # For the root file of the project, it may not be in the sys.path, so we add it so importlib can find it
        sys.path = [str(entry_file.parent)] + sys.path
        self.finder.update_toplevel_module_paths(sys.path)

        root_name = entry_file.stem
        root: Module = self._parse_module(ModuleIdentifier(root_name))

        self.proj.add_root_module(root.name)
        self.proj.add_module(root)

        root_package: Package = self.package_finder.find_package(root)
        self.proj.add_package(root_package)
        root_package.add_module(root.id)

        self.import_handler.resolve_module_imports(root)
        remaining_modules = queue.SimpleQueue()
        for sub in root.submodules:
            remaining_modules.put(sub)

        while not remaining_modules.empty():
            next_module: ModuleIdentifier = remaining_modules.get()
            if self.proj.has_module(next_module.name):
                continue
            cached_module = self.project_cache.find_in_cache(next_module)
            if cached_module is None:
                mod = self._parse_module(next_module)
                if mod is None:
                    continue
                self.proj.add_module(mod)
                self.import_handler.resolve_module_imports(mod)
            else:
                mod = cached_module
                self.proj.add_module(mod)
                self.import_handler.resolve_module_imports(mod)

            package = self._resolve_module_package(mod)
            if self._does_shallow_parsing_apply(package):
                continue

            for sub in mod.submodules:
                if not self.proj.has_module(sub.name):
                    remaining_modules.put(sub)
        sys.path = sys.path[1:]
        logger.success(f"Parsing finished for {entry_file.absolute()}")
        return self.proj

    def _parse_module(self, module_id: ModuleIdentifier) -> Module:
        try:
            return self._parse_module_unchecked(module_id)
        except Exception as e:
            logger.exception(f"Error in _parse_module for module {module_id.name}")
        mod = Module(module_id, None, None)
        return mod

    def _parse_module_unchecked(self, module_id: ModuleIdentifier) -> Module:
        logger.info(f"Parsing module {module_id.name}")
        if module_id.name == "__main__":
            # __main__ module is technically the currently loaded top module,
            # but we dont have any reasons right now to deal with that.
            mod = Module(module_id, None, None)
            return mod

        module_path = self.find_module_path(module_id)
        if module_path is None:
            # I guess there can be multiple reasons.
            # One reason is when the import is platform specific. For example pwd is unix only
            mod = Module(module_id, None, None)
            return mod
        if not self.finder.is_parsable_origin(module_path):
            mod = Module(module_id, module_path, None)
            return mod

        if module_id.name == "pydoc_data.topics":
            # TODO: Right now libcst crashes on this file when parsing or when enumerating imports.
            # For now it does not affect us if we just skip the file.
            # In the future we may want to switch to parso/ast module, or hope it gets fixed.
            mod = Module(module_id, module_path, None)
            return mod

        logger.debug(f"Parsing module {module_id.name} from {module_path}")
        content = Path(module_path).read_bytes()  # TODO: DI FileLoader
        cst: libcst.Module = libcst.parse_module(content)
        mod = Module(module_id, module_path, cst)
        return mod

    def _resolve_module_package(self, mod: Module) -> Package:
        package: Package = self.package_finder.find_package(mod)
        package.add_module(mod.id)
        if not self.proj.has_package(package.name):
            self.proj.add_package(package)
        return package

    def _does_shallow_parsing_apply(self, package: Package) -> bool:
        if self.shallow_stdlib and package.package_type == PackageType.StandardLib:
            return True
        elif self.shallow_site_packages and package.package_type == PackageType.Site:
            return True
        return False

    def find_module_path(self, module_id: ModuleIdentifier):
        spec = self.finder.find_spec(module_id.name) if module_id.spec is None else module_id.spec
        if spec is None:
            return None
        return spec.origin
