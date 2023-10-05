import json
from pathlib import Path
import shutil

import click


def make_main_py(path: Path) -> None:
    py_script_text = """import rdetoolkit

rdetoolkit.run()
"""
    with open(path, mode='w', encoding="utf-8") as f:
        f.write(py_script_text)


def make_requirements_txt(path: Path) -> None:
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
    with open(path, mode='w', encoding="utf-8") as f:
        f.write(package_text)


def make_template_json(path: Path) -> None:
    with open(path, mode='w', encoding="utf-8") as f:
        json.dump({}, f, indent=4)

def make__json(path: Path) -> None:
    with open(path, mode='w', encoding="utf-8") as f:
        json.dump({}, f, indent=4)


@click.group()
def cli():
    pass


@click.command()
def init() -> None:
    """Initialize the project."""
    directorys = [
        Path('container/modules'),
        Path('container/data/inputdata'),
        Path('container/data/invoice'),
        Path('container/data/tasksupport')
    ]
    try:
        for dir in directorys:
            dir.mkdir(parents=True, exist_ok=True)

        if not Path('container/main.py').exists():
            make_main_py(Path('container/main.py'))

        if not Path('container/requirements.txt').exists():
            make_requirements_txt(Path('container/requirements.txt'))

        if not Path('container/data/invoice/invoice.json').exists():
            make_template_json(Path('container/data/invoice/invoice.json'))

        if not Path('container/data/tasksupport/invoice.schema.json').exists():
            make_template_json(Path('container/data/tasksupport/invoice.schema.json'))

        if not Path('container/data/tasksupport/meatadata-def.json').exists():
            make_template_json(Path('container/data/tasksupport/metadata-def.json'))

        click.echo(click.style("Ready to develop a structured program for RDE.", fg="green"))
        click.echo("\nCheck the folder you created: container\n")
        click.echo("Done!")
    except Exception:
        click.echo(click.style("Failed to create files required for structured RDE programs.", fg="red"), err=True)
        for dir in directorys:
            if dir.exists():
                shutil.rmtree(dir)


cli.add_command(init)

if __name__ == '__main__':
    cli()
