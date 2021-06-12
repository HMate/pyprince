import pathlib
import typer

from pyprince import parser


def main(entrypoint: pathlib.Path):
    typer.echo(f"Start is: {entrypoint.name}")
    # typer.echo(cst.code)
    mod = parser.parse_project(entrypoint)
    print(mod)


if __name__ == "__main__":
    typer.run(main)