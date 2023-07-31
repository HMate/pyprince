from importlib.machinery import ModuleSpec
import sys
from typing import Optional

from pyprince.logger import logger


class ModuleFinder:
    def find_module(self, name, path=None) -> Optional[ModuleSpec]:
        meta_path = sys.meta_path
        for finder in meta_path:
            try:
                spec = finder.find_spec(name, path)
                if spec is not None:
                    return spec
            except AttributeError:
                logger.warning(f"Finder {finder} does not have find_spec method")
        return None
