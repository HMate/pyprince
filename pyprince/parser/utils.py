import libcst
from libcst._nodes.internal import CodegenState


def render_node(node: libcst.CSTNode):
    state = CodegenState("  ", "\n")
    node._codegen(state)
    return "".join(state.tokens)
