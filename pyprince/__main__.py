#!/usr/bin/python3
from os.path import dirname

try:
    from pyprince import console_entry_main
except ModuleNotFoundError:
    # When running from npm-package, we need to add the parent directory to the path
    # So that we can import pyprince and deps from the workspace
    import sys

    sys.path.append(dirname(dirname(__file__)))
    from pyprince import console_entry_main

# TODO:
# - Either remove messages from cout, and make it proper json in every case, or do socket base communication.
# - Implement full project parser without importing modules. Look into parso vs libcst
# - Built npm module will be only compatible with python version it was built from.
#   Current cause is orjson. Either remove orjson, or see how can we make it compatible with multiple versions.
# - Add tests for the npm package for every python version.


if __name__ == "__main__":
    console_entry_main()
