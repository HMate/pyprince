from enum import Enum
import pathlib
from typing import Optional
import sys

import typer

from pyprince import parser, generators
from pyprince.utils import logging, logger, serializer


class OutputFormat(str, Enum):
    json = "json"
    dot = "dot"


app = typer.Typer()


def console_entry_main():
    app()


@app.command()
def parse(
    entrypoint: pathlib.Path,
    describe_modules: bool = typer.Option(False, "--dm"),
    output_file: Optional[pathlib.Path] = typer.Option(None, "-o"),
    cache_file: Optional[pathlib.Path] = typer.Option(None, "--cache"),
    output_format: OutputFormat = typer.Option(OutputFormat.json, "-f"),
    shallow_stdlib: bool = typer.Option(False, "--shallow-std"),
):
    logging.init()
    logger.info(f"****** Starting pyprince at {pathlib.Path().absolute()} ******")
    logger.info(f"Program called with args: {sys.argv}")

    if not check_entrypoint(entrypoint):
        typer.echo("Entrypoint check failed, exiting.")
        return

    project_cache = load_cache(cache_file)
    project = parser.parse_project(entrypoint, project_cache=project_cache, shallow_stdlib=shallow_stdlib)
    save_cache(cache_file, project)

    if describe_modules:
        desc = generators.describe_module_dependencies(project)
        if output_format == OutputFormat.json:
            result = serializer.to_json(desc)
        else:
            result = serializer.to_graphviz_dot(desc)

        if output_file is not None:
            if not output_file.exists():
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.touch()
            output_file.write_text(result)
        else:
            typer.echo(result)
    else:
        typer.echo(generators.generate_code(project))
    logger.success(f"pyprince finished")


@app.command()
def version():
    typer.echo(f"pyprince version: 0.0.5")


def load_cache(cache_file: Optional[pathlib.Path]) -> Optional[parser.ProjectCache]:
    try:
        project_cache = None
        if cache_file is not None:
            logger.info(f"Using cache. Cache path: {cache_file}")
            project_cache = parser.ProjectCache()
            if cache_file.exists():
                logger.info(f"Loading cache from {cache_file}")
                with cache_file.open("r") as cache_stream:
                    project_cache.load_stream(cache_stream)
        else:
            logger.info(f"Project cache disabled")
        return project_cache
    except Exception:
        logger.opt(exception=True).warning(f"Failed to load cache file at: {cache_file}")
        raise


def save_cache(cache_file: Optional[pathlib.Path], project: parser.Project):
    if cache_file is not None:
        try:
            if not cache_file.exists():
                logger.info(f"Creating folders for cache {cache_file}")
                cache_file.parent.mkdir(parents=True, exist_ok=True)
            with cache_file.open("w") as cache_stream:
                logger.info(f"Writing cache {cache_file}")
                parser.ProjectCache().serialize(cache_stream, project)
        except IOError:
            logger.opt(exception=True).warning(f"Failed to create cache file at: {cache_file}")


def check_entrypoint(entrypoint: pathlib.Path):
    if not entrypoint.exists():
        typer.echo(f"Entrypoint does not exists: {entrypoint}")
        return False
    return True
