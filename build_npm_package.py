"""
This script should be run from the env that contains the runtime deps of pyprince.
It will copy all of them to the npm package.
"""
from pathlib import Path
import shutil
import sys


workspace_dir = Path(__file__).parent
package_dir = workspace_dir / "npm-package" / "pyprince"
shutil.rmtree(package_dir, ignore_errors=True)

# Copy pyprince code
code_dir = workspace_dir / "pyprince"
shutil.copytree(code_dir, package_dir)

# Copy libraries
packages = Path(sys.exec_prefix) / "Lib" / "site-packages"
shutil.copytree(packages, package_dir, dirs_exist_ok=True)

# TODO: We probably want to create a wheel out of these to have less files in the package
