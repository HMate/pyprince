from pyprince.transformators.VariableReplacer import VariableReplacer
from pyprince.transformators.NodeReplacer import NodeReplacer
from typing import Optional, Union
import libcst

from pyprince import parser
import pyprince.generators as gen


class FunctionExpander(libcst.CSTTransformer):
    def __init__(self, project: parser.Project) -> None:
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
        # TODO: if func call is nested inside another func call, or an other expression,
        # move result to a variable.
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
                        result = self._substitute_single_line_function_call(
                            func_def, expr, call_node, enclosing_node, result
                        )
            elif isinstance(enclosing_node, libcst.Expr):
                if len(func_def.body.body) == 1:
                    expr = func_def.body.body[0].body[0]
                    if (isinstance(expr, libcst.Expr)) and expr.value is not None:
                        # function is a single SimpleStatementLine, but not a return
                        result = self._substitute_single_line_function_call(
                            func_def, expr, call_node, enclosing_node, result
                        )
        return result

    def _substitute_single_line_function_call(
        self,
        func_def: libcst.FunctionDef,
        func_line: Union[libcst.Expr, libcst.Return],
        caller_node: libcst.Call,
        caller_line_node: libcst.BaseSmallStatement,
        tree_root: libcst.CSTNode,
    ) -> libcst.CSTNode:
        params = func_def.params.params
        code_line = func_line.value.deep_clone()
        code_line = self._substitute_args_into_expression(code_line, params, caller_node.args)

        changed_line = caller_line_node.with_changes(value=code_line)
        replacer = NodeReplacer(caller_line_node, changed_line)
        return tree_root.visit(replacer)  # type: ignore

    def _substitute_args_into_expression(self, expr, params, args):
        for i, param in enumerate(params):
            param_name = param.name.value
            # search any variable use in returned value, that uses this param
            # get matching args from call, and substitute them in into the returned val
            arg = args[i].value
            locator = VariableReplacer(param_name, arg)
            changed = expr.visit(locator)
            if isinstance(changed, libcst.BaseExpression):
                expr = changed
        return expr

    def _get_call_node_name(self, node: libcst.Call):
        """Get the name of the function that is invoked in libcst.Call node"""
        if isinstance(node.func, libcst.Name):
            return node.func.value
        else:
            print(f"WARNING Cannot find function name: in {type(node.func)} - {gen.render_node(node)}")
            return None
