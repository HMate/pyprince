from pathlib import Path


def get_test_scenarios_dir() -> Path:
    return Path(__file__).parent.parent / "test_scenarios"


from .PackageGenerator import PackageGenerator