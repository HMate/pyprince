from types import ModuleType
import libcst
from libcst._nodes.internal import CodegenState

import inspect
from pyvis.network import Network


from pyprince.parser.Project import Project


def render_node(node: libcst.CSTNode):
    state = CodegenState(" " * 4, "\n")
    node._codegen(state)
    return "".join(state.tokens)


def generate_code(proj: Project) -> str:
    root_cst = proj.get_syntax_tree(proj.modules.__name__)
    return root_cst.code


def draw_modules(proj: Project):
    net = Network(width="1280px", height="920px", directed=True, layout=True)

    def _recursively_enumerate_submodules(mod: ModuleType, visited: dict[ModuleType, int]):
        if mod not in visited:
            node_id = len(visited)
            visited[mod] = node_id
            net.add_node(node_id, label=mod.__name__, shape="box")
        node_id = visited[mod]

        subs: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.ismodule)
        for name, sub in subs:
            if sub == mod:
                continue
            if sub not in visited:
                _recursively_enumerate_submodules(sub, visited)
            sub_id = visited[sub]
            net.add_edge(node_id, sub_id)

    if not proj.modules:
        return
    visited = {}
    _recursively_enumerate_submodules(proj.modules, visited)

    target_html = "network.html"
    net.show_buttons(filter_=["layout", "physics"])
    net.options.layout.hierarchical
    net.show(target_html)
    print(f"Graph generated in {target_html}")
