import libcst
from libcst._nodes.internal import CodegenState

from pyprince.parser.Project import Project


def render_node(node: libcst.CSTNode):
    state = CodegenState(" " * 4, "\n")
    node._codegen(state)
    return "".join(state.tokens)


def generate_code(proj: Project) -> str:
    root_cst = proj.get_syntax_tree(proj.modules.__name__)
    return root_cst.code
