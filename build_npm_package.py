"""
This script should be run from the env that contains the runtime deps of pyprince.
It will copy all of them to the npm package.
"""
from pathlib import Path
import shutil
import sys
import subprocess


workspace_dir = Path(__file__).parent
package_dir = workspace_dir / "npm-package" / "pyprince"
shutil.rmtree(package_dir, ignore_errors=True)

# Copy pyprince code
code_dir = workspace_dir / "pyprince"
shutil.copytree(code_dir, package_dir)

res = subprocess.run("poetry export -f requirements.txt --without-hashes".split(), capture_output=True, check=True)
deps_raw = res.stdout.decode("utf-8").splitlines()

# Copy libraries
site_packages = Path(sys.exec_prefix) / "Lib" / "site-packages"
for dep_line in deps_raw:
    if (not dep_line) or ("==" not in dep_line):
        continue
    parts = dep_line.split(";")
    dep = parts[0].split("==")[0].replace("-", "_")
    dep_version = parts[0].split("==")[1].strip()
    dep_filename = dep + ".py"
    dep_path = site_packages / dep
    if dep_path.is_dir():
        shutil.copytree(dep_path, package_dir / dep, dirs_exist_ok=True)
    elif (site_packages / dep_filename).is_file():
        shutil.copy(site_packages / dep_filename, package_dir / dep_filename)
    else:
        # maybe the package module is called differently from the package, so look in top_level.txt
        top_level = site_packages / (f"{dep}-{dep_version}.dist-info") / "top_level.txt"
        if not top_level.exists():
            raise RuntimeError(
                f"Dependency {dep} folder is not found in {site_packages}, top_level.txt not found in {top_level}"
            )
        modules = [m for m in top_level.read_text().splitlines() if not m.startswith("_")]
        if len(modules) > 1:
            raise RuntimeError(
                f"{dep} has more than one names, please provide manual mapping for correct one: {modules}"
            )
        if len(modules) == 0:
            raise RuntimeError(
                f"{dep} has no public name in {top_level}, please provide manual mapping for correct one: {modules}"
            )
        module_path = site_packages / modules[0]
        if not module_path.exists():
            raise RuntimeError(
                f"{dep} should be at {module_path}, but it not exists"
            )
        shutil.copytree(module_path, package_dir / modules[0], dirs_exist_ok=True)

# TODO: We probably want to create a wheel out of these to have less files in the package
