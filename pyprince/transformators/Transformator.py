from __future__ import annotations
from dataclasses import dataclass

from pyprince.transformators.FunctionExpander import FunctionExpander
from pyprince.parser.Project import Project


@dataclass
class Transformator:
    """Provides methods to alter the code tree of a project"""
    proj: Project

    def expand_function(self, entry_func_name: str) -> Transformator:
        # TODO: Find places where functions are called. Remove function call node
        # Find the called function ast.
        # Replace original call with ast. Substitute func arguments into the ast.
        # In the injected ast, replace every "return" with the assignment, if there was an assignment.
        # if func call is nested inside another func call, or an other expression,
        # move result to a variable.
        name, module_entry = self.proj.find_module_for_function(entry_func_name)
        if not module_entry or not name:
            return self
        injector = FunctionExpander(self.proj)
        expanded = module_entry.visit(injector)

        new_proj = self.proj.clone()
        new_proj.add_syntax_tree(name, expanded)
        return Transformator(new_proj)
