import pathlib
from typing import Optional
from pyprince.parser.Project import ImportLocation, Project
from pyprince.parser.ImportResolver import ImportResolver

import libcst
from libcst.tool import dump


class CSTImportResolver(libcst.CSTTransformer):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.current_import_name: Optional[str] = None

    def visit_Import(self, node: libcst.Import):
        print(f"myvisit: {[nm.evaluated_name for nm in node.names]}")
        self.current_import_name = ""

    def leave_Import(self, node: libcst.Import, updated_node: libcst.CSTNode):
        self.current_import_name = None
        return node

    def visit_ImportAlias(self, node: libcst.ImportAlias):
        alias = node.evaluated_alias
        if alias is None:
            alias = node.evaluated_name
        print(f"alias: {alias}")
        self.project.add_import(alias, ImportLocation(self.current_import_name, node.evaluated_name))

    def visit_ImportFrom(self, node: libcst.ImportFrom):
        if node.module is None:
            self.current_import_name = "."
        else:
            self.current_import_name = node.module.value
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
    return result
