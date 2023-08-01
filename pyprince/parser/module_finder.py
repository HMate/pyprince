from importlib.machinery import ModuleSpec
import sys
from typing import Optional, Sequence

from pyprince.logger import logger


def find_module(name: str, path: Optional[Sequence[str]] = None) -> Optional[ModuleSpec]:
    # TODO: when name contains a submodule: ex: collections.abs, os.path
    # If submodule exists on fs, we could find it by searching folders.
    # But if submodule is just an alias from an import, we will have to interpret code, or load the parent module.
    meta_path = sys.meta_path
    for finder in meta_path:
        try:
            spec = finder.find_spec(name, path)
            if spec is not None:
                return spec
        except AttributeError:
            logger.warning(f"Finder {finder} does not have find_spec method")
    return None
