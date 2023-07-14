# This script builds pyprince for npm. To invoke this script:
# 1. activate the poetry virtual env: poetry shell
# 2. run this script: python build_package.py
import itertools

import PyInstaller.__main__
from stdlib_list import stdlib_list

# This is a hack to include all stdlib modules, otherwise pyinstaller will not include them,
# and pyprince wont be able to find them.
# So we list them all, and turn on the noarchive debug option to make them explicit files.
libs = stdlib_list()
# We remove test.* modules, because they fail the exe build, and they are interanl only anyway
libs = [x for x in libs if not x.startswith("test.")]
args = ["--hidden-import"] * len(libs)
hiddenimports = [x for x in itertools.chain.from_iterable(itertools.zip_longest(args, libs)) if x]

PyInstaller.__main__.run(
    [
        "pyprince/__main__.py",
        "--name",
        "pyprince",
        "--distpath",
        "npm-package",
        "--specpath",
        "build",
        "--onedir",
        "--clean",
        "--noconfirm",
        "--win-private-assemblies",
        *hiddenimports,
        "--debug",
        "noarchive",
    ]
)
