from __future__ import annotations

import pathlib
from typing import Literal

import click

from rdetoolkit.exceptions import InvoiceSchemaValidationError
from rdetoolkit.invoicefile import ExcelInvoiceFile
from rdetoolkit.rdelogger import get_logger

logger = get_logger(__name__)


class GenerateExcelInvoiceCommand:

    def __init__(self, invoice_schema_file: pathlib.Path, output_path: pathlib.Path, mode: Literal["file", "folder"]) -> None:
        self.invoice_schema_file = invoice_schema_file
        self.output_path = output_path
        self.mode = mode

    def invoke(self) -> None:
        """Invokes the command and generates an Excel invoice.

        Args:
            ctx (click.Context): The Click context object.

        Returns:
            None
        """
        click.echo("📄 Generating ExcelInvoice template...")
        click.echo(f"- Schema: {self.invoice_schema_file}")
        click.echo(f"- Output: {self.output_path}")
        click.echo(f"- Mode: {self.mode}")

        try:
            if not self.invoice_schema_file.exists():
                emsg = f"Schema file not found: {self.invoice_schema_file}"
                raise FileNotFoundError(emsg)
            ExcelInvoiceFile.generate_template(self.invoice_schema_file, self.output_path, self.mode)
            click.echo(click.style(f"✨ ExcelInvoice template generated successfully! : {self.output_path}", fg="green"))
        except InvoiceSchemaValidationError as e:
            logger.error(f"File error: {e}")
            click.echo(click.style(f"🔥 Schema Error: {e}", fg="red"))
            raise click.Abort from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            click.echo(click.style(f"🔥 Error: An unexpected error occurred: {e}", fg="red"))
            raise click.Abort from e
