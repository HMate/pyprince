import importlib.util
from importlib.machinery import ModuleSpec
from pathlib import Path
import sys
from typing import Dict, Optional, Sequence, Tuple

from pyprince.logger import logger
from pyprince.parser.project import ModuleIdentifier
from pyprince.parser import constants


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
        # Cache all modules we found to speed up future lookups
        self.module_cache: Dict[str, ModuleIdentifier] = dict()

    def update_toplevel_module_paths(self, paths: Sequence[str]) -> None:
        self._top_level_paths = [Path(p).resolve() for p in paths]
        self._top_level_path_strings = [str(p) for p in self._top_level_paths]

    def is_parsable_origin(self, module_origin: str) -> bool:
        return not (
            (module_origin in [constants.BUILTIN, constants.FROZEN])
            or (module_origin.endswith(".pyd"))
            or (module_origin.endswith(".pyc"))
            or (module_origin.endswith(".pyo"))
        )

    def find_top_level_module(self, module_name: str) -> ModuleIdentifier:
        """Searches for a top_level module with the given name. If the module is not found in sys.path,
        the builtin importlib is used to find it.
        If the module is not found creates an empty module with the given name.
        """
        mod_id = self.try_find_top_level_module(module_name)

        if mod_id is None:
            logger.warning(f"Could not resolve path to top-level module {module_name}")
            return ModuleIdentifier(module_name)
        assert mod_id.spec is not None
        logger.trace(f"Resolved module {mod_id.name} from {module_name} to {mod_id.spec.origin}")
        return mod_id

    def try_find_top_level_module(self, module_name: str) -> Optional[ModuleIdentifier]:
        """Searches for a top_level module with the given name. If the module is not found in sys.path,
        the builtin importlib is used to find it. If the module is not found return None.
        """
        if module_name in self.module_cache:
            return self.module_cache[module_name]
        spec = None

        if "." in module_name:
            parent_name, leaf_name = self.split_package_name(module_name)
            parent_module = self.try_find_top_level_module(parent_name)
            if (
                (parent_module is not None)
                and (parent_module.spec is not None)
                and (parent_module.spec.origin is not None)
                and self.is_parsable_origin(parent_module.spec.origin)
            ):
                search_path = Path(parent_module.spec.origin).resolve().parent
                spec = self.find_module_under_path(leaf_name, [str(search_path)])
        else:
            spec = self.find_module_under_path(module_name, self._top_level_path_strings)

        if spec is None:
            spec = self.find_spec(module_name)
            if spec is None:
                return None

        mod_id = ModuleIdentifier(module_name, spec)
        self.module_cache[module_name] = mod_id
        return mod_id

    def find_relative_module(
        self, module_name: Optional[str], relative_level: int, parent_module: ModuleIdentifier
    ) -> Optional[ModuleIdentifier]:
        """Searches for a relative module with the given name.
        Starting from the parent package looks for a relative module based on relative_level.
        If the module is not found creates an empty module with a fully qualified name derived from parent_module's name.
        If relative_level is greater then the package depth, or negative, we return None.
        """
        if relative_level < 0:
            logger.warning(
                f"Relative level was negative ({relative_level}) for module {module_name} with parent {parent_module.name}"
            )
            return None

        is_package_module = (parent_module.spec is not None) and self.is_package_module(parent_module.spec.origin)
        parent_parts = parent_module.name.split(".")
        needed_parts = len(parent_parts) - relative_level
        if is_package_module:
            needed_parts = len(parent_parts) - relative_level + 1
        if needed_parts <= 0:
            logger.warning(
                f"Could not resolve path to relative module {'.'*relative_level}{module_name} from module "
                + f"{parent_module.name}, and its relative level exceeds package depth"
            )
            return None
        leaf_part = [module_name] if module_name is not None else []
        full_module_name = ".".join(parent_parts[:needed_parts] + leaf_part)

        mod_id = self.try_find_top_level_module(full_module_name)
        if mod_id is None:
            parent_path = parent_module.spec.origin if parent_module.spec is not None else None
            logger.warning(
                f"Could not resolve path to relative module {'.'*relative_level}{module_name} from module "
                + f"{parent_module.name}({parent_path}), resolved its name to {full_module_name}"
            )
            mod_id = ModuleIdentifier(full_module_name)
        else:
            logger.trace(
                f"Resolved relative module to {mod_id.name} from module {parent_module.name} {'.'*relative_level} {module_name}"
            )
        return mod_id

    def is_package_module(self, module_path: Optional[str]) -> bool:
        """Return true if module is a package module, meaning it has an __init__ file and it can contain submodules."""
        if module_path is None:
            return False
        return Path(module_path).stem == "__init__"

    def split_package_name(self, module_name: str) -> Tuple[str, str]:
        parts = module_name.rpartition(".")
        return parts[0], parts[2]

    def find_spec(self, module_name: str, parent_name: Optional[str] = None) -> Optional[ModuleSpec]:
        """Wrapper around importlib.util.find_spec to find location of module by its full name.
        If module_name is relative (starts with .) then parent_name is used to resolve the full name.
        """
        try:
            # I was debating doing the full resolution in module_finder to avoid running unknown code for security reasons.
            # Unforunately that is very complicated. For submodule imports, python relies on interpreting the code of
            # the parent module, because the subpackage may be defined as a variable. Interpreting that is complicated.
            # So now lets just use the builtin module finder, and accept the risk of running unknown code.
            return importlib.util.find_spec(module_name, parent_name)

        except (ModuleNotFoundError, ValueError) as e:
            # ModuleNotFoundError happens for org.python.core in pickle.py
            # ValueError happens for builtins, because it does not have a spec
            logger.debug(f"Could not find module {module_name} - {e}")
            return None

    def find_module_under_path(self, name: str, path: Optional[Sequence[str]] = None) -> Optional[ModuleSpec]:
        """Look for module under a list of filesystem paths.
        Note that in case 'name' is a complex name (ie module.sub) this function will
        throw away the parent part and only looks for the sub part.
        """

        if self.path_finder is None:
            return None

        spec = self.path_finder.find_spec(name, path)
        return spec
