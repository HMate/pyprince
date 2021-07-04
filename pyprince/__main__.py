import pathlib
from pyprince import generators
import typer

from pyprince import parser


def main(entrypoint: pathlib.Path, draw_modules: bool = typer.Option(False, "--dm")):
    typer.echo(f"Start is: {entrypoint.name}")
    mod = parser.parse_project(entrypoint)
    if draw_modules:
        generators.draw_modules(mod)
    else:
        print(generators.generate_code(mod))


if __name__ == "__main__":
    typer.run(main)