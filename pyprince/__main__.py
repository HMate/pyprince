#!/usr/bin/python3
from pyprince import console_entry_main

# TODO:
# - Built npm module will be only compatible with python version it was built from.
#   The cause of this was orjson. I removed it. See how can we make compatibility work.
# - Add tests for the npm package for every python version.

# TODO: 0.0.6:
# - Also serialize package path - needs structure for packages
# - Convert entry to flask app
# - api endpoint to parse selected module by name
# - api endpoint to parse from entrypoint script and shallow parse other modules
# - api endpoint to parse all recusively.

if __name__ == "__main__":
    console_entry_main()
