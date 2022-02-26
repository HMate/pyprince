import orjson
from pyprince.generators import DependencyDescriptor


def to_json(descriptor: DependencyDescriptor) -> str:
    return orjson.dumps(descriptor.to_dict(), option=orjson.OPT_INDENT_2).decode("utf-8")


def to_graphviz_dot(descriptor: DependencyDescriptor) -> str:
    file_builder: list[str] = []
    file_builder.append("digraph G {")
    for parent, targets in descriptor.edges.items():
        for target in targets:
            file_builder.append(f'    "{parent}" -> "{target}"')
    file_builder.append("}")
    return "\n".join(file_builder)
