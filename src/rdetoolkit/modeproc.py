import os
import shutil
from pathlib import Path
from typing import Callable, Optional

from rdetoolkit import img2thumb
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.impl.input_controller import ExcelInvoiceChecker, InvoiceChechker, MultiFileChecker, RDEFormatChecker
from rdetoolkit.interfaces.filechecker import IInputFileChecker
from rdetoolkit.invoiceFile import ExcelInvoiceFile, InvoiceFile, update_description_with_features, apply_default_filename_mapping_rule
from rdetoolkit.models.rde2types import RdeFormatFlags, RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import read_from_json_file


_CallbackType = Callable[[RdeInputDirPaths, RdeOutputResourcePath], None]


def rdeformat_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = None):
    """Process the source data and apply specific transformations using the provided callback function.

    This function performs several steps, including overwriting the invoice,
    copying input files, and updating descriptions. Any errors during the description
    update step are silently ignored.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        datasets_process_function (_CallbackType): A callback function that processes datasets.

    Raises:
        Any exceptions raised by `datasets_process_function` will propagate upwards. Exceptions during
        the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    # rewriting the invoice
    invoice = InvoiceFile(resource_paths.invoice_org)
    invoice_dst_filepath = resource_paths.invoice.joinpath("invoice.json")
    invoice.overwrite(invoice_dst_filepath)
    copy_input_to_rawfile_for_rdeformat(resource_paths)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    img2thumb.copy_images_to_thumbnail(
        resource_paths.thumbnail,
        resource_paths.main_image,
        out_dir_other_img=resource_paths.other_image,
    )

    try:
        update_description_with_features(resource_paths, invoice_dst_filepath, srcpaths.tasksupport.joinpath("metadata-def.json"))
    except Exception:
        pass


def multifile_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = None):
    """Processes multiple source files and applies transformations using the provided callback function.

    This function handles tasks related to invoices, processes datasets, and attempts
    to update descriptions with features. Errors during the update step are silently ignored.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        datasets_process_function (_CallbackType): A callback function that processes datasets.

    Raises:
        Any exceptions raised by `datasets_process_function` will propagate upwards. Exceptions during
        the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    invoice = InvoiceFile(resource_paths.invoice_org)
    invoice_dst_filepath = resource_paths.invoice.joinpath("invoice.json")
    invoice.overwrite(invoice_dst_filepath)

    copy_input_to_rawfile(resource_paths.raw, resource_paths.rawfiles)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    # rewriting support for ${filename} by default
    invoice_contents = read_from_json_file(resource_paths.invoice.joinpath("invoice.json"))
    if invoice_contents.get("basic", {}).get("dataName") == "${filename}":
        replacement_rule = {"${filename}": str(resource_paths.rawfiles[0].name)}
        apply_default_filename_mapping_rule(replacement_rule, resource_paths.invoice.joinpath("invoice.json"))

    img2thumb.copy_images_to_thumbnail(
        resource_paths.thumbnail,
        resource_paths.main_image,
        out_dir_other_img=resource_paths.other_image,
    )

    try:
        update_description_with_features(resource_paths, invoice_dst_filepath, srcpaths.tasksupport.joinpath("metadata-def.json"))
    except Exception:
        pass


def excel_invoice_mode_process(
    srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, excel_invoice_file: Path, idx: int, datasets_process_function: Optional[_CallbackType] = None
):
    """Process invoice data from an Excel file and apply dataset transformations using the provided callback function.

    This function handles tasks such as overwriting Excel invoices, copying input to raw files,
    processing datasets, and updating descriptions with features. Specific exceptions are caught and
    re-raised as structured errors for easier troubleshooting.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        excel_invoice_file (Path): Path to the source Excel invoice file.
        idx (int): Index or identifier for the data being processed.
        datasets_process_function (_CallbackType): A callback function that processes datasets.

    Raises:
        StructuredError: When encountering issues related to Excel invoice overwriting.
        Any exceptions raised by `datasets_process_function` will propagate upwards. Exceptions during
        the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    # rewriting the invoice
    excel_invoice = ExcelInvoiceFile(excel_invoice_file)
    try:
        excel_invoice.overwrite(
            resource_paths.invoice_org,
            resource_paths.invoice.joinpath("invoice.json"),
            resource_paths.invoice_schema_json,
            idx,
        )
    except StructuredError:
        raise
    except Exception as e:
        raise StructuredError(
            f"ERROR: failed to generate invoice file for data {idx:04d}",
            eObj=e,
        )

    copy_input_to_rawfile(resource_paths.raw, resource_paths.rawfiles)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    # rewriting support for ${filename} by default
    # Excelinvoice applies to file mode only, folder mode is not supported.
    # FileMode has only one element in resource_paths.rawfiles.
    invoice_contents = read_from_json_file(resource_paths.invoice.joinpath("invoice.json"))
    if invoice_contents.get("basic", {}).get("dataName") == "${filename}" and len(resource_paths.rawfiles) == 1:
        replacement_rule = {"${filename}": str(resource_paths.rawfiles[0].name)}
        apply_default_filename_mapping_rule(replacement_rule, resource_paths.invoice.joinpath("invoice.json"))

    img2thumb.copy_images_to_thumbnail(
        resource_paths.thumbnail,
        resource_paths.main_image,
        out_dir_other_img=resource_paths.other_image,
    )

    try:
        update_description_with_features(
            resource_paths, resource_paths.invoice.joinpath("invoice.json"), srcpaths.tasksupport.joinpath("metadata-def.json")
        )
    except Exception:
        pass


def invoice_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = None):
    """Processes invoice-related data, applies dataset transformations using the provided callback function, and updates descriptions.

    This function first copies input data to raw files, then processes the datasets, and finally attempts
    to update descriptions with features. Any exceptions encountered during the description update step are silently ignored.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        datasets_process_function (_CallbackType): A callback function that processes datasets.

    Raises:
        Any exceptions raised by `datasets_process_function` will propagate upwards. Exceptions during
        the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    copy_input_to_rawfile(resource_paths.raw, resource_paths.rawfiles)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    # rewriting support for ${filename} by default
    invoice_contents = read_from_json_file(resource_paths.invoice.joinpath("invoice.json"))
    if invoice_contents.get("basic", {}).get("dataName") == "${filename}":
        replacement_rule = {"${filename}": str(resource_paths.rawfiles[0].name)}
        apply_default_filename_mapping_rule(replacement_rule, resource_paths.invoice.joinpath("invoice.json"))

    img2thumb.copy_images_to_thumbnail(
        resource_paths.thumbnail,
        resource_paths.main_image,
        out_dir_other_img=resource_paths.other_image,
    )

    try:
        update_description_with_features(
            resource_paths, resource_paths.invoice.joinpath("invoice.json"), srcpaths.tasksupport.joinpath("metadata-def.json")
        )
    except Exception:
        pass


def copy_input_to_rawfile_for_rdeformat(resource_paths: RdeOutputResourcePath):
    """Copy the input raw files to their respective directories based on the file's part names.

    This function scans through the parts of each file's path in `resource_paths.rawfiles`. If the file path
    contains a directory name listed in the `directories` dict, the file will be copied to the corresponding
    directory.

    Args:
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.

    Returns:
        None
    """
    directories = {
        "raw": resource_paths.raw,
        "main_image": resource_paths.main_image,
        "other_image": resource_paths.other_image,
        "meta": resource_paths.meta,
        "structured": resource_paths.struct,
        "logs": resource_paths.logs,
    }
    for f in resource_paths.rawfiles:
        for dir_name, directory in directories.items():
            if dir_name in f.parts:
                shutil.copy(f, os.path.join(directory, f.name))
                break


def copy_input_to_rawfile(raw_dir_path: Path, raw_files: tuple[Path, ...]):
    """Copy the input raw files to the specified directory.

    This function takes a list of raw file paths and copies each file to the given `raw_dir_path`.

    Args:
        raw_dir_path (Path): The directory path where the raw files will be copied to.
        raw_files (tuple[Path, ...]): A tuple of file paths that need to be copied.

    Returns:
        None
    """
    for f in raw_files:
        shutil.copy(f, os.path.join(raw_dir_path, f.name))


def selected_input_checker(src_paths: RdeInputDirPaths, unpacked_dir_path: Path, fmtflags: RdeFormatFlags) -> IInputFileChecker:
    """Determine the appropriate input file checker based on the provided format flags and source paths.

    The function scans the source paths to identify the type of input files present. Based on the file type
    and format flags provided, it instantiates and returns the appropriate checker.

    Args:
        src_paths (RdeInputDirPaths): Paths for the source input files.
        unpacked_dir_path (Path): Directory path for unpacked files.
        fmtflags (RdeFormatFlags): Format flags indicating which checker mode is enabled.

    Returns:
        IInputFileChecker: An instance of the appropriate input file checker based on the provided criteria.

    Raises:
        None, but callers should be aware that downstream exceptions can be raised by individual checker initializations.
    """
    input_files = [f for f in src_paths.inputdata.glob("*")]
    excel_invoice_files = [f for f in input_files if f.suffix.lower() in [".xls", ".xlsx"] and f.stem.endswith("_excel_invoice")]
    if fmtflags.is_rdeformat_enabled:
        return RDEFormatChecker(unpacked_dir_path)
    elif fmtflags.is_multifile_enabled:
        return MultiFileChecker(unpacked_dir_path)
    elif excel_invoice_files:
        return ExcelInvoiceChecker(unpacked_dir_path)
    else:
        return InvoiceChechker(unpacked_dir_path)
