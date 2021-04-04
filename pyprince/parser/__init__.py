import pathlib

import libcst
from libcst.tool import dump

def parse_file(entry_file: pathlib.Path):
    content = entry_file.read_text()
    cst = libcst.parse_module(content)
    return dump(cst)