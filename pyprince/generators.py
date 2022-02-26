from types import ModuleType
import inspect
from collections import defaultdict

import libcst
from libcst._nodes.internal import CodegenState

from pyprince.parser.Project import Project


class DependencyDescriptor:
    def __init__(self) -> None:
        self.nodes: list[str] = []
        self.edges: dict[str, list[str]] = defaultdict(list)

    def add_node(self, node: str):
        self.nodes.append(node)

    def add_edge(self, root: str, sub: str):
        self.edges[root].append(sub)

    def to_dict(self):
        return {"nodes": self.nodes, "edges": dict(self.edges)}


def render_node(node: libcst.CSTNode):
    state = CodegenState(" " * 4, "\n")
    node._codegen(state)
    return "".join(state.tokens)


def generate_code(proj: Project) -> str:
    root_cst = proj.get_syntax_tree(proj.modules.__name__)
    return root_cst.code


def describe_module_dependencies(proj: Project) -> DependencyDescriptor:
    """
    Generates a json which describes all the dependencies between modules.
    The json contains node names, and edges between nodes.
    The node names are unique.
    """

    result = DependencyDescriptor()
    if not proj.modules:
        return result

    def _recursively_enumerate_submodules(mod: ModuleType, visited: set[ModuleType]):
        if mod not in visited:
            node_id = len(visited)
            visited.add(mod)
            result.add_node(get_module_name(mod))

        subs: list[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.ismodule)
        for name, sub in subs:
            if sub == mod:
                continue
            if sub not in visited:
                _recursively_enumerate_submodules(sub, visited)
            result.add_edge(get_module_name(mod), get_module_name(sub))

    visited = set()
    _recursively_enumerate_submodules(proj.modules, visited)

    return result


def get_module_name(mod: ModuleType) -> str:
    if hasattr(mod, "__spec__") and mod.__spec__ is not None:
        return mod.__spec__.name
    if hasattr(mod, "_spec__") and mod._spec__ is not None:
        return mod._spec__.name
    return mod.__name__
