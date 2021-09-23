import pathlib
import typer

from pyprince import parser, generators, serializer


def main(entrypoint: pathlib.Path, draw_modules: bool = typer.Option(False, "--dm")):
    typer.echo(f"Start is: {entrypoint.name}")
    mod = parser.parse_project(entrypoint)
    if draw_modules:
        desc = generators.describe_module_dependencies(mod)
        dj = serializer.to_json(desc)
        print(dj.decode('utf-8'))
    else:
        print(generators.generate_code(mod))


if __name__ == "__main__":
    typer.run(main)