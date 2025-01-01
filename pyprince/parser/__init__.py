from pathlib import Path

from pyprince.parser.Project import Project, Module, ModuleIdentifier
from pyprince.parser.project_importer import get_module_name, parse_project_by_imports
from pyprince.parser.project_parser import parse_project_new


def parse_project(entry_file: Path, shallow_stdlib: bool) -> Project:
    """
    Parses in all the module files starting from an entry_file.
    When 'shallow_stdlib' param is true, we wont include the whole stdlib, 
    just the surface modules that other modules include.
    """
    return parse_project_new(entry_file, shallow_stdlib)
    # return parse_project_by_imports(entry_file)
