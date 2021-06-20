from pathlib import Path
import sys


def get_test_scenarios_dir() -> Path:
    return Path(__file__).parent.parent / "test_scenarios"


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


from .PackageGenerator import PackageGenerator