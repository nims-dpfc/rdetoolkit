from __future__ import annotations

import copy
import json
import os
import shutil
from pathlib import Path
from typing import Any, Callable

import chardet
import pandas as pd

from rdetoolkit import rde2util
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.fileops import readf_json, writef_json
from rdetoolkit.models.rde2types import RdeFsPath, RdeOutputResourcePath
from rdetoolkit.rde2util import StorageDir


def read_excelinvoice(excelinvoice_filepath: RdeFsPath) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reads an ExcelInvoice and processes each sheet into a dataframe.

    This function reads an ExcelInvoice file and processes various sheets within the file, specifically looking for sheets named `invoiceList_format_id`,`generalTerm`, and `specificTerm`.

    These sheets are converted into pandas dataframes and returned as output.

    Args:
        excelinvoice_filepath (str): The file path of the Excel invoice file.

    Returns:
        tuple: A tuple containing dataframes for the invoice list, general terms, and specific terms.If any of these sheets are missing or if there are multiple invoice list sheets, a StructuredError is raised.

    Raises:
        StructuredError: If there are multiple sheets with `invoiceList_format_id` in the ExcelInvoice, or if no sheets are present in the ExcelInvoice.
    """
    dct_sheets = pd.read_excel(excelinvoice_filepath, sheet_name=None, dtype=str, header=None, index_col=None)
    dfexcelinvoice = None
    df_general = None
    df_specific = None
    for sh_name, df in dct_sheets.items():
        if df.empty:
            continue
        if df.iat[0, 0] == "invoiceList_format_id":
            if dfexcelinvoice is not None:
                emsg = "ERROR: multiple sheet in invoiceList files"
                raise StructuredError(emsg)
            ExcelInvoiceFile.check_intermittent_empty_rows(df)
            dfexcelinvoice = __process_invoice_sheet(df)
        elif sh_name == "generalTerm":
            df_general = __process_general_term_sheet(df)
        elif sh_name == "specificTerm":
            df_specific = __process_specific_term_sheet(df)

    if dfexcelinvoice is None:
        emsg = "ERROR: no sheet in invoiceList files"
        raise StructuredError(emsg)
    return dfexcelinvoice, df_general, df_specific


def __process_invoice_sheet(df: pd.DataFrame) -> pd.Series:
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    hd1 = list(df.iloc[1, :].fillna(""))
    hd2 = list(df.iloc[2, :].fillna(""))
    df.columns = [f"{s1}/{s2}" if s1 else s2 for s1, s2 in zip(hd1, hd2)]
    return df.iloc[4:, :].reset_index(drop=True).copy()


def __process_general_term_sheet(df: pd.DataFrame) -> pd.Series:
    _df_general = df[1:].copy()
    _df_general.columns = ["term_id", "key_name"]
    return _df_general


def __process_specific_term_sheet(df: pd.DataFrame) -> pd.Series:
    _df_specific = df[1:].copy()
    _df_specific.columns = ["sample_class_id", "term_id", "key_name"]
    return _df_specific


def check_exist_rawfiles(dfexcelinvoice: pd.DataFrame, excel_rawfiles: list[Path]) -> list[Path]:
    """Checks for the existence of raw file paths listed in a DataFrame against a list of file Paths.

    This function compares a set of file names extracted from the `data_file_names/name` column of the provided DataFrame (dfexcelinvoice) with the names of files in the excel_rawfiles list.
    If there are file names in the DataFrame that are not present in the excel_rawfiles list, it raises a StructuredError with a message indicating the missing file.
    If all file names in the DataFrame are present in the excel_rawfiles list, it returns a list of Path objects from excel_rawfiles, sorted in the order they appear in the DataFrame.

    Args:
        dfexcelinvoice (pd.DataFrame): A DataFrame containing file names in the 'data_file_names/name' column.
        excel_rawfiles (list[Path]): A list of Path objects representing file paths.

    Raises:
        tructuredError: If any file name in dfexcelinvoice is not found in excel_rawfiles.

    Returns:
        list[Path]: A list of Path objects corresponding to the file names in dfexcelinvoice, ordered as they appear in the DataFrame.
    """
    file_set_group = {f.name for f in excel_rawfiles}
    file_set_invoice = set(dfexcelinvoice["data_file_names/name"])
    if file_set_invoice - file_set_group:
        emsg = f"ERROR: raw file not found: {(file_set_invoice-file_set_group).pop()}"
        raise StructuredError(emsg)
    # excel_rawfilesを、インボイス出現順に並び替える
    _tmp = {f.name: f for f in excel_rawfiles}
    return [_tmp[f] for f in dfexcelinvoice["data_file_names/name"]]


def _assign_invoice_val(invoiceobj: dict[str, Any], key1: str, key2: str, valobj: Any, invoiceschema_obj: dict[str, Any]) -> None:
    """When the destination key, which is the first key 'keys1', is 'custom', valobj is cast according to the invoiceschema_obj. In all other cases, valobj is assigned without changing its type."""
    if key1 == "custom":
        dct_schema = invoiceschema_obj["properties"][key1]["properties"][key2]
        try:
            invoiceobj[key1][key2] = rde2util.castval(valobj, dct_schema["type"], dct_schema.get("format"))
        except StructuredError as struct_err:
            emsg = f"ERROR: failed to cast invoice value for key [{key1}][{key2}]"
            raise StructuredError(emsg) from struct_err
    else:
        invoiceobj[key1][key2] = valobj


def overwrite_invoicefile_for_dpfterm(
    invoiceobj: dict[str, Any],
    invoice_dst_filepath: RdeFsPath,
    invoiceschema_filepath: RdeFsPath,
    invoice_info: dict[str, Any],
) -> None:
    """A function to overwrite DPF metadata into an invoice file.

    Args:
        invoiceobj (dict[str, Any]): The object of invoice.json.
        invoice_dst_filepath (RdeFsPath): The file path for the destination invoice.json.
        invoiceschema_filepath (RdeFsPath): The file path of invoice.schema.json.
        invoice_info (dict[str, Any]): Information about the invoice file.
    """
    with open(invoiceschema_filepath, "rb") as f:
        data = f.read()
    enc = chardet.detect(data)["encoding"]
    with open(invoiceschema_filepath, encoding=enc) as f:
        invoiceschema_obj = json.load(f)
    for k, v in invoice_info.items():
        _assign_invoice_val(invoiceobj, "custom", k, v, invoiceschema_obj)
    with open(invoice_dst_filepath, "w", encoding=enc) as fout:
        json.dump(invoiceobj, fout, indent=4, ensure_ascii=False)


def check_exist_rawfiles_for_folder(dfexcelinvoice: pd.DataFrame, rawfiles_tpl: tuple) -> list:
    """Function to check the existence of rawfiles_tpl specified for a folder.

    It checks whether rawfiles_tpl, specified as an index, exists in all indexes of ExcelInvoice.
    Assumes that the names of the terminal folders are unique and checks for the existence of rawfiles_tpl.

    Args:
        dfexcelinvoice (DataFrame): The dataframe of ExcelInvoice.
        rawfiles_tpl (tuple): Tuple of raw files.

    Returns:
        list: A list of rawfiles_tpl sorted in the order they appear in the invoice.

    Raises:
        StructuredError: If rawfiles_tpl does not exist in all indexes of ExcelInvoice, or if there are unused raw data.
    """
    # Check for the existence of rawfiles_tpl specified as an index
    # Conversely, check that all rawfiles_tpl are present in the ExcelInvoice index
    dcttpl = {str(tpl[0].parent.name): tpl for tpl in rawfiles_tpl}  # Assuming terminal folder names are unique
    dir_setglob = set(dcttpl.keys())
    dir_set_invoice = set(dfexcelinvoice["data_folder"])
    if dir_setglob == dir_set_invoice:
        # Reorder rawfiles_tpl according to the order of appearance in the invoice
        return [dcttpl[d] for d in dfexcelinvoice["data_folder"]]
    if dir_setglob - dir_set_invoice:
        emsg = f"ERROR: unused raw data: {(dir_setglob-dir_set_invoice).pop()}"
        raise StructuredError(emsg)
    if dir_set_invoice - dir_setglob:
        emsg = f"ERROR: raw data not found: {(dir_set_invoice-dir_setglob).pop()}"
        raise StructuredError(emsg)

    emsg = "ERROR: unknown error"
    raise StructuredError(emsg)  # This line should never be reached


class InvoiceFile:
    """Represents an invoice file and provides utilities to read and overwrite it.

    Attributes:
        invoice_path (Path): Path to the invoice file.
        invoice_obj (dict): Dictionary representation of the invoice JSON file.

    Args:
        invoice_path (Path): The path to the invoice file.

    Raises:
        ValueError: If `invoice_obj` is not a dictionary.

    Example:
        # Usage
        invoice = InvoiceFile("invoice.json")
        invoice.invoice_obj["basic"]["dataName"] = "new_data_name"
        invoice.overwrite("invoice_new.json")
    """

    def __init__(self, invoice_path: Path):
        self.invoice_path = invoice_path
        self._invoice_obj = self.read()

    @property
    def invoice_obj(self) -> dict[str, Any]:
        """Gets the invoice object."""
        return self._invoice_obj

    @invoice_obj.setter
    def invoice_obj(self, value: dict[str, Any]) -> None:
        """Sets the invoice object."""
        if not isinstance(value, dict):
            emsg = "invoice_obj must be a dictionary"
            raise ValueError(emsg)
        self._invoice_obj = value

    def __getitem__(self, key: str) -> Any:
        return self._invoice_obj[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._invoice_obj[key] = value

    def __delitem__(self, key: str) -> None:
        del self._invoice_obj[key]

    def read(self, *, target_path: Path | None = None) -> dict:
        """Reads the content of the invoice file and returns it as a dictionary.

        Args:
            target_path (Optional[Path], optional): Path to the target invoice file. If not provided,
                uses the path from `self.invoice_path`. Defaults to None.

        Returns:
            dict: Dictionary representation of the invoice JSON file.
        """
        if target_path is None:
            target_path = self.invoice_path

        self.invoice_obj = readf_json(target_path)
        return self.invoice_obj

    def overwrite(self, dst_file_path: Path, *, src_obj: Path | None = None) -> None:
        """Overwrites the contents of the destination file with the invoice JSON data.

        Args:
            dst_file_path (Path): The path to the destination file.
            src_obj (Optional[Path], optional): The path to the source object. Defaults to None.

        Raises:
            StructuredError: If the destination file does not exist.

        Example:
            # Usage
            invoice = InvoiceFile("invoice.json")
            invoice.invoice_obj["basic"]["dataName"] = "new_data_name"
            invoice.overwrite("invoice_new.json")

        """
        if src_obj is None:
            src_obj = self.invoice_path
        parent_dir = os.path.dirname(dst_file_path)
        os.makedirs(parent_dir, exist_ok=True)
        writef_json(dst_file_path, self.invoice_obj)

    @classmethod
    def copy_original_invoice(cls, src_file_path: Path, dst_file_path: Path) -> None:
        """Copies the original invoice file from the source file path to the destination file path.

        Args:
            src_file_path (Path): The source file path of the original invoice file.
            dst_file_path (Path): The destination file path where the original invoice file will be copied to.

        Raises:
            StructuredError: If the source file path does not exist.

        Returns:
            None
        """
        if not os.path.exists(src_file_path):
            emsg = f"File Not Found: {src_file_path}"
            raise StructuredError(emsg)
        if src_file_path != dst_file_path:
            shutil.copy(str(src_file_path), str(dst_file_path))


class ExcelInvoiceFile:
    """Class representing an invoice file in Excel format. Provides utilities for reading and overwriting the invoice file.

    Attributes:
        invoice_path (Path): Path to the invoice file.
        dfexcelinvoice (pd.DataFrame): Dataframe of the invoice.
        df_general (pd.DataFrame): Dataframe of general data.
        df_specific (pd.DataFrame): Dataframe of specific data.
    """

    def __init__(self, invoice_path: Path):
        self.invoice_path = invoice_path
        self.dfexcelinvoice, self.df_general, self.df_specific = self.read()

    def read(self, *, target_path: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Reads the content of the Excel invoice file and returns it as three dataframes.

        Args:
            target_path (Optional[Path], optional): Path to the invoice file to be read. If not provided,
                uses the path from `self.invoice_path`. Defaults to None.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Three dataframes (dfexcelinvoice, df_general, df_specific).

        Raises:
            StructuredError: If the invoice file is not found, or if multiple sheets exist in the invoice list files,
            or if no sheet is present in the invoice list files.
        """
        if target_path is None:
            target_path = self.invoice_path

        if not os.path.exists(target_path):
            emsg = f"ERROR: excelinvoice not found {target_path}"
            raise StructuredError(emsg)

        dct_sheets = pd.read_excel(target_path, sheet_name=None, dtype=str, header=None, index_col=None)

        dfexcelinvoice, df_general, df_specific = None, None, None
        for sh_name, df in dct_sheets.items():
            if df.empty:
                continue

            target_comment_value = df.iat[0, 0]
            if target_comment_value == "invoiceList_format_id":
                if dfexcelinvoice is not None:
                    emsg = "ERROR: multiple sheet in invoiceList files"
                    raise StructuredError(emsg)
                ExcelInvoiceFile.check_intermittent_empty_rows(df)
                dfexcelinvoice = self._process_invoice_sheet(df)
            elif sh_name == "generalTerm":
                df_general = self._process_general_term_sheet(df)
            elif sh_name == "specificTerm":
                df_specific = self._process_specific_term_sheet(df)

        if dfexcelinvoice is None:
            emsg = "ERROR: no sheet in invoiceList files"
            raise StructuredError(emsg)

        return dfexcelinvoice, df_general, df_specific

    def _process_invoice_sheet(self, df: pd.DataFrame) -> pd.Series:
        df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
        hd1 = list(df.iloc[1, :].fillna(""))
        hd2 = list(df.iloc[2, :].fillna(""))
        df.columns = [f"{s1}/{s2}" if s1 else s2 for s1, s2 in zip(hd1, hd2)]
        return df.iloc[4:, :].reset_index(drop=True).copy()

    def _process_general_term_sheet(self, df: pd.DataFrame) -> pd.Series:
        _df_general = df[1:].copy()
        _df_general.columns = ["term_id", "key_name"]
        return _df_general

    def _process_specific_term_sheet(self, df: pd.DataFrame) -> pd.Series:
        _df_specific = df[1:].copy()
        _df_specific.columns = ["sample_class_id", "term_id", "key_name"]
        return _df_specific

    def overwrite(self, invoice_org: Path, dist_path: Path, invoice_schema_path: Path, idx: int) -> None:
        """Overwrites the content of the original invoice file based on the data from the Excel invoice and saves it as a new file.

        Args:
            invoice_org (Path): Path to the original invoice file.
            dist_path (Path): Path to where the overwritten invoice file will be saved.
            invoice_schema_path (Path): Path to the invoice schema.
            idx (int): Index of the target row in the invoice dataframe.
        """
        invoice_schema_obj = readf_json(invoice_schema_path)
        invoice_obj = readf_json(invoice_org)

        # excelインボイスの値が空欄の場合に、オリジナルの値が入らないように初期化。
        # このバージョンのエクセルインボイスではタグ、関連試料は対応しない。
        for key, value in invoice_obj.items():
            if key == "sample":
                self._initialize_sample(value)
            else:
                self._initialize_non_sample(key, value)

        for k, valstr in self.dfexcelinvoice.iloc[idx, :].dropna().items():
            self._assign_value_to_invoice(k, valstr, invoice_obj, invoice_schema_obj)

        self._ensure_sample_id_order(invoice_obj)

        writef_json(dist_path, invoice_obj, enc="utf_8")

    @staticmethod
    def check_intermittent_empty_rows(df: pd.DataFrame) -> None:
        """Function to detect if there are empty rows between data rows in the ExcelInvoice (in DataFrame format).

        If an empty row exists, an exception is raised.

        Args:
            df (pd.DataFrame): Information of Sheet 1 of ExcelInvoice.

        Raises:
            StructuredError: An exception is raised if an empty row exists.
        """
        for i, row in df.iterrows():
            if not ExcelInvoiceFile.__is_empty_row(row):
                continue
            if any(not ExcelInvoiceFile.__is_empty_row(r) for r in df.iloc[i + 1]):
                emsg = "Error! Blank lines exist between lines"
                raise StructuredError(emsg)

    @staticmethod
    def __is_empty_row(row: pd.Series) -> bool:
        return all(cell == "" or pd.isnull(cell) for cell in row)

    def _assign_value_to_invoice(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        assign_funcs: dict[str, Callable[[str, str, dict[Any, Any], dict[Any, Any]], None]] = {
            "basic/": self._assign_basic,
            "sample/": self._assign_sample,
            "sample.general/": self._assign_sample_general,
            "sample.specific/": self._assign_sample_specific,
            "custom/": self._assign_custom,
        }

        for prefix, func in assign_funcs.items():
            if key.startswith(prefix):
                func(key, value, invoice_obj, schema_obj)
                break

    def _assign_basic(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("basic/", "")
        _assign_invoice_val(invoice_obj, "basic", cval, value, schema_obj)

    def _assign_sample(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("sample/", "")
        if cval == "names":
            _assign_invoice_val(invoice_obj, "sample", cval, [value], schema_obj)
        else:
            _assign_invoice_val(invoice_obj, "sample", cval, value, schema_obj)

    def _assign_sample_general(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("sample.general/", "sample.general.")
        term_id = self.df_general[self.df_general["key_name"] == cval]["term_id"].values[0]
        for dictobj in invoice_obj["sample"]["generalAttributes"]:
            if dictobj.get("termId") == term_id:
                dictobj["value"] = value
                break

    def _assign_sample_specific(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("sample.specific/", "sample.specific.")
        term_id = self.df_specific[self.df_specific["key_name"] == cval]["term_id"].values[0]
        for dictobj in invoice_obj["sample"]["specificAttributes"]:
            if dictobj.get("termId") == term_id:
                dictobj["value"] = value
                break

    def _assign_custom(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("custom/", "")
        _assign_invoice_val(invoice_obj, "custom", cval, value, schema_obj)

    def _ensure_sample_id_order(self, invoice_obj: dict) -> None:
        sample_info_value = invoice_obj.get("sample")
        if sample_info_value is None:
            return
        if "sampleId" not in sample_info_value:
            return

        sampleid_value = invoice_obj["sample"].pop("sampleId")
        invoice_obj["sample"] = {"sampleId": sampleid_value, **invoice_obj["sample"]}

    def _initialize_sample(self, sample_obj: Any) -> None:
        for item, val in sample_obj.items():
            if item in ["sampleId", "composition", "referenceUrl", "description", "ownerId"]:
                sample_obj[item] = None
            elif item in ["generalAttributes", "specificAttributes"]:
                for attribute in val:
                    attribute["value"] = None

    def _initialize_non_sample(self, key: str, value: Any) -> None:
        if key not in ["datasetId", "sample"]:
            for item in value:
                if item not in ["dateSubmitted", "instrumentId"]:
                    value[item] = None


def backup_invoice_json_files(excel_invoice_file: Path | None, mode: str | None) -> Path:
    """Backs up invoice files and retrieves paths based on the mode specified in the input.

    For excelinvoice and rdeformat modes, it backs up invoice.json as the original file in the temp directory in MultiDataTile mode.
    For other modes, it treats the files in the invoice directory as the original files.
    After backing up, it returns the file paths for invoice_org.json and invoice.schema.json.

    Args:
        excel_invoice_file (Optional[Path]): File path for excelinvoice mode
        mode (str): mode flags

    Returns:
        tuple[Path, Path]: File paths for invoice.json and invoice.schema.json
    """
    if mode is None:
        mode = ""
    invoice_org_filepath = StorageDir.get_specific_outputdir(False, "invoice").joinpath("invoice.json")
    if (excel_invoice_file is not None) or (mode is not None and mode.lower() in ["rdeformat", "multidatatile"]):
        invoice_org_filepath = StorageDir.get_specific_outputdir(True, "temp").joinpath("invoice_org.json")
        shutil.copy(StorageDir.get_specific_outputdir(False, "invoice").joinpath("invoice.json"), invoice_org_filepath)
    # elif mode is not None and mode.lower() in ["rdeformat", "multidatatile"]:
    #     invoice_org_filepath = StorageDir.get_specific_outputdir(True, "temp").joinpath("invoice_org.json")
    #     shutil.copy(StorageDir.get_specific_outputdir(False, "invoice").joinpath("invoice.json"), invoice_org_filepath)

    return invoice_org_filepath


def __serch_key_from_constant_variable_obj(key: str, metadata_json_obj: dict) -> dict | None:
    if key in metadata_json_obj["constant"]:
        return metadata_json_obj["constant"]
    if metadata_json_obj.get("variable"):
        _variable = metadata_json_obj["variable"]
        if len(_variable) > 0:
            return metadata_json_obj["variable"][0]
        return None
    return None


def update_description_with_features(
    rde_resource: RdeOutputResourcePath,
    dst_invoice_json: Path,
    metadata_def_json: Path,
) -> None:
    """Writes the provided features to the description field RDE.

    This function takes a dictionary of features and formats them to be written
    into the description field(to invoice.json)

    Args:
        rde_resource (RdeOutputResourcePath): Path object containing resource paths needed for RDE processing.
        dst_invoice_json (Path): Path to the invoice.json file where the features will be written.
        metadata_def_json (Path): Path to the metadata list JSON file, which may include definitions or schema information.

    Returns:
        None: The function does not return a value but writes the features to the invoice.json file in the description field.
    """
    with open(dst_invoice_json, "rb") as dst_invoice:
        enc_dst_invoice_data = dst_invoice.read()
    enc = chardet.detect(enc_dst_invoice_data)["encoding"]
    with open(dst_invoice_json, encoding=enc) as f:
        invoice_obj = json.load(f)

    with open(rde_resource.invoice_schema_json, "rb") as rde_resource_invoice_schema:
        enc_rde_invoice_schema_data = rde_resource_invoice_schema.read()
    enc = chardet.detect(enc_rde_invoice_schema_data)["encoding"]
    with open(rde_resource.invoice_schema_json, encoding=enc) as f:
        invoice_schema_obj = json.load(f)

    with open(metadata_def_json, "rb") as metadata_def_json_f:
        enc_rde_invoice_schema_data = metadata_def_json_f.read()
    enc = chardet.detect(enc_rde_invoice_schema_data)["encoding"]
    with open(metadata_def_json, encoding=enc) as f:
        metadata_def_obj = json.load(f)

    with open(rde_resource.meta.joinpath("metadata.json"), encoding=enc) as f:
        metadata_json_obj = json.load(f)

    description = invoice_obj["basic"]["description"] if invoice_obj["basic"]["description"] else ""
    for key, value in metadata_def_obj.items():
        if not value.get("_feature"):
            continue

        dscheader = __serch_key_from_constant_variable_obj(key, metadata_json_obj)
        if dscheader is None:
            continue
        if dscheader.get(key) is None:
            continue

        if value.get("unit"):
            description += f"\n{metadata_def_obj[key]['name']['ja']}({metadata_def_obj[key]['unit']}):{dscheader[key]['value']}"
        else:
            description += f"\n{metadata_def_obj[key]['name']['ja']}:{dscheader[key]['value']}"

        if description.startswith("\n"):
            description = description[1:]

    _assign_invoice_val(invoice_obj, "basic", "description", description, invoice_schema_obj)
    writef_json(dst_invoice_json, invoice_obj)


class RuleBasedReplacer:
    """A class for changing the rules of data naming.

    This class is used to manage and apply file name mapping rules. It reads rules from a JSON format
    rule file, sets rules, and performs file name transformations and replacements based on those rules.

    Attributes:
        rules (dict[str, str]): Dictionary holding the mapping rules.
        last_apply_result (dict[str, Any]): The result of the last applied rules.

    Args:
        rule_file_path (Optional[Union[str, Path]]): Path to the rule file. If specified, rules are loaded from this path.
    """

    def __init__(self, *, rule_file_path: str | Path | None = None):
        self.rules: dict[str, str] = {}
        self.last_apply_result: dict[str, Any] = {}

        if isinstance(rule_file_path, str):
            rule_file_path = Path(rule_file_path)
        if rule_file_path and rule_file_path.exists():
            self.load_rules(rule_file_path)

    def load_rules(self, filepath: str | Path) -> None:
        """Function to read file mapping rules.

        The file containing the mapping rules must be in JSON format.

        Args:
            filepath (Union[str, Path]): The file path of the JSON file containing the mapping rules.

        Raises:
            StructuredError: An exception is raised if the file extension is not json.
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)
        if filepath.suffix != ".json":
            emsg = f"Error. File format/extension is not correct: {filepath}"
            raise StructuredError(emsg)

        data = readf_json(filepath)
        self.rules = data.get("filename_mapping", {})

    def get_apply_rules_obj(
        self,
        replacements: dict[str, Any],
        source_json_obj: dict[str, Any] | None,
        *,
        mapping_rules: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Function to convert file mapping rules into a JSON format.

        This function takes string mappings separated by dots ('.') and converts them into a dictionary format, making it easier to handle within a target JsonObject.

        Args:
            replacements (dict[str, str]): The object containing mapping rules.
            source_json_obj (Optional[dict[str, Any]]): Objects of key and value to which you want to apply the rule
            mapping_rules (Optional[dict[str, str]], optional): Rules for mapping key and value. Defaults to None.

        Returns:
            dict[str, Any]: dictionary type data after conversion

        Example:
            # rule.json
            rule = {
                "filename_mapping": {
                    "invoice.basic.dataName": "${filename}",
                    "invoice.sample.names": ["${somedataname}"],
                }
            }
            replacer = RuleBasedReplacer('rules.json')
            replacements = {
                '${filename}': 'example.txt',
                '${somedataname}': ['some data']
            }
            result = replacer.apply_rules(replacement_rule, save_file_path, mapping_rules = rule)
            print(result)
        """
        # [TODO] Correction of type definitions in version 0.1.6
        if mapping_rules is None:
            mapping_rules = self.rules
        if source_json_obj is None:
            source_json_obj = {}

        for key, value in self.rules.items():
            keys = key.split(".")
            replace_value = replacements.get(value, "")
            current_obj: dict[str, Any] = source_json_obj
            for k in keys[:-1]:
                # search for the desired key in the dictionary from "xxx.xxx.xxx" ...
                if k not in current_obj:
                    current_obj[k] = {}
                current_obj = current_obj[k]
            current_obj[keys[-1]] = replace_value

        self.last_apply_result = source_json_obj

        return self.last_apply_result

    def set_rule(self, path: str, variable: str) -> None:
        """Sets a new rule.

        Args:
            path (str): The path to the target location for replacement.
            variable (str): The rule after replacement.

        Example:
            replacer = RuleBasedReplacer()
            replacer.set_rule('invoice.basic.dataName', 'filename')
            replacer.set_rule('invoice.sample.name', 'dataname')
            print(replacer.rules)
        """
        self.rules[path] = variable

    def write_rule(self, replacements_rule: dict[str, Any], save_file_path: str | Path) -> str:
        """Function to write file mapping rules to a target JSON file.

        Writes the set mapping rules (in JSON format) to the target file

        Args:
            replacements_rule (dict[str, str]): The object containing mapping rules.
            save_file_path (Union[str, Path]): The file path for saving.

        Raises:
            StructuredError: An exception error occurs if the extension of the save path is not .json.
            StructuredError: An exception error occurs if values cannot be written to the json.

        Returns:
            str: The result of writing to the target JSON.
        """
        contents: str = ""

        if isinstance(save_file_path, str):
            save_file_path = Path(save_file_path)

        if save_file_path.suffix != ".json":
            emsg = f"Extension error. Incorrect extension: {save_file_path}"
            raise StructuredError(emsg)

        if save_file_path.exists():
            exists_contents = readf_json(save_file_path)
            _ = self.get_apply_rules_obj(replacements_rule, exists_contents)
            data_to_write = copy.deepcopy(exists_contents)
        else:
            new_contents: dict[str, Any] = {}
            _ = self.get_apply_rules_obj(replacements_rule, new_contents)
            data_to_write = copy.deepcopy(new_contents)
            enc = "utf-8"

        try:
            with open(save_file_path, mode="w", encoding=enc) as f:
                json.dump(data_to_write, f, indent=4, ensure_ascii=False)
                contents = json.dumps({"filename_mapping": self.rules})
        except json.JSONDecodeError as json_err:
            emsg = "Error. No write was performed on the target json"
            raise StructuredError(emsg) from json_err

        return contents


def apply_default_filename_mapping_rule(replacement_rule: dict[str, Any], save_file_path: str | Path) -> dict[str, Any]:
    """Applies a default filename mapping rule based on the basename of the save file path.

    This function creates an instance of RuleBasedReplacer and applies a default mapping rule. If the basename
    of the save file path is 'invoice', it sets a specific rule for 'basic.dataName'. After setting the rule,
    it writes the mapping rule to the specified file path and returns the result of the last applied rules.

    Args:
        replacement_rule (dict[str, Any]): The replacement rules to be applied.
        save_file_path (Union[str, Path]): The file path where the replacement rules are saved.

    Returns:
        dict[str, Any]: The result of the last applied replacement rules.

    The function assumes the existence of certain structures in the replacement rules and file paths, and it
    specifically checks for a basename of 'invoice' to apply a predefined rule.
    """
    if isinstance(save_file_path, str):
        basename = os.path.splitext(os.path.basename(save_file_path))[0]
    elif isinstance(save_file_path, Path):
        basename = save_file_path.stem

    replacer = RuleBasedReplacer()
    if basename == "invoice":
        replacer.set_rule("basic.dataName", "${filename}")
    replacer.write_rule(replacement_rule, save_file_path)

    return replacer.last_apply_result


def apply_magic_variable(invoice_path: str | Path, rawfile_path: str | Path, *, save_filepath: str | Path | None = None) -> dict[str, Any]:
    """Converts the magic variable ${filename}.

    If ${filename} is present in basic.dataName of invoice.json, it is replaced with the filename of rawfile_path.

    Args:
        invoice_path (Union[str, Path]): The file path of invoice.json.
        rawfile_path (Union[str, Path]): The file path of the input data.
        save_filepath (Optional[Union[str, Path]], optional): The file path to save to. Defaults to None.

    Returns:
        dict[str, Any]: The content of invoice.json after replacement.
    """
    contents: dict[str, Any] = {}
    if isinstance(invoice_path, str):
        invoice_path = Path(invoice_path)
    if isinstance(rawfile_path, str):
        rawfile_path = Path(rawfile_path)
    if save_filepath is None:
        save_filepath = invoice_path

    invoice_contents = readf_json(invoice_path)
    if invoice_contents.get("basic", {}).get("dataName") == "${filename}":
        replacement_rule = {"${filename}": str(rawfile_path.name)}
        contents = apply_default_filename_mapping_rule(replacement_rule, save_filepath)

    return contents
