from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Iterable, Optional
import inspect

import libcst
from libcst._nodes.expression import BaseExpression

import pyprince.parser.utils as ut


@dataclass
class ImportLocation:
    # the fully qualified import name of the parent package
    parent_name: str
    # name of the module/function/class to import
    name: str


class CSTVariableReplacer(libcst.CSTTransformer):
    """Search for variable occurences in CST"""

    def __init__(self, variable_name: str, inserted_value: BaseExpression) -> None:
        super().__init__()
        self.variable_name = variable_name
        self.inserted_value = inserted_value
        self.call_paths: list[list[libcst.CSTNode]] = []
        self.current_node_path: list[libcst.CSTNode] = []

    def leave_Name(self, node: libcst.Name, updated_node: libcst.Name):
        if node.value == self.variable_name:
            return self.inserted_value.deep_clone()
        return node


class CSTNodeReplacer(libcst.CSTTransformer):
    """Replace occurences of one node with another recursively. Uses deep_equals, not '=='"""

    def __init__(self, obsolete_node: libcst.CSTNode, requested_node: libcst.CSTNode) -> None:
        super().__init__()
        self.obsolete_node = obsolete_node
        self.requested_node = requested_node

    def on_leave(self, original_node: libcst.CSTNode, updated_node: libcst.CSTNode):
        if original_node.deep_equals(self.obsolete_node):
            return self.requested_node
        return updated_node


class CSTFunctionInjector(libcst.CSTTransformer):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.line_can_be_replaced = False
        self.call_paths: list[list[libcst.CSTNode]] = []
        self.current_node_path: list[libcst.CSTNode] = []

    def on_visit(self, node: libcst.CSTNode) -> bool:
        self.current_node_path.append(node)
        # print(f"{[type(p).__name__ for p in self.current_node_path]}")
        return super().on_visit(node)

    def on_leave(self, original_node: libcst.CSTNode, updated_node: libcst.CSTNode):
        self.current_node_path.pop()
        res: libcst.CSTNode = super().on_leave(original_node, updated_node)  # type: ignore
        if len(self.current_node_path) != 0:
            return res

        return self._inject_functions(res)

    def visit_Call(self, node: libcst.Call):
        func_name = self._get_call_node_name(node)
        if not func_name:
            return True
        has_func = self.project.has_function(func_name)
        if has_func:
            self.call_paths.append(self.current_node_path.copy())
        return True

    def _inject_functions(self, root: libcst.CSTNode):
        # print(f"Injecting these:")
        result = root
        for path in self.call_paths:
            call_node: libcst.Call = path[-1]  # type: ignore
            func_name = self._get_call_node_name(call_node)
            if not func_name:
                print(f"WARNING: Got call without name: {call_node}")
                continue

            func_def: Optional[libcst.FunctionDef] = self.project.get_function(func_name)
            if not func_def:
                continue

            enclosing_node = path[-2]
            if isinstance(enclosing_node, libcst.Assign):
                if len(func_def.body.body) == 1:
                    expr = func_def.body.body[0].body[0]
                    if (isinstance(expr, libcst.Return)) and expr.value is not None:
                        # function is a single SimpleStatementLine, and it is a return
                        params = func_def.params.params
                        returned_value = expr.value.deep_clone()
                        returned_value = self._substitute_args_into_expression(returned_value, params, call_node.args)

                        changed_line = enclosing_node.with_changes(value=returned_value)
                        replacer = CSTNodeReplacer(enclosing_node, changed_line)
                        result = result.visit(replacer)
            elif isinstance(enclosing_node, libcst.Expr):
                if len(func_def.body.body) == 1:
                    expr = func_def.body.body[0].body[0]
                    if (isinstance(expr, libcst.Expr)) and expr.value is not None:
                        # function is a single SimpleStatementLine, but not a return
                        params = func_def.params.params
                        code_line = expr.value.deep_clone()
                        returned_value = self._substitute_args_into_expression(code_line, params, call_node.args)

                        changed_line = enclosing_node.with_changes(value=returned_value)
                        replacer = CSTNodeReplacer(enclosing_node, changed_line)
                        result = result.visit(replacer)
        return result

    def _substitute_args_into_expression(self, expr, params, args):
        for i, param in enumerate(params):
            param_name = param.name.value
            # search any variable use in returned value, that uses this param
            # get matching args from call, and substitute them in into the returned val
            arg = args[i].value
            locator = CSTVariableReplacer(param_name, arg)
            changed = expr.visit(locator)
            if isinstance(changed, libcst.BaseExpression):
                expr = changed
        return expr

    def _get_call_node_name(self, node: libcst.Call):
        """Get the name of the function that is invoked in libcst.Call node"""
        if isinstance(node.func, libcst.Name):
            return node.func.value
        else:
            print(f"WARNING Cannot find function name: in {type(node.func)} - {ut.render_node(node)}")
            return None


@dataclass
class Project:
    # The mapping of aliases to importLocations
    modules: Optional[ModuleType]
    syntax_trees: dict[str, tuple[ModuleType, libcst.Module]] = field(default_factory=dict)
    imports: dict[str, ImportLocation] = field(default_factory=dict)

    def add_import(self, name: str, node: ImportLocation):
        self.imports[name] = node

    def add_syntax_tree(self, module: ModuleType, st: libcst.Module):
        self.syntax_trees[module.__name__] = (module, st)

    def get_syntax_tree(self, module_name: str):
        if module_name not in self.syntax_trees:
            return None
        return self.syntax_trees[module_name][1]

    def iter_modules(self) -> Iterable[ModuleType]:
        if not self.modules:
            return
        visited = []
        yield from self._recursively_enumerate_submodules(self.modules, visited)

    def _recursively_enumerate_submodules(self, mod: ModuleType, visited: list[ModuleType]) -> Iterable[ModuleType]:
        visited.append(mod)
        yield mod
        subs: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.ismodule)
        for name, sub in subs:
            if sub not in visited:
                yield from self._recursively_enumerate_submodules(sub, visited)

    def generate_code(self):
        # TODO: Extract this method to its own CodeGenerator class
        root_cst = self.get_syntax_tree(self.modules.__name__)
        return root_cst.code

    def generate_code_one_level_expanded(self, entry_func_name):
        # TODO: Extract this method to its own CodeGenerator class
        entry = self.get_function(entry_func_name)
        if not entry:
            return ""

        # TODO: Find places where functions are called. Remove function call node
        # Find the called function ast.
        # Replace original call with ast. Substitute func arguments into the ast.
        # In the injected ast, replace every "return" with the assignment, if there was an assignment.
        # if func call is nested inside another func call, or an other expression,
        # move result to a variable.
        injector = CSTFunctionInjector(self)
        expanded = entry.visit(injector)

        return ut.render_node(expanded)

    def has_function(self, func_name: str) -> bool:
        return self.get_function(func_name) is not None

    def get_function(self, func_name: str):
        module_name = self._find_module_for_function(func_name)
        if not module_name:
            return None
        root_cst = self.get_syntax_tree(module_name)
        for node in root_cst.children:
            if isinstance(node, libcst.FunctionDef) and node.name.value == func_name:
                return node
        else:
            return None

    def _find_module_for_function(self, func_name: str) -> Optional[str]:
        functions: list[tuple[str, function]] = inspect.getmembers(self.modules, inspect.isfunction)
        for name, func in functions:
            if name == func_name:
                return func.__module__
        return None

    # TODO: Split to classes:
    # - CodeGenerator - generate code for project/module/function
    # - CodeTransformer - Expands function calls, substitute variables, adds/removes new code nodes
    #     Xpand single function call
    #     Xpand all functions calls one level in single function
    #     Xpand all functions calls until possible in a single function
    #     Xpand all functions calls until possible in whole module (remove unused functions?)
    # - Project/Module/Function - Own AST wrappers? So searching, modifiying is easier
    #     These should also store the structure of the original source, provide mapping between the two

    # TODO: def code generators:
    # - full expand a function
    # - expand one level

    # TODO: AST alteration
    # - optimize variable usages, remove duplicated usages (asd = 7; rar = asd; => rar = 7)
    # - create variable-function dependency graph
    # - group together code with matching dependencies
