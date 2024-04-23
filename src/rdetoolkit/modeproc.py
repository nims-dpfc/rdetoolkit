import os
import shutil
from pathlib import Path
from typing import Callable, Optional

from rdetoolkit import img2thumb
from rdetoolkit.config import Config
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.impl.input_controller import (
    ExcelInvoiceChecker,
    InvoiceChecker,
    MultiFileChecker,
    RDEFormatChecker,
)
from rdetoolkit.interfaces.filechecker import IInputFileChecker
from rdetoolkit.invoiceFile import (
    ExcelInvoiceFile,
    InvoiceFile,
    apply_default_filename_mapping_rule,
    update_description_with_features,
)
from rdetoolkit.models.rde2types import RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import read_from_json_file
from rdetoolkit.validation import invoice_validate, metadata_def_validate

_CallbackType = Callable[[RdeInputDirPaths, RdeOutputResourcePath], None]


def rdeformat_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = None, config: Optional[Config] = None):
    """Process the source data and apply specific transformations using the provided callback function.

    This function performs several steps:

    1. Overwrites the invoice file.
    2. Copies input files to the rawfile directory.
    3. Runs a custom dataset process function if provided.
    4. Copies images to the thumbnail directory.
    5. Updates descriptions with features, ignoring any errors during this step.
    6. Validates the metadata-def.json file.
    7. Validates the invoice file against the invoice schema.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        datasets_process_function (_CallbackType, optional): A callback function that processes datasets. Defaults to None.
        config (Config, optional): Configuration instance for structured processing execution. Defaults to None.

    Raises:
        Any exceptions raised by `datasets_process_function` or during the validation steps will propagate upwards. Exceptions during the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    if config is None:
        config = Config()
    # rewriting the invoice
    invoice = InvoiceFile(resource_paths.invoice_org)
    invoice_dst_filepath = resource_paths.invoice.joinpath("invoice.json")
    invoice.overwrite(invoice_dst_filepath)
    copy_input_to_rawfile_for_rdeformat(resource_paths)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    if config.save_thumbnail_image:
        img2thumb.copy_images_to_thumbnail(
            resource_paths.thumbnail,
            resource_paths.main_image,
        )

    try:
        update_description_with_features(resource_paths, invoice_dst_filepath, srcpaths.tasksupport.joinpath("metadata-def.json"))
    except Exception:
        pass

    # validate metadata-def.json
    metadata_def_validate(srcpaths.tasksupport.joinpath("metadata-def.json"))

    # validate metadata-def.json
    schema_path = srcpaths.tasksupport.joinpath("invoice.schema.json")
    invoice_validate(invoice_dst_filepath, schema_path)


def multifile_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = None, config: Optional[Config] = None):
    """Processes multiple source files and applies transformations using the provided callback function.

    This function performs several steps:

    1. Overwrites the invoice file.
    2. Copies input files to the rawfile directory.
    3. Runs a custom dataset process function if provided.
    4. Replaces the placeholder '${filename}' in the invoice with the actual filename if necessary.
    5. Copies images to the thumbnail directory.
    6. Attempts to update descriptions with features, ignoring any errors during this step.
    7. Validates the metadata-def.json file.
    8. Validates the invoice file against the invoice schema.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        datasets_process_function (_CallbackType, optional): A callback function that processes datasets. Defaults to None.
        config (Config, optional): Configuration instance for structured processing execution. Defaults to None.

    Raises:
        Any exceptions raised by `datasets_process_function` or during the validation steps will propagate upwards. Exceptions during the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    if config is None:
        config = Config()

    invoice = InvoiceFile(resource_paths.invoice_org)
    invoice_dst_filepath = resource_paths.invoice.joinpath("invoice.json")
    invoice.overwrite(invoice_dst_filepath)

    if config.save_raw:
        copy_input_to_rawfile(resource_paths.raw, resource_paths.rawfiles)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    # rewriting support for ${filename} by default
    if config.magic_variable:
        invoice_contents = read_from_json_file(resource_paths.invoice.joinpath("invoice.json"))
        if invoice_contents.get("basic", {}).get("dataName") == "${filename}":
            replacement_rule = {"${filename}": str(resource_paths.rawfiles[0].name)}
            apply_default_filename_mapping_rule(replacement_rule, resource_paths.invoice.joinpath("invoice.json"))

    if config.save_thumbnail_image:
        img2thumb.copy_images_to_thumbnail(resource_paths.thumbnail, resource_paths.main_image)

    try:
        update_description_with_features(resource_paths, invoice_dst_filepath, srcpaths.tasksupport.joinpath("metadata-def.json"))
    except Exception:
        pass

    # validate metadata-def.json
    metadata_def_validate(srcpaths.tasksupport.joinpath("metadata-def.json"))

    # validate metadata-def.json
    schema_path = srcpaths.tasksupport.joinpath("invoice.schema.json")
    invoice_validate(invoice_dst_filepath, schema_path)


def excel_invoice_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, excel_invoice_file: Path, idx: int, datasets_process_function: Optional[_CallbackType] = None, config: Optional[Config] = None):
    """Processes invoice data from an Excel file and applies dataset transformations using the provided callback function.

    This function performs several steps:

    1. Overwrites the Excel invoice file.
    2. Copies input files to the rawfile directory.
    3. Runs a custom dataset process function if provided.
    4. Replaces the placeholder '${filename}' in the invoice with the actual filename if necessary.
    5. Copies images to the thumbnail directory.
    6. Attempts to update descriptions with features, ignoring any errors during this step.
    7. Validates the metadata-def.json file.
    8. Validates the invoice file against the invoice schema.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        excel_invoice_file (Path): Path to the source Excel invoice file.
        idx (int): Index or identifier for the data being processed.
        datasets_process_function (_CallbackType, optional): A callback function that processes datasets. Defaults to None.
        config (Config, optional): Configuration instance for structured processing execution. Defaults to None.

    Raises:
        StructuredError: When encountering issues related to Excel invoice overwriting or during the validation steps.
        Any exceptions raised by `datasets_process_function` will propagate upwards. Exceptions during the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    if config is None:
        config = Config()

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

    if config.save_raw:
        copy_input_to_rawfile(resource_paths.raw, resource_paths.rawfiles)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    # rewriting support for ${filename} by default
    # Excelinvoice applies to file mode only, folder mode is not supported.
    # FileMode has only one element in resource_paths.rawfiles.
    if config.magic_variable:
        invoice_contents = read_from_json_file(resource_paths.invoice.joinpath("invoice.json"))
        if invoice_contents.get("basic", {}).get("dataName") == "${filename}" and len(resource_paths.rawfiles) == 1:
            replacement_rule = {"${filename}": str(resource_paths.rawfiles[0].name)}
            apply_default_filename_mapping_rule(replacement_rule, resource_paths.invoice.joinpath("invoice.json"))

    if config.save_thumbnail_image:
        img2thumb.copy_images_to_thumbnail(resource_paths.thumbnail, resource_paths.main_image)

    try:
        update_description_with_features(resource_paths, resource_paths.invoice.joinpath("invoice.json"), srcpaths.tasksupport.joinpath("metadata-def.json"))
    except Exception:
        pass

    # validate metadata-def.json
    metadata_def_validate(srcpaths.tasksupport.joinpath("metadata-def.json"))

    # validate metadata-def.json
    schema_path = srcpaths.tasksupport.joinpath("invoice.schema.json")
    invoice_validate(resource_paths.invoice.joinpath("invoice.json"), schema_path)


def invoice_mode_process(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath, datasets_process_function: Optional[_CallbackType] = None, config: Optional[Config] = None):
    """Processes invoice-related data, applies dataset transformations using the provided callback function, and updates descriptions.

    This function performs several steps:

    1. Copies input files to the rawfile directory.
    2. Runs a custom dataset process function if provided.
    3. Copies images to the thumbnail directory.
    4. Replaces the placeholder '${filename}' in the invoice with the actual filename if necessary.
    5. Attempts to update descriptions with features, ignoring any errors during this step.
    6. Validates the metadata-def.json file.
    7. Validates the invoice file against the invoice schema.

    Args:
        srcpaths (RdeInputDirPaths): Input paths for the source data.
        resource_paths (RdeOutputResourcePath): Paths to the resources where data will be written or read from.
        datasets_process_function (_CallbackType, optional): A callback function that processes datasets. Defaults to None.
        config (Config, optional): Configuration instance for structured processing execution. Defaults to None.

    Raises:
        Any exceptions raised by `datasets_process_function` will propagate upwards. Exceptions during the `update_description_with_features` step are caught and silently ignored.

    Returns:
        None
    """
    if config is None:
        config = Config()

    if config.save_raw:
        copy_input_to_rawfile(resource_paths.raw, resource_paths.rawfiles)

    # run custom dataset process
    if datasets_process_function is not None:
        datasets_process_function(srcpaths, resource_paths)

    if config.save_thumbnail_image:
        img2thumb.copy_images_to_thumbnail(resource_paths.thumbnail, resource_paths.main_image)

    # rewriting support for ${filename} by default
    if config.magic_variable:
        invoice_contents = read_from_json_file(resource_paths.invoice.joinpath("invoice.json"))
        if invoice_contents.get("basic", {}).get("dataName") == "${filename}":
            replacement_rule = {"${filename}": str(resource_paths.rawfiles[0].name)}
            apply_default_filename_mapping_rule(replacement_rule, resource_paths.invoice.joinpath("invoice.json"))

    try:
        update_description_with_features(resource_paths, resource_paths.invoice.joinpath("invoice.json"), srcpaths.tasksupport.joinpath("metadata-def.json"))
    except Exception:
        pass

    # validate metadata-def.json
    metadata_def_validate(srcpaths.tasksupport.joinpath("metadata-def.json"))

    # validate metadata-def.json
    schema_path = srcpaths.tasksupport.joinpath("invoice.schema.json")
    invoice_validate(resource_paths.invoice.joinpath("invoice.json"), schema_path)


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
        "nonshared_raw": resource_paths.nonshared_raw,
    }
    for f in resource_paths.rawfiles:
        for dir_name, directory in directories.items():
            if dir_name in f.parts:
                shutil.copy(f, os.path.join(str(directory), f.name))
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


def selected_input_checker(src_paths: RdeInputDirPaths, unpacked_dir_path: Path, mode: str) -> IInputFileChecker:
    """Determine the appropriate input file checker based on the provided format flags and source paths.

    The function scans the source paths to identify the type of input files present. Based on the file type
    and format flags provided, it instantiates and returns the appropriate checker.

    Args:
        src_paths (RdeInputDirPaths): Paths for the source input files.
        unpacked_dir_path (Path): Directory path for unpacked files.
        mode (str): Format flags indicating which checker mode is enabled.

    Returns:
        IInputFileChecker: An instance of the appropriate input file checker based on the provided criteria.

    Raises:
        None, but callers should be aware that downstream exceptions can be raised by individual checker initializations.
    """
    input_files = [f for f in src_paths.inputdata.glob("*")]
    excel_invoice_files = [f for f in input_files if f.suffix.lower() in [".xls", ".xlsx"] and f.stem.endswith("_excel_invoice")]
    if mode == "rdeformat":
        return RDEFormatChecker(unpacked_dir_path)
    elif mode == "multifile":
        return MultiFileChecker(unpacked_dir_path)
    elif excel_invoice_files:
        return ExcelInvoiceChecker(unpacked_dir_path)
    else:
        return InvoiceChecker(unpacked_dir_path)
