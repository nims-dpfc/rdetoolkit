import pathlib
from typing import Literal

import click

from rdetoolkit.cmd.command import InitCommand, VersionCommand
from rdetoolkit.cmd.gen_excelinvoice import GenerateExcelInvoiceCommand


@click.group()
def cli() -> None:
    """CLI generates template projects for RDE structured programs."""


@click.command()
def init() -> None:
    """Output files needed to build RDE structured programs."""
    cmd = InitCommand()
    cmd.invoke()


@click.command()
def version() -> None:
    """Command to display version."""
    cmd = VersionCommand()
    cmd.invoke()


@click.command()
@click.argument("invoice_schema_json_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=pathlib.Path), metavar="<invoice.shcema.json file path>")
@click.option("-o", "--output", "output_path", type=click.Path(exists=False, dir_okay=False, resolve_path=True, path_type=pathlib.Path), required=True, metavar="<path to ExcelInvoice file output>")
@click.option("-m", "--mode", type=click.Choice(["file", "folder"], case_sensitive=False), default="file", metavar="<filemode or foldermode>")
def make_excelinvoice(invoice_schema_json_path: pathlib.Path, output_path: pathlib.Path, mode: Literal["file", "folder"]) -> None:
    """Generate an Excel invoice based on the provided schema and save it to the specified output path.

    Args:
        invoice_schema_json_path (pathlib.Path): The path to the JSON file containing the invoice schema.
        output_path (pathlib.Path): The path where the generated Excel invoice will be saved.
        mode (Literal["file", "folder"]): The mode indicating whether the output is a single file or a folder.

    Returns:
        None
    """
    cmd = GenerateExcelInvoiceCommand(invoice_schema_json_path, output_path, mode)
    cmd.invoke()


cli.add_command(init)
cli.add_command(version)
cli.add_command(make_excelinvoice)
