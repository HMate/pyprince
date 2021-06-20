import libcst


class NodeReplacer(libcst.CSTTransformer):
    """Replace occurences of one node with another recursively. Uses deep_equals, not '=='"""

    def __init__(self, obsolete_node: libcst.CSTNode, requested_node: libcst.CSTNode):
        super().__init__()
        self.obsolete_node = obsolete_node
        self.requested_node = requested_node

    def on_leave(self, original_node: libcst.CSTNode, updated_node: libcst.CSTNode):
        if original_node.deep_equals(self.obsolete_node):
            return self.requested_node
        return updated_node
