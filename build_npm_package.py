"""
This script should be run from the env that contains the runtime deps of pyprince.
It will copy all of them to the npm package.
"""
from pathlib import Path
import shutil

excluded_packages = ["setuptools"]

workspace_dir = Path(__file__).parent
package_dir = workspace_dir / "npm-package"

# Copy pyprince code
executable = workspace_dir / "build" / "pyprince.pyz"
shutil.copy2(executable, package_dir)
