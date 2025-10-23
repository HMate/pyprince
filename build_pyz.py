"""
Build a pyz package for pyprince into the /build folder using shiv and pip.
This script should be started from the venv that contains the dev deps of pyprince.
"""

import subprocess
import venv
import os
import sys
from pathlib import Path

print("Building pyprince pyz package")
print(f"Python path: {sys.exec_prefix}")
print(f"Current path: {Path('.').resolve()}")


def run(command, **kwargs):
    print(f"Running: {command}")
    return subprocess.run(command.split(), check=True, **kwargs)


if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    res = run(
        "poetry export -f requirements.txt --without-hashes -o build/requirements.txt", capture_output=True, shell=True
    )

    # Create venv for building
    print("Create build/build_venv")
    builder = venv.EnvBuilder(clear=True, with_pip=True)
    builder.create("build/build_venv")

    print("Install deps into venv")
    pip = "build/build_venv/Scripts/pip"
    run(f"{pip} install --no-cache-dir -r build/requirements.txt")
    run(f"{pip} install .")

    print("Build pyz file")
    run(
        "python -m shiv -c pyprince -o build/pyprince.pyz --compressed --site-packages ./build/build_venv/Lib/site-packages",
        shell=True,
    )
