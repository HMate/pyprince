import libcst
from libcst._nodes.expression import BaseExpression


class VariableReplacer(libcst.CSTTransformer):
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
        return updated_node
