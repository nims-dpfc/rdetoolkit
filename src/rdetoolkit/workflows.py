from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from rdetoolkit.config import load_config
from rdetoolkit.errors import handle_and_exit_on_structured_error, handle_generic_error, skip_exception_context
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.invoicefile import backup_invoice_json_files
from rdetoolkit.models.config import Config
from rdetoolkit.models.rde2types import RawFiles, RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.models.result import WorkflowExecutionStatus, WorkflowResultManager
from rdetoolkit.modeproc import (
    _CallbackType,
    excel_invoice_mode_process,
    invoice_mode_process,
    multifile_mode_process,
    rdeformat_mode_process,
    selected_input_checker,
)
from rdetoolkit.rde2util import StorageDir
from rdetoolkit.rdelogger import get_logger


def check_files(srcpaths: RdeInputDirPaths, *, mode: str | None) -> tuple[RawFiles, Path | None]:
    """Classify input files to determine if the input pattern is appropriate.

    1. Invoice
        1. File mode (e.g. sample.txt)
        2. Folder mode (e.g. sample1.txt, sample2.txt)
        3. Input file none
    2. ExcelInvoice
        1. File mode (e.g. sample.zip (compressed with only one file) + *_excel_invoice.xlsx)
        2. Folder mode (e.g. sample.zip (folder compressed) + *_excel_invoice.xlsx)
        2-3. None (e.g. *_excel_invoice.xlsx)
    3. Format (e.g. *.zip, tasksupport/rdeformat.txt)
    4. Multiple Files in a Flat Structure (e.g., sample1.txt, sample2.txt, sample3.txt)

    Returns:
        tuple(list[tuple[Path, ...]]), Optional[Path]):
        Registered data file path group, presence of Excel invoice file

    Example:
        ```python
        # MODE: Invoice / Mode: File / Input: single file
        check_files(srcpaths, fmt_flags=format_flags)
        tuple([(Path('data/inputdata/sample.txt'),)], None)

        # MODE: Invoice / Mode: Folder / Input: multi files
        check_files(srcpaths, fmt_flags=format_flags)
        tuple([(Path('data/inputdata/sample1.txt'), (Path('data/inputdata/sample2.txt'))], None)

        # MODE: Invoice / Mode: None / Input: no files
        check_files(srcpaths, fmt_flags=format_flags)
        tuple([()], None)

        # MODE: ExcelInvoice / Mode: File / Input: zip + *_excel_invoice.xlsx
        check_files(srcpaths, fmt_flags=format_flags)
        tuple([(Path('data/inputdata/sample.txt'),)], Path("data/inputdata/dataset_excel_invoice.xlsx"))

        # MODE: ExcelInvoice / Mode: Folder / Input: zip + *_excel_invoice.xlsx
        checkFiles(srcpaths, fmt_flags=format_flags)
        tuple([(Path('data/inputdata/sample1.txt'), (Path('data/inputdata/sample2.txt'))], Path("data/inputdata/dataset_excel_invoice.xlsx"))

        # MODE: ExcelInvoice / Mode: None / Input: *_excel_invoice.xlsx
        check_files(srcpaths, fmt_flags=format_flags)
        tuple([], Path("data/inputdata/dataset_excel_invoice.xlsx"))
        ```

    Note:
        The destination paths for reading input files are different for the shipping label and ExcelInvoice.
        invoice: /data/inputdata/<registered_files>
        excelinvoice: /data/temp/<registered_files>
    """
    out_dir_temp = StorageDir.get_specific_outputdir(True, "temp")
    if mode is None:
        mode = ""
    input_checker = selected_input_checker(srcpaths, out_dir_temp, mode)
    rawfiles, excelinvoice = input_checker.parse(srcpaths.inputdata)

    return rawfiles, excelinvoice


def generate_folder_paths_iterator(
    raw_files_group: RawFiles,
    invoice_org_filepath: Path,
    invoice_schema_filepath: Path,
) -> Generator[RdeOutputResourcePath, None, None]:
    """Generates iterator for RDE output folder paths.

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

    Example:
        ```python
        rawfiles_tplList = [(Path('data/temp/samle1.txt'),), (Path('data/temp/sample2.txt'),), (Path('data/temp/sample3.txt'),)]

        excel_invoice_files = Path("data/inputdata/sample_excel_invoice.xlsx")

        create_folders(raw_files_group, excel_invoice_files)
        ```
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
            nonshared_raw=StorageDir.get_specific_outputdir(True, "nonshared_raw", idx),
            invoice_patch=StorageDir.get_specific_outputdir(True, "invoice_patch", idx),
            attachment=StorageDir.get_specific_outputdir(True, "attachment", idx),
        )
        yield rdeoutput_resource_path


def run(*, custom_dataset_function: _CallbackType | None = None, config: Config | None = None) -> str:  # pragma: no cover
    """RDE Structuring Processing Function.

    This function executes the structuring process for RDE data. If you want to implement custom processing for the input data,
    you can pass a user-defined function as an argument. The function should accept the data class `RdeInputDirPaths`, which is
    internally parsed by RDE, and the data class `RdeOutputResourcePath`, which stores the output directory paths used by RDE.

    Args:
        custom_dataset_function (Optional[_CallbackType], optional): User-defined structuring function. Defaults to None.
        config (Optional[Config], optional): Configuration class for the structuring process. If not specified, default values are loaded automatically. Defaults to None.

    Returns:
        str: The JSON representation of the workflow execution results.

    Raises:
        StructuredError: If a structured error occurs during the process.
        Exception: If a generic error occurs during the process.

    Note:
        If `extended_mode` is specified, the evaluation of the execution mode is performed in the order of `extended_mode -> excelinvoice -> invoice`,
        and the structuring process is executed.

    Example:
        ```python
        ### custom.py
        def custom_dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath) -> None:
            ...(original process)...

        ### main.py
        from rdetoolkit import workflow
        from custom import custom_dataset # User-defined structuring processing function

        cfg = Config(save_raw=True, save_main_image=False, save_thumbnail_image=False, magic_variable=False)
        workflow.run(custom_dataset_function=custom_dataset, config=cfg) # Execute structuring process
        ```

        If options are specified (setting the mode to "RDEformat"):

        ```python
        ### main.py
        from rdetoolkit.config import Config
        from rdetoolkit import workflow
        from custom import custom_dataset # User-defined structuring processing function

        cfg = Config(extended_mode="rdeformat", save_raw=True, save_main_image=False, save_thumbnail_image=False, magic_variable=False)
        workflow.run(custom_dataset_function=custom_dataset, config=cfg) # Execute structuring process
        ```
    """
    logger = get_logger(__name__, file_path=StorageDir.get_specific_outputdir(True, "logs").joinpath("rdesys.log"))
    wf_manager = WorkflowResultManager()
    error_info = None

    try:
        # Enabling mode flag and validating input file
        srcpaths = RdeInputDirPaths(
            inputdata=StorageDir.get_specific_outputdir(False, "inputdata"),
            invoice=StorageDir.get_specific_outputdir(False, "invoice"),
            tasksupport=StorageDir.get_specific_outputdir(False, "tasksupport"),
        )

        # Loading configuration file
        __config = load_config(str(srcpaths.tasksupport), config=config)
        srcpaths.config = __config

        raw_files_group, excel_invoice_files = check_files(srcpaths, mode=__config.system.extended_mode)

        # Backup of invoice.json
        invoice_org_filepath = backup_invoice_json_files(excel_invoice_files, __config.system.extended_mode)
        invoice_schema_filepath = srcpaths.tasksupport.joinpath("invoice.schema.json")

        # Execution of data set structuring process based on various modes
        for idx, rdeoutput_resource in enumerate(generate_folder_paths_iterator(raw_files_group, invoice_org_filepath, invoice_schema_filepath)):
            if __config.system.extended_mode is not None and __config.system.extended_mode.lower() == "rdeformat":
                mode = "rdeformat"
                status = rdeformat_mode_process(str(idx), srcpaths, rdeoutput_resource, custom_dataset_function)
            elif __config.system.extended_mode is not None and __config.system.extended_mode.lower() == "multidatatile":
                mode = "MultiDataTile"
                ignore_error = __config.multidata_tile.ignore_errors if __config.multidata_tile else False
                with skip_exception_context(Exception, logger=logger, enabled=ignore_error) as error_info:
                    status = multifile_mode_process(str(idx), srcpaths, rdeoutput_resource, custom_dataset_function)
            elif excel_invoice_files is not None:
                mode = "Excelinvoice"
                status = excel_invoice_mode_process(srcpaths, rdeoutput_resource, excel_invoice_files, idx, custom_dataset_function)
            else:
                mode = "Invoice"
                status = invoice_mode_process(str(idx), srcpaths, rdeoutput_resource, custom_dataset_function)

            if error_info and any(value is not None for value in error_info.values()):
                code = error_info.get("code")
                status = WorkflowExecutionStatus(
                    run_id=str(idx),
                    title=f"Structured Process Faild: {mode}",
                    status="failed",
                    mode=mode,
                    error_code=int(code) if code and code.isdigit() else 999,
                    error_message=error_info.get("message"),
                    stacktrace=error_info.get("stacktrace"),
                    target=",".join(str(file) for file in rdeoutput_resource.rawfiles),
                )
            wf_manager.add_status(status)

    except StructuredError as e:
        handle_and_exit_on_structured_error(e, logger)
    except Exception as e:
        handle_generic_error(e, logger)

    return wf_manager.to_json()
