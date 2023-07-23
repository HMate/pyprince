from pathlib import Path

from pyprince.parser.Project import Project, Module
from pyprince.parser.project_importer import get_module_name, parse_project_by_imports
from pyprince.parser.project_parser import parse_project_new


def parse_project(entry_file: Path) -> Project:
    return parse_project_new(entry_file)
    # return parse_project_by_imports(entry_file)
