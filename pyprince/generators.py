from dataclasses import dataclass, field
import dataclasses
from collections import defaultdict
from typing import List, Set

from pyprince.parser import Project, Module, Package, PackageType


@dataclass
class PackageDescriptor:
    type: str = PackageType.Unknown.name
    modules: Set[str] = field(default_factory=set)


class DependencyDescriptor:
    def __init__(self) -> None:
        self.nodes: List[str] = []
        self.edges: dict[str, List[str]] = defaultdict(list)
        self.packages: dict[str, PackageDescriptor] = defaultdict(PackageDescriptor)

    def add_node(self, node: str):
        self.nodes.append(node)

    def add_edge(self, root: str, sub: str):
        self.edges[root].append(sub)

    def add_package(self, package: Package):
        self.packages[package.name] = PackageDescriptor(package.package_type.name, package.modules)

    def to_dict(self):
        result = {"nodes": self.nodes, "edges": dict(self.edges)}
        if len(self.packages) > 0:
            result["packages"] = {k: dataclasses.asdict(v) for k, v in self.packages.items()}
        return result


def generate_code(proj: Project) -> str:
    root_cst = proj.get_syntax_tree(proj.get_root_modules()[0])
    return root_cst.code if root_cst else ""


def describe_module_dependencies(proj: Project) -> DependencyDescriptor:
    """
    Generates a struct which describes all the dependencies between modules.

    The DependencyDescriptor struct contains node names, and edges between nodes.
    The nodes can be package names and module names (a package is roughly a folder full of modules).

    The node names are unique.
    """
    return _describe_deps(proj)


def _describe_deps(proj: Project) -> DependencyDescriptor:
    result = DependencyDescriptor()

    for module_name in proj.get_modules():
        result.add_node(module_name)
        mod = proj.get_module(module_name)
        if mod is None:
            continue
        for sub in mod.submodules:
            result.add_edge(mod.name, sub.name)

    for package_name in proj.list_packages():
        package = proj.get_package(package_name)
        if package is None:
            continue
        result.add_package(package)

    return result
