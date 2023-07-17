from os.path import dirname

try:
    from pyprince import parser, generators, serializer
except ModuleNotFoundError:
    # When running from npm-package, we need to add the parent directory to the path
    # So that we can import pyprince and deps from the workspace
    import sys

    sys.path.append(dirname(dirname(__file__)))
    from pyprince import parser, generators, serializer

from enum import Enum
import pathlib
import typer


class OutputFormat(str, Enum):
    json = "json"
    dot = "dot"


def main(
    entrypoint: pathlib.Path,
    draw_modules: bool = typer.Option(False, "--dm"),
    output_format: OutputFormat = typer.Option(OutputFormat.json, "-f"),
):
    mod = parser.parse_project(entrypoint)
    if draw_modules:
        desc = generators.describe_module_dependencies(mod)
        if output_format == OutputFormat.json:
            result = serializer.to_json(desc)
        else:
            result = serializer.to_graphviz_dot(desc)
        typer.echo(result)
    else:
        typer.echo(generators.generate_code(mod))


if __name__ == "__main__":
    typer.run(main)
