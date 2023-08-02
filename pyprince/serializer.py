import json
import traceback
from typing import List

from pyprince.generators import DependencyDescriptor


def to_json(descriptor: DependencyDescriptor) -> str:
    return json.dumps(descriptor.to_dict(), indent=2)


def exception_to_json() -> str:
    return json.dumps({"result": "error", "details": traceback.format_exc()}, indent=2)


def to_graphviz_dot(descriptor: DependencyDescriptor) -> str:
    file_builder: List[str] = []
    file_builder.append("digraph G {")
    for parent, targets in descriptor.edges.items():
        for target in targets:
            file_builder.append(f'    "{parent}" -> "{target}"')
    file_builder.append("}")
    return "\n".join(file_builder)
