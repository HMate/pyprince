from types import ModuleType
import inspect
from collections import defaultdict

import libcst
from libcst._nodes.internal import CodegenState

from pyprince.parser import get_module_name
from pyprince.parser.Project import Project, Module


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
    root_cst = proj.get_syntax_tree(proj.root_modules[0].name)
    return root_cst.code if root_cst else ""


def describe_module_dependencies(proj: Project) -> DependencyDescriptor:
    """
    Generates a json which describes all the dependencies between modules.
    The json contains node names, and edges between nodes.
    The node names are unique.
    """
    return _describe_deps(proj)
    # return _describe_deps_from_imports(proj)


def _describe_deps(proj: Project) -> DependencyDescriptor:
    result = DependencyDescriptor()

    def _recursively_enumerate_submodules(mod: Module, visited: set[str]):
        if mod.name not in visited:
            visited.add(mod.name)
            result.add_node(mod.name)

        for sub in mod.submodules:
            if sub == mod:
                continue
            if sub.name not in visited:
                _recursively_enumerate_submodules(sub, visited)
            result.add_edge(mod.name, sub.name)

    visited = set()
    for root in proj.root_modules:
        _recursively_enumerate_submodules(root, visited)

    return result


def _describe_deps_from_imports(proj: Project) -> DependencyDescriptor:
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
