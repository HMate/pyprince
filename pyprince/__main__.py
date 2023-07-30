#!/usr/bin/python3
from os.path import dirname

from pyprince import console_entry_main


# TODO:
# - Implement full project parser without importing modules. Look into parso vs libcst
# - Built npm module will be only compatible with python version it was built from.
#   Current cause is orjson. Either remove orjson, or see how can we make it compatible with multiple versions.
# - Add tests for the npm package for every python version.


if __name__ == "__main__":
    console_entry_main()
