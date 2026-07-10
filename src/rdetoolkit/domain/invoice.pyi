from pathlib import Path
from rdetoolkit.invoicefile import ExcelInvoiceFile as ExcelInvoiceFile, InvoiceFile as InvoiceFile, SmartTableFile as SmartTableFile
from rdetoolkit.types import InvoiceData as InvoiceData

def load_invoice(invoice_path: str | Path, *, schema_path: str | Path | None = None) -> InvoiceData: ...
def open_invoice_file(invoice_path: str | Path, *, schema_path: str | Path | None = None) -> InvoiceFile: ...
def open_excel_invoice(invoice_path: str | Path) -> ExcelInvoiceFile: ...
def open_smarttable(table_path: str | Path) -> SmartTableFile: ...
def build_excelinvoice_tile_invoice(
    *,
    excel_path: Path,
    invoice_org: Path,
    invoice_schema_path: Path,
    dist_path: Path,
    idx: int,
) -> InvoiceData: ...
def build_smarttable_tile_invoice(
    *,
    smarttable_rowfile: Path,
    invoice_org: Path,
    invoice_schema_path: Path,
    dist_path: Path,
    rawfiles: tuple[Path, ...] = ...,
) -> InvoiceData: ...
