from enum import Enum
import pathlib

import typer

from pyprince import parser, generators, serializer, logger


class OutputFormat(str, Enum):
    json = "json"
    dot = "dot"


def console_entry_main():
    typer.run(main)


def main(
    entrypoint: pathlib.Path,
    draw_modules: bool = typer.Option(False, "--dm"),
    output_format: OutputFormat = typer.Option(OutputFormat.json, "-f"),
):
    logger.init()
    logger.logger.info(f"Starting pyprince at {pathlib.Path().absolute()}")

    if not check_entrypoint(entrypoint):
        typer.echo("Entrypoint check failed, exiting.")
        return

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


def check_entrypoint(entrypoint: pathlib.Path):
    if not entrypoint.exists():
        typer.echo(f"Entrypoint does not exists: {entrypoint}")
        return False
    return True
