import subprocess
import venv
import os

os.makedirs("build", exist_ok=True)
res = subprocess.run(
    "poetry export -f requirements.txt --without-hashes -o build/requirements.txt".split(),
    capture_output=True,
    check=True,
)

# Create venv for building
print("Create build/build_venv")
builder = venv.EnvBuilder(clear=True, with_pip=True)
builder.create("build/build_venv")

print("Install deps into venv")
pip = "build/build_venv/Scripts/pip"
subprocess.run(f"{pip} install --no-cache-dir -r build/requirements.txt".split(), check=True)
subprocess.run(f"{pip} install .".split(), check=True)
print("Build pyz file")
subprocess.run(
    f"python -m shiv -c pyprince -o build/pyprince.pyz --compressed --site-packages ./build/build_venv/Lib/site-packages".split(),
    check=True,
)
