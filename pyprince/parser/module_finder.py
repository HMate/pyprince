import importlib.util
from importlib.machinery import ModuleSpec, PathFinder
from pathlib import Path
import sys
from typing import Optional, Sequence

from attr import has

from pyprince.logger import logger
from pyprince.parser.Project import Module, ModuleIdentifier


class ModuleFinder:
    def __init__(self) -> None:
        self.update_toplevel_module_paths(sys.path)
        self.path_finder = None
        for finder in sys.meta_path:
            if getattr(finder, "__name__", None) == "PathFinder":
                self.path_finder = finder
                break
        else:
            logger.error("Could not find PathFinder in sys.meta_path")

    def update_toplevel_module_paths(self, paths: Sequence[str]) -> None:
        self._top_level_paths = [Path(p).resolve() for p in paths]

    def find_module(self, module_name: str, parent_module: Optional[Module] = None) -> ModuleIdentifier:
        """Searches for a module with the given name.
        It first looks under the given parent package for a relative module, then with the builtin finder.
        """
        # If a module is relative, or a true child of the current module, we have to resolve its name by keeping track of the current module name
        # First see if the module exists under the parent path. This handles shadowed and relative imports.
        if parent_module is not None:
            module = self.find_relative_module(module_name, parent_module)
            if module is not None:
                return module

        spec = self.find_spec(module_name)
        if spec is None:
            if parent_module is not None:
                logger.warning(
                    f"Could not resolve path to submodule {module_name} from module {parent_module.name}({parent_module.path})"
                )
            else:
                logger.warning(f"Could not resolve path to submodule {module_name}")
            sub_id = ModuleIdentifier(module_name)
            return sub_id
        logger.trace(f"Resolved module {spec.name} from {module_name}")
        sub_id = ModuleIdentifier(spec.name, spec)
        return sub_id

    def find_relative_module(self, module_name: str, parent_module: Module) -> Optional[ModuleIdentifier]:
        """Searches for a relative module under parent_module. Returns None if there were no submodule found with the given name."""
        if parent_module.path is None:
            return None
        parent_file = Path(parent_module.path)
        search_path = parent_file.parent.resolve()
        spec = self.find_module_under_path(module_name, [str(search_path)])
        if spec is None:
            return None
        # if spec.name is already fully qualified, or we looked for a top level package then return it
        if ("." in spec.name) or (search_path in self._top_level_paths):
            logger.trace(f"Found toplevel module {module_name} - {spec.name} - under top level path {search_path}")
            return ModuleIdentifier(spec.name, spec)
        # Otherwise we have to resolve the parent module name.
        is_parent_package = self.is_package_module(parent_module)
        if is_parent_package:
            logger.trace(f"Found submodule {module_name} - {parent_module.name} > {spec.name}")
            return ModuleIdentifier(f"{parent_module.name}.{spec.name}", spec)
        # there should be a parent part, we throw away the last part
        parent = self.get_parent_package_name(parent_module)
        logger.trace(
            f"Found sibling module {module_name} - {parent} > {spec.name} from {parent_module.name} : {parent_file}"
        )
        # If parent_module.path endswith .__init__.py we are okay. Otherwise we have to deduce who is the real parent.
        return ModuleIdentifier(f"{parent}.{spec.name}", spec)

    def is_package_module(self, module: Module) -> bool:
        """Return true if module is a package module, as in it can contain submodules."""
        if module.path is None:
            return False
        parent_file = Path(module.path)
        return parent_file.stem == "__init__"

    def get_parent_package_name(self, module: Module) -> str:
        return module.name.rpartition(".")[0]

    def find_spec(self, module_name: str) -> Optional[ModuleSpec]:
        """Wrapper around importlib.util.find_spec to find location of module by its full name."""
        try:
            # I was debating doing the full resolution in module_finder to avoid running unknown code for security reasons.
            # Unforunately that is very complicated. For submodule imports, python relies on interpreting the code of
            # the parent module, because the subpackage may be defined as a variable. Interpreting that is complicated.
            # So now lets just use the builtin module finder, and accept the risk of running unknown code.
            return importlib.util.find_spec(module_name)

        except (ModuleNotFoundError, ValueError) as e:
            # ModuleNotFoundError happens for org.python.core in pickle.py
            # ValueError happens for builtins, because it does not have a spec
            logger.debug(f"Could not find module {module_name} - {e}")
            return None

    def find_module_under_path(self, name: str, path: Optional[Sequence[str]] = None) -> Optional[ModuleSpec]:
        """Look for module under a list of filesystem paths."""

        if self.path_finder is None:
            return None

        spec = self.path_finder.find_spec(name, path)
        return spec
