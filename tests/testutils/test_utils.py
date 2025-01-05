from pathlib import Path
import sys
import sysconfig
from typing import Union

from pyprince.parser.package_finder import PackageFinder
from pyprince.parser.project import Module, ModuleIdentifier


def get_test_scenarios_dir() -> Path:
    return Path(__file__).parent.parent / "test_scenarios"


def stdlib_path():
    return Path(PackageFinder.get_stdlib_path())


# Tests can import modules during run, we want to unimport them before next run
known_mod_keys = None


def remove_imported_modules():
    """Remove modules that were imported during a previous test run"""
    global known_mod_keys
    mod_keys = set(sys.modules.keys())
    if known_mod_keys:
        unknown = mod_keys.difference(known_mod_keys)
        if unknown:
            for key in unknown:
                sys.modules.pop(key)
    known_mod_keys = set(sys.modules.keys())


def create_module(name: str, path: Union[str, Path, None] = None) -> Module:
    module = Module(ModuleIdentifier(name, None), str(path) if path is not None else None, None)
    return module
