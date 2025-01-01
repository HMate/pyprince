from types import ModuleType
import inspect
from collections import defaultdict
from typing import List

from pyprince.parser import get_module_name
from pyprince.parser import Project, Module


class DependencyDescriptor:
    def __init__(self) -> None:
        self.nodes: List[str] = []
        self.edges: dict[str, List[str]] = defaultdict(list)

    def add_node(self, node: str):
        self.nodes.append(node)

    def add_edge(self, root: str, sub: str):
        self.edges[root].append(sub)

    def to_dict(self):
        return {"nodes": self.nodes, "edges": dict(self.edges)}


def generate_code(proj: Project) -> str:
    root_cst = proj.get_syntax_tree(proj.get_root_modules()[0])
    return root_cst.code if root_cst else ""


def describe_module_dependencies(proj: Project) -> DependencyDescriptor:
    """
    Generates a struct which describes all the dependencies between modules.

    The DependencyDescriptor struct contains node names, and edges between nodes.
    The nodes can be package names and module names (a package is roughly a folder full of modules).

    The node names are unique.
    TODO: Add option to group modules into packages
    """
    return _describe_deps(proj)
    # return _describe_deps_from_imports(proj)


def _describe_deps(proj: Project) -> DependencyDescriptor:
    result = DependencyDescriptor()

    for module_name in proj.get_modules():
        result.add_node(module_name)
        mod = proj.get_module(module_name)
        if mod is None:
            continue
        for sub in mod.submodules:
            result.add_edge(mod.name, sub.name)

    return result


def _describe_deps_from_imports(proj: Project) -> DependencyDescriptor:
    """
    Looks through modules that are loaded in and add them to descriptor.
    """
    result = DependencyDescriptor()
    modules = proj.get_loaded_modules()
    if not modules:
        return result

    def _recursively_enumerate_submodules(mod: ModuleType, visited: set[ModuleType]):
        if mod not in visited:
            node_id = len(visited)
            visited.add(mod)
            result.add_node(get_module_name(mod))

        subs: List[tuple[str, ModuleType]] = inspect.getmembers(mod, inspect.ismodule)
        for name, sub in subs:
            if sub == mod:
                continue
            if sub not in visited:
                _recursively_enumerate_submodules(sub, visited)
            result.add_edge(get_module_name(mod), get_module_name(sub))

    visited = set()
    _recursively_enumerate_submodules(modules, visited)

    return result
