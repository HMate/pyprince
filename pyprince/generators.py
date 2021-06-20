from pyprince.parser.Project import Project
import pyprince.parser.utils as ut
from pyprince.transformators.FunctionExpander import FunctionExpander
import libcst
from libcst._nodes.internal import CodegenState


def render_node(node: libcst.CSTNode):
    state = CodegenState(" " * 4, "\n")
    node._codegen(state)
    return "".join(state.tokens)


def generate_code(proj: Project) -> str:
    # TODO: Extract this method to its own CodeGenerator class
    root_cst = proj.get_syntax_tree(proj.modules.__name__)
    return root_cst.code


def generate_code_one_level_expanded(proj: Project, entry_func_name: str) -> str:
    # TODO: Extract this method to its own CodeGenerator class
    entry = proj.get_function(entry_func_name)
    if not entry:
        return ""

    # TODO: Find places where functions are called. Remove function call node
    # Find the called function ast.
    # Replace original call with ast. Substitute func arguments into the ast.
    # In the injected ast, replace every "return" with the assignment, if there was an assignment.
    # if func call is nested inside another func call, or an other expression,
    # move result to a variable.
    injector = FunctionExpander(proj)
    expanded = entry.visit(injector)

    return render_node(expanded)
