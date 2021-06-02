from pathlib import Path


def get_test_scenarios_dir() -> Path:
    return Path(__file__).parent / "test_scenarios"