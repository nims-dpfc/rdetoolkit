# ---------------------------------------------------------
# Copyright (c) 2023, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
#
# Contributor:
#     Hayato Sonokawa
# ---------------------------------------------------------
# coding: utf-8
from pathlib import Path
from typing import Generator, Optional

from src.rdetoolkit.models.rde2types import (RdeFormatFlags, RdeInputDirPaths,
                                             RdeOutputResourcePath)
from src.rdetoolkit.modeproc import selected_input_checker
from src.rdetoolkit.rde2util import StorageDir


def check_files(srcpaths: RdeInputDirPaths, *, fmt_flags: RdeFormatFlags) -> tuple[list[tuple[Path, ...]], Optional[Path]]:
    """Classify input files to determine if the input pattern is appropriate.
    In accordance with two input modes and the file type of the data to be registered,
    the following input pattern classification is performed.

    1 Invoice
        1-1 File mode (e.g. sample.txt)
        1-2 Folder mode (e.g. sample1.txt, sample2.txt)
        1-3 Input file none
    2 ExcelInvoice
        2-1 File mode (e.g. sample.zip (compressed with only one file) + *_excel_invoice.xlsx)
        2-2 Folder mode (e.g. sample.zip (folder compressed) + *_excel_invoice.xlsx)
        2-3 None (e.g. *_excel_invoice.xlsx)
    3 Format (e.g. *.zip, tasksupport/rdeformat.txt)
    4 Multiple Files in a Flat Structure (e.g., sample1.txt, sample2.txt, sample3.txt)

    Returns:
        tuple(list[tuple[Path, ...]]), Optional[Path]):
        Registered data file path group, presence of Excel invoice file

    Examples:
        # 1-1: Type: Invoice / Mode: File / Input: single file
        >>> checkFiles()
        tuple([(Path('data/inputdata/sample.txt'),)], None)

        # 1-2 : Type: Invoice / Mode: Folder / Input: multi files
        >>> checkFiles()
        tuple([(Path('data/inputdata/sample1.txt'), (Path('data/inputdata/sample2.txt'))], None)

        # 1-3 : Type: Invoice / Mode: None / Input: no files
        >>> checkFiles()
        tuple([()], None)

        # 2-1: Type: ExcelInvoice / Mode: File / Input: zip + *_excel_invoice.xlsx
        >>> checkFiles()
        tuple([(Path('data/inputdata/sample.txt'),)], Path("data/inputdata/dataset_excel_invoice.xlsx"))

        # 2-2: Type: ExcelInvoice / Mode: Folder / Input: zip + *_excel_invoice.xlsx
        >>> checkFiles()
        tuple([(Path('data/inputdata/sample1.txt'), (Path('data/inputdata/sample2.txt'))], Path("data/inputdata/dataset_excel_invoice.xlsx"))

        # 2-3: Type: ExcelInvoice / Mode: None / Input: *_excel_invoice.xlsx
        >>> checkFiles()
        tuple([], Path("data/inputdata/dataset_excel_invoice.xlsx"))

    Note:
        The destination paths for reading input files are different for the shipping label and ExcelInvoice.
        invoice: /data/inputdata/<registered_files>
        excelinvoice: /data/temp/<registered_files>
    """
    out_dir_temp = StorageDir.get_specific_outputdir(True, "temp")
    input_checker = selected_input_checker(srcpaths, out_dir_temp, fmt_flags)
    rawfiles, excelinvoice = input_checker.parse(srcpaths.inputdata)

    return rawfiles, excelinvoice


def generate_folder_paths_iterator(
    raw_files_group: list[tuple[Path, ...]], invoice_org_filepath: Path, invoice_schema_filepath: Path
) -> Generator[RdeOutputResourcePath, None, None]:
    """Generates iterator for RDE output folder paths
    Create data folders for registration in the RDE system.
    Excel invoice: Create divided folders according to the number of registered data.

    Args:
        raw_files_group (List[Tuple[pathlib.Path, ...]]): A list of tuples containing raw file paths.
        invoice_org_filepath (pathlib.Path): invoice_org.json file path
        invoice_schema_filepath (Path): invoice.schema.json file path

    Yields:
        RdeOutputResourcePath: A named tuple of output folder paths for RDE resources

    Raises:
        StructuredError: Occurs when the structured process fails to process correctly.

    Examples:
        >>> rawFilesTplList = [(Path('data/temp/samle1.txt'),), (Path('data/temp/sample2.txt'),), (Path('data/temp/sample3.txt'),)]
        >>> excel_invoice_files = Path("data/inputdata/sample_excel_invoice.xlsx")
        >>> create_folders(raw_files_group, excel_invoice_files)

    TODO: エクセルインボイスで登録時にraw_files_groupがnullの場合への対応
    """
    for idx, raw_files in enumerate(raw_files_group):
        rdeoutput_resource_path = RdeOutputResourcePath(
            raw=StorageDir.get_specific_outputdir(True, "raw", idx),
            rawfiles=raw_files,
            struct=StorageDir.get_specific_outputdir(True, "structured", idx),
            main_image=StorageDir.get_specific_outputdir(True, "main_image", idx),
            other_image=StorageDir.get_specific_outputdir(True, "other_image", idx),
            thumbnail=StorageDir.get_specific_outputdir(True, "thumbnail", idx),
            meta=StorageDir.get_specific_outputdir(True, "meta", idx),
            logs=StorageDir.get_specific_outputdir(True, "logs", idx),
            invoice=StorageDir.get_specific_outputdir(True, "invoice", idx),
            invoice_schema_json=invoice_schema_filepath,
            invoice_org=invoice_org_filepath,
            temp=StorageDir.get_specific_outputdir(True, "temp", idx),
        )
        yield rdeoutput_resource_path
