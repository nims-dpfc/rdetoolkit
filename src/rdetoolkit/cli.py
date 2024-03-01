import json
import shutil
from pathlib import Path

import click

from . import __version__


def make_main_py(path: Path) -> None:
    """Function to create the main.py template.

    Args:
        path (Path): Destination file path
    """
    py_script_text = """import rdetoolkit

rdetoolkit.workflows.run()
"""
    if Path(path).exists():
        return None

    with open(path, mode="w", encoding="utf-8") as f:
        f.write(py_script_text)


def make_requirements_txt(path: Path) -> None:
    """Function to create the requirements.txt template.

    Args:
        path (Path): Destination file path
    """
    package_text = """# ----------------------------------------------------
# Please add the desired packages and install the libraries after that.
# Then, run
#
# pip install -r requirements.txt
#
# on the terminal to install the required packages.
# ----------------------------------------------------
# ex.
# pandas==2.0.3
# numpy
"""
    if Path(path).exists():
        return None

    with open(path, mode="w", encoding="utf-8") as f:
        f.write(package_text)


def make_template_json(path: Path) -> None:
    """Function to create the json file template.

    Args:
        path (Path): Destination file path
    """
    if Path(path).exists():
        return None

    with open(path, mode="w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)


@click.group()
def cli():
    """Defines the root command for a CLI group.

    This function uses the Click decorator to create a command group for a CLI application.
    Various subcommands can be added to this group. It does nothing on its own when executed,
    but serves as a foundation for organizing subcommands and their functionalities.
    """
    pass


@click.command()
def init() -> None:
    """Initialize the project."""
    directorys = [Path("container/modules"), Path("container/data/inputdata"), Path("container/data/invoice"), Path("container/data/tasksupport")]

    for dir in directorys:
        dir.mkdir(parents=True, exist_ok=True)

    try:
        make_main_py(Path("container/main.py"))
        make_requirements_txt(Path("container/requirements.txt"))
        make_template_json(Path("container/data/invoice/invoice.json"))
        make_template_json(Path("container/data/tasksupport/invoice.schema.json"))
        make_template_json(Path("container/data/tasksupport/metadata-def.json"))

        click.echo(click.style("Ready to develop a structured program for RDE.", fg="green"))
        click.echo("\nCheck the folder you created: container\n")
        click.echo("Done!")
    except Exception:
        click.echo(click.style("Failed to create files required for structured RDE programs.", fg="red"), err=True)
        for dir in directorys:
            if dir.exists():
                shutil.rmtree(dir)


@click.command()
def version():
    """Command to display version."""
    click.echo(__version__)


cli.add_command(init)
cli.add_command(version)
