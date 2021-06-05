import sys
import pathlib
from typing import Optional, Sequence
import importlib, importlib.util

from pyprince.parser.Project import ImportLocation, Project
from pyprince.parser.ImportResolver import ImportResolver

import libcst
from libcst.tool import dump


class CSTImportResolver(libcst.CSTTransformer):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.current_import_name: str = ""

    def visit_Import(self, node: libcst.Import):
        """The whole of: import mod"""
        print(f"myvisit: {[nm.evaluated_name for nm in node.names]}")
        for name in node.names:
            alias = name.evaluated_alias
            if alias is None:
                alias = name.evaluated_name
            self.project.add_import(alias, ImportLocation("", name.evaluated_name))
        self.current_import_name = ""

    def leave_Import(self, node: libcst.Import, updated_node: libcst.CSTNode):
        self.current_import_name = ""
        return node

    # def visit_ImportAlias(self, node: libcst.ImportAlias):
    #     """the alias part in: 
    #     import alias
    #     from util import alias
    #     """
    #     alias = node.evaluated_alias
    #     if alias is None:
    #         alias = node.evaluated_name
    #     print(f"alias: {alias}")
    #     self.project.add_import(alias, ImportLocation(self.current_import_name, node.evaluated_name))

    def visit_ImportFrom(self, node: libcst.ImportFrom):
        """The whole of: from pack import mod"""
        package = ""
        # None==node.module means we are importing relatively from own package
        # ie. from . import mod
        if node.module is not None:
            package = f"{node.module.value}."
        if isinstance(node.names, Sequence):
            for name in node.names:
                alias = name.evaluated_alias
                if alias is None:
                    alias = name.evaluated_name
                self.project.add_import(alias, ImportLocation("", f"{package}{name.evaluated_name}"))
        print(f"import from: {self.current_import_name}")

    def leave_ImportFrom(self, node: libcst.ImportFrom, updated_node: libcst.CSTNode):
        self.current_import_name = None
        return node


def parse_file(entry_file: pathlib.Path) -> Project:
    content = entry_file.read_text()
    result = Project()
    resolver = CSTImportResolver(result)
    cst: libcst.Module = libcst.parse_module(content)
    cst.visit(resolver)

    # TODO: Figure out how to find module path for every scenario
    # TODO: sys is builtin - what now?
    sys.path = [str(entry_file.parent)] + sys.path
    try:
        for alias, location in result.imports.items():
            # TODO: Handle: import ..module
            if location.name.startswith(".") and location.parent_name == "":
                location.name = location.name[1:]
            # TODO: We have to manually DFS import modules, and check manually the paths? 
            # Because find_spec calls __import__, which runs real code, and also it seems to need parent packages to be loaded
            spec = importlib.util.find_spec(location.name, location.parent_name)
            if spec:
                print(f"spec {location.name}:{location.parent_name}: {spec.name} - {spec.origin}")
            else:
                print(f"spec {location.name}:{location.parent_name}: None:(")
    finally:
        sys.path = sys.path[1:]

    return result

def parse_file2(entry_file: pathlib.Path):
    # TODO: We will need a mix between this and parse_file, 
    # we need to find all modules, 
    # and for now we can piggyback onimportlib.import_module, 
    # but int the future this will be unsafe because of unsfafe code in modules. 
    # After module paths and objects are known, we parse their ASTs, and then we 
    # can start to patch in objects from imported modules
    content = entry_file.read_text()
    module_name = entry_file.stem


    sys.path = [str(entry_file.parent)] + sys.path
    try:
        mod = importlib.import_module(module_name)
        return mod
    except Exception as e:
        print(f"Got: {e}")
    finally:
        sys.path = sys.path[1:]
    return None

