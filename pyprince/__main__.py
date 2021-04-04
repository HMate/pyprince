import pathlib
import typer

from pyprince import parser


def main(entrypoint: pathlib.Path):
    typer.echo(f"Start is: {entrypoint.name}")
    cst = parser.parse_file(entrypoint)
    typer.echo(cst)

if __name__ == "__main__":
    typer.run(main)