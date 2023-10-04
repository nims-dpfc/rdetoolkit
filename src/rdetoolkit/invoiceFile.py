# ---------------------------------------------------------
# Copyright (c) 2022, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
#
# Contributor:
#     Hiroko Nagao
#    Hiroshi Shinotsuka
# ---------------------------------------------------------
# coding: utf-8

import json
import os
import shutil
from pathlib import Path
from typing import Any, Callable, Optional

import chardet
import pandas as pd

from rdetoolkit import rde2util
from rdetoolkit.rde2util import StorageDir
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import RdeOutputResourcePath, RdeFormatFlags


def readExcelInvoice(excelInvoiceFilePath):
    dctSheets = pd.read_excel(excelInvoiceFilePath, sheet_name=None, dtype=str, header=None, index_col=None)
    dfExcelInvoice = None
    dfGeneral = None
    dfSpecific = None
    for shName, df in dctSheets.items():
        if df.iat[0, 0] == "invoiceList_format_id":
            if dfExcelInvoice is not None:
                raise StructuredError("ERROR: multiple sheet in invoiceList files")
            df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
            hd1 = list(df.iloc[1, :].fillna(""))
            hd2 = list(df.iloc[2, :].fillna(""))
            df.columns = [f"{s1}/{s2}" if s1 else s2 for s1, s2 in zip(hd1, hd2)]
            dfExcelInvoice = df.iloc[4:, :].reset_index(drop=True).copy()
        elif shName == "generalTerm":
            dfGeneral = df[1:].copy()
            dfGeneral.columns = ["term_id", "key_name"]
        elif shName == "specificTerm":
            dfSpecific = df[1:].copy()
            dfSpecific.columns = ["sample_class_id", "term_id", "key_name"]
        else:
            pass

    if dfExcelInvoice is None:
        raise StructuredError("ERROR: no sheet in invoiceList files")
    return dfExcelInvoice, dfGeneral, dfSpecific


def checkExistRawFiles(dfExcelInvoice, excelRawFiles):
    # インデックスとして指定されたrawFilePathの存在チェック
    # 逆に、rawFileListがExcelInvoiceのincdexに全て存在している事をチェック
    fileSetGlob = set([f.name for f in excelRawFiles])
    fileSetInvoice = set(dfExcelInvoice["data_file_names/name"])
    if fileSetGlob == fileSetInvoice:
        # excelRawFilesを、インボイス出現順に並び替える
        dctTmp = {f.name: f for f in excelRawFiles}
        return [dctTmp[f] for f in dfExcelInvoice["data_file_names/name"]]
    elif fileSetGlob - fileSetInvoice:
        raise StructuredError(f"ERROR: unused raw file: {(fileSetGlob-fileSetInvoice).pop()}")
    elif fileSetInvoice - fileSetGlob:
        raise StructuredError(f"ERROR: raw file not found: {(fileSetInvoice-fileSetGlob).pop()}")
    raise StructuredError("ERROR: unknown error")  # ここには来ない


def _assignInvoiceVal(invoiceObj, key1, key2, valObj, invoiceSchemaObj):
    """
    代入先の先頭であるkeys1が"custom"の時、valObjはinvoiceSchemaObjに従ってキャストされる。それ以外の場合はvalObjの型をそのまま変更せずに代入する
    """
    if key1 == "custom":
        dctSchema = invoiceSchemaObj["properties"][key1]["properties"][key2]
        try:
            invoiceObj[key1][key2] = rde2util.castVal(valObj, dctSchema["type"], dctSchema.get("format"))
        except rde2util._CastError:
            raise StructuredError(f"ERROR: failed to cast invoice value for key [{key1}][{key2}]")
    else:
        invoiceObj[key1][key2] = valObj


def overwriteInvoiceFileforDPFTerm(invoiceObj, invoiceDstFilePath, invoiceSchemaFilePath, invoiceInfo):
    enc = chardet.detect(open(invoiceSchemaFilePath, "rb").read())["encoding"]
    with open(invoiceSchemaFilePath, encoding=enc) as f:
        invoiceSchemaObj = json.load(f)
    for k, v in invoiceInfo.items():
        _assignInvoiceVal(invoiceObj, "custom", k, v, invoiceSchemaObj)
    with open(invoiceDstFilePath, "w", encoding=enc) as fOut:
        json.dump(invoiceObj, fOut, indent=4, ensure_ascii=False)


def checkExistRawFiles_for_folder(dfExcelInvoice, rawFilesTpl):
    # インデックスとして指定されたrawFilesTplの存在チェック
    # 逆に、rawFilesTplがExcelInvoiceのincdexに全て存在している事をチェック
    dctTpl = {str(tpl[0].parent.name): tpl for tpl in rawFilesTpl}  # 末端フォルダ名は一意であると想定
    dirSetGlob = set(dctTpl.keys())
    dirSetInvoice = set(dfExcelInvoice["data_folder"])
    if dirSetGlob == dirSetInvoice:
        # rawFilesTplを、インボイス出現順に並び替える
        return [dctTpl[d] for d in dfExcelInvoice["data_folder"]]
    elif dirSetGlob - dirSetInvoice:
        raise StructuredError(f"ERROR: unused raw data: {(dirSetGlob-dirSetInvoice).pop()}")
    elif dirSetInvoice - dirSetGlob:
        raise StructuredError(f"ERROR: raw data not found: {(dirSetInvoice-dirSetGlob).pop()}")

    raise StructuredError("ERROR: unknown error")  # ここには来ない


class InvoiceFile:
    """Represents an invoice file and provides utilities to read and overwrite it.

    Attributes:
        invoice_path (Path): Path to the invoice file.
        invoice_obj (dict): Dictionary representation of the invoice JSON file.

    Note:
        - The class uses an external utility `rde2util.detect_text_file_encoding` to detect the encoding of the file.
    """

    def __init__(self, invoice_path: Path):
        self.invoice_path = invoice_path
        self.invoice_obj = self.read()

    def read(self, *, target_path: Optional[Path] = None) -> dict:
        """Reads the content of the invoice file and returns it as a dictionary.

        Args:
            target_path (Optional[Path], optional): Path to the target invoice file. If not provided,
                uses the path from `self.invoice_path`. Defaults to None.

        Returns:
            dict: Dictionary representation of the invoice JSON file.
        """
        if target_path is None:
            target_path = self.invoice_path
        enc = rde2util.detect_text_file_encoding(target_path)
        with open(target_path, encoding=enc) as f:
            self.invoice_json = json.load(f)
        return self.invoice_json

    def overwrite(self, dist_file_path: Path, *, src_file_path: Optional[Path] = None):
        """Overwrites the destination file with the content of the source invoice file.

        Args:
            dist_file_path (Path): Path to the destination file to be overwritten.
            src_file_path (Optional[Path], optional): Path to the source invoice file. If not provided,
                uses the path from `self.invoice_path`. Defaults to None.

        Raises:
            StructuredError: If the source file is not found.
        """
        if src_file_path is None:
            src_file_path = self.invoice_path
        if not os.path.exists(src_file_path):
            raise StructuredError(f"File Not Found: {src_file_path}")
        if src_file_path != dist_file_path:
            shutil.copy(str(src_file_path), str(dist_file_path))


class ExcelInvoiceFile:
    """Class representing an invoice file in Excel format. Provides utilities for reading and overwriting the invoice file.

    Attributes:
        invoice_path (Path): Path to the invoice file.
        dfExcelInvoice (pd.DataFrame): Dataframe of the invoice.
        dfGeneral (pd.DataFrame): Dataframe of general data.
        dfSpecific (pd.DataFrame): Dataframe of specific data.
    """

    def __init__(self, invoice_path: Path):
        self.invoice_path = invoice_path
        self.dfExcelInvoice, self.dfGeneral, self.dfSpecific = self.read()

    def read(self, *, target_path: Optional[Path] = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Reads the content of the Excel invoice file and returns it as three dataframes.

        Args:
            target_path (Optional[Path], optional): Path to the invoice file to be read. If not provided,
                uses the path from `self.invoice_path`. Defaults to None.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Three dataframes (dfExcelInvoice, dfGeneral, dfSpecific).

        Raises:
            StructuredError: If the invoice file is not found, or if multiple sheets exist in the invoice list files,
            or if no sheet is present in the invoice list files.
        """
        if target_path is None:
            target_path = self.invoice_path

        if not os.path.exists(target_path):
            raise StructuredError(f"ERROR: excelinvoice not found {target_path}")

        dctSheets = pd.read_excel(target_path, sheet_name=None, dtype=str, header=None, index_col=None)

        dfExcelInvoice = None
        dfGeneral = None
        dfSpecific = None
        for shName, df in dctSheets.items():
            if df.iat[0, 0] == "invoiceList_format_id":
                if dfExcelInvoice is not None:
                    raise StructuredError("ERROR: multiple sheet in invoiceList files")
                df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
                hd1 = list(df.iloc[1, :].fillna(""))
                hd2 = list(df.iloc[2, :].fillna(""))
                df.columns = [f"{s1}/{s2}" if s1 else s2 for s1, s2 in zip(hd1, hd2)]
                dfExcelInvoice = df.iloc[4:, :].reset_index(drop=True).copy()
            elif shName == "generalTerm":
                dfGeneral = df[1:].copy()
                dfGeneral.columns = ["term_id", "key_name"]
            elif shName == "specificTerm":
                dfSpecific = df[1:].copy()
                dfSpecific.columns = ["sample_class_id", "term_id", "key_name"]
            else:
                pass

        if dfExcelInvoice is None:
            raise StructuredError("ERROR: no sheet in invoiceList files")

        return dfExcelInvoice, dfGeneral, dfSpecific

    def overwrite(self, invoice_org: Path, dist_path: Path, invoice_schema_path: Path, idx: int) -> None:
        """Overwrites the content of the original invoice file based on the data from the Excel invoice and saves it as a new file.

        Args:
            invoice_org (Path): Path to the original invoice file.
            dist_path (Path): Path to where the overwritten invoice file will be saved.
            invoice_schema_path (Path): Path to the invoice schema.
            idx (int): Index of the target row in the invoice dataframe.
        """

        invoice_schema_obj = self._load_json(invoice_schema_path)
        invoice_obj = self._load_json(invoice_org)

        # excelインボイスの値が空欄の場合に、オリジナルの値が入らないように初期化。
        # このバージョンのエクセルインボイスではタグ、関連試料は対応しない。
        for key, value in invoice_obj.items():
            if key == "sample":
                self._initialize_sample(value)
            else:
                self._initialize_non_sample(key, value)

        for k, valStr in self.dfExcelInvoice.iloc[idx, :].dropna().items():
            self._assign_value_to_invoice(k, valStr, invoice_obj, invoice_schema_obj)

        self._ensure_sample_id_order(invoice_obj)

        enc = self._detect_encoding(invoice_org)
        enc = "utf_8" if enc.lower() == "ascii" else enc
        self._write_json(dist_path, invoice_obj, enc)

    def _assign_value_to_invoice(self, key: str, value: str, invoice_obj: dict, schema_obj: dict):
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
        _assignInvoiceVal(invoice_obj, "basic", cval, value, schema_obj)

    def _assign_sample(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("sample/", "")
        if cval == "names":
            _assignInvoiceVal(invoice_obj, "sample", cval, [value], schema_obj)
        else:
            _assignInvoiceVal(invoice_obj, "sample", cval, value, schema_obj)

    def _assign_sample_general(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("sample.general/", "sample.general.")
        termID = self.dfGeneral[self.dfGeneral["key_name"] == cval]["term_id"].values[0]
        for dObj in invoice_obj["sample"]["generalAttributes"]:
            if dObj.get("termId") == termID:
                dObj["value"] = value
                break

    def _assign_sample_specific(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("sample.specific/", "sample.specific.")
        termID = self.dfSpecific[self.dfSpecific["key_name"] == cval]["term_id"].values[0]
        for dObj in invoice_obj["sample"]["specificAttributes"]:
            if dObj.get("termId") == termID:
                dObj["value"] = value
                break

    def _assign_custom(self, key: str, value: str, invoice_obj: dict, schema_obj: dict) -> None:
        cval = key.replace("custom/", "")
        _assignInvoiceVal(invoice_obj, "custom", cval, value, schema_obj)

    def _ensure_sample_id_order(sefl, invoice_obj: dict):
        sample_info_value = invoice_obj.get("sample")
        if sample_info_value is None:
            return
        if "sampleId" not in sample_info_value:
            return

        sampleId_value = invoice_obj["sample"].pop("sampleId")
        invoice_obj["sample"] = {"sampleId": sampleId_value, **invoice_obj["sample"]}

    def _detect_encoding(self, file_path: Path):
        return rde2util.detect_text_file_encoding(file_path)

    def _load_json(self, file_path: Path):
        enc = self._detect_encoding(file_path)
        with open(file_path, encoding=enc) as f:
            return json.load(f)

    def _write_json(self, file_path: Path, obj: Any, enc: str):
        with open(file_path, "w", encoding=enc) as f:
            json.dump(obj, f, indent=4, ensure_ascii=False)

    def _initialize_sample(self, sample_obj: Any):
        for item, val in sample_obj.items():
            if item in ["sampleId", "composition", "referenceUrl", "description", "ownerId"]:
                sample_obj[item] = None
            elif item in ["generalAttributes", "specificAttributes"]:
                for attribute in val:
                    attribute["value"] = None

    def _initialize_non_sample(self, key: str, value: Any):
        if key not in ["datasetId", "sample"]:
            for item in value:
                if item not in ["dateSubmitted", "instrumentId"]:
                    value[item] = None


def backup_invoice_json_files(excel_invoice_file: Optional[Path], fmt_flags: RdeFormatFlags) -> Path:
    """Backs up invoice files and retrieves paths based on the mode specified in the input.
    For excelinvoice and rdeformat modes, it backs up invoice.json as the original file in the temp directory in multifile mode.
    For other modes, it treats the files in the invoice directory as the original files.
    After backing up, it returns the file paths for invoice_org.json and invoice.schema.json.

    Args:
        excel_invoice_file (Optional[Path]): File path for excelinvoice mode
        fmt_flags (RdeFormatFlags): Object containing mode flags

    Returns:
        tuple[Path, Path]: File paths for invoice.json and invoice.schema.json
    """
    invoice_org_filepath = StorageDir.get_specific_outputdir(False, "invoice").joinpath("invoice.json")
    if excel_invoice_file is not None:
        invoice_org_filepath = StorageDir.get_specific_outputdir(True, "temp").joinpath("invoice_org.json")
        shutil.copy(
            StorageDir.get_specific_outputdir(False, "invoice").joinpath("invoice.json"),
            invoice_org_filepath
        )
    elif fmt_flags.is_rdeformat_enabled or fmt_flags.is_multifile_enabled:
        invoice_org_filepath = StorageDir.get_specific_outputdir(True, "temp").joinpath("invoice_org.json")
        shutil.copy(
            StorageDir.get_specific_outputdir(False, "invoice").joinpath("invoice.json"),
            invoice_org_filepath
        )

    return invoice_org_filepath


def update_description_with_features(
    rde_resource: RdeOutputResourcePath,
    dst_invoice_json: Path,
    metadata_def_json: Path,
):
    """Writes the provided features to the description field RDE
    This function takes a dictionary of features and formats them to be written
    into the description field(to invoice.json)

    Args:
        rde_resource (RdeOutputResourcePath): Path object containing resource paths needed for RDE processing.
        invoice_json (Path): Path to the invoice.json file where the features will be written.
        metadata_def_json (Path): Path to the metadata list JSON file, which may include definitions or schema information.

    Returns:
        None: The function does not return a value but writes the features to the invoice.json file in the description field.
    """
    enc = chardet.detect(open(dst_invoice_json, "rb").read())["encoding"]
    with open(dst_invoice_json, encoding=enc) as f:
        invoice_obj = json.load(f)

    enc = chardet.detect(open(rde_resource.invoice_schema_json, "rb").read())["encoding"]
    with open(rde_resource.invoice_schema_json, encoding=enc) as f:
        invoice_schema_obj = json.load(f)

    enc = chardet.detect(open(metadata_def_json, "rb").read())["encoding"]
    with open(metadata_def_json, encoding=enc) as f:
        metadata_def_obj = json.load(f)

    with open(rde_resource.meta.joinpath("metadata.json"), encoding=enc) as f:
        metadata_json_obj = json.load(f)

    if invoice_obj["basic"]["description"]:
        description = invoice_obj["basic"]["description"] + "\n"
    else:
        description = ""
    for key, value in metadata_def_obj.items():
        if not value.get("_feature"):
            continue

        if key in metadata_json_obj["constant"]:
            dscheader = metadata_json_obj["constant"]
        else:
            dscheader = metadata_json_obj["variable"][0]
        if value.get("unit"):
            description += f"{metadata_def_obj[key]['name']['ja']}({metadata_def_obj[key]['unit']}):{dscheader[key]['value']}\n"
        else:
            description += f"{metadata_def_obj[key]['name']['ja']}:{dscheader[key]['value']}\n"

    _assignInvoiceVal(invoice_obj, "basic", "description", description, invoice_schema_obj)
    rde2util.write_to_json_file(dst_invoice_json, invoice_obj)
