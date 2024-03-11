# ---------------------------------------------------------
# Copyright (c) 2024, Materials Data Platform, NIMS
#
# This software is released under the MIT License.
# ---------------------------------------------------------
# coding: utf-8
import csv
import json
import os
import pathlib
import re
import zipfile
from copy import deepcopy
from typing import Any, Optional, TypedDict, Union, cast

import chardet  # for following failure cases
import dateutil.parser
from charset_normalizer import detect

from rdetoolkit.exceptions import StructuredError, catch_exception_with_message
from rdetoolkit.models.rde2types import MetadataDefJson, MetaItem, MetaType, RdeFsPath, RepeatedMetaType, ValueUnitPair


class _ChardetType(TypedDict):
    encoding: str
    language: str
    confidence: float


def get_default_values(defaultValsFilePath):
    """Reads default values from a default_value.csv file and returns them as a dictionary.

    This function opens a file specified by 'defaultValsFilePath', detects its encoding,
    and reads its content as a CSV. Each row in the CSV file should have 'key' and 'value' columns.
    The function constructs and returns a dictionary mapping keys to their corresponding values.

    Args:
        defaultValsFilePath (str | Path): The file path to the CSV file containing default values.

    Returns:
        dict: A dictionary containing the keys and their corresponding default values.
    """
    dctDefaultVals = {}
    enc = chardet.detect(open(defaultValsFilePath, "rb").read())["encoding"]
    with open(defaultValsFilePath, encoding=enc) as fIn:
        for row in csv.DictReader(fIn):
            dctDefaultVals[row["key"]] = row["value"]
    return dctDefaultVals


def detect_text_file_encoding(text_filepath: RdeFsPath) -> str:
    """Detect the encoding of a given text file.

    This function attempts to detect the encoding of a text file. If the initially
    detected encoding isn't one of the usual ones, it uses chardet for a more thorough detection.

    Args:
        text_filepath (RdeFsPath): Path to the text file to be analyzed.

    Returns:
        str: The detected encoding of the text file.

    Raises:
        FileNotFoundError: If the given file path does not exist.
    """
    if isinstance(text_filepath, pathlib.Path):
        text_filepath = str(text_filepath)

    USUAL_ENC = ["ascii", "shift_jis", "utf_8", "utf_8_sig", "euc_jp"]
    byteAr = open(text_filepath, "rb").read()
    _cast_detect_ret: _ChardetType = cast(_ChardetType, detect(byteAr))
    if _cast_detect_ret["encoding"] is not None:
        enc = _cast_detect_ret["encoding"].replace("-", "_").lower()
    else:
        enc = ""

    if enc not in USUAL_ENC:
        ret = chardet.detect(byteAr)
        if ret["encoding"] is not None:
            enc = ret["encoding"].replace("-", "_").lower()
    if enc == "shift_jis":
        enc = "cp932"
    return enc


def _split_value_unit(tgtStr: str) -> ValueUnitPair:  # pragma: no cover
    """Split units and values from input characters.

    Args:
        tgtStr (str): String combining values and units

    Returns:
        ValueUnitPair: Result of splitting values and units
    """
    valpair = ValueUnitPair(value="", unit="")
    valLeft = str(tgtStr).strip()
    ptn1 = r"^[+-]?[0-9]*\.?[0-9]*"  # 実数部の正規表現
    ptn2 = r"[eE][+-]?[0-9]+"  # 指数部の正規表現
    r1 = re.match(ptn1, valLeft)
    if r1:
        _v = r1.group()
        valLeft = valLeft[r1.end() :]
        r2 = re.match(ptn2, valLeft)
        if r2:
            print(r2)
            _v += r2.group()
            valpair.value = _v
            valpair.unit = valLeft[r2.end() :]
        else:
            valpair.value = _v.strip()
            valpair.unit = valLeft.strip()
    else:
        valpair.unit = valLeft.strip()
    return valpair


def _decode_filename(info: zipfile.ZipInfo) -> None:  # pragma: no cover
    """Helper: Decode the file name of `ZipInfo` using Shift JIS (SJIS) encoding.

    Args:
        info (zipfile.ZipInfo): The `ZipInfo` object containing the file information.
    """
    LANG_ENC_FLAG = 0x800
    encoding = "utf_8" if info.flag_bits & LANG_ENC_FLAG else "cp437"
    info.filename = info.filename.encode(encoding).decode("cp932")


def unzip_japanese_zip(src_zipfilepath: str, dst_dirpath: str) -> None:
    """Extracts files from a ZIP archive considering Japanese file name encodings.

    This function handles ZIP archives that may have file names encoded with
    Japanese-specific encodings (like Shift JIS). It decodes the file names
    appropriately before extracting them to ensure they are correctly named
    in the destination directory.

    Args:
        src_zipfilepath (str): Path to the source ZIP file to be extracted.
        dst_dirpath (str): Destination directory path where the files should be extracted.
    """
    with zipfile.ZipFile(src_zipfilepath) as zfile:
        for zinfo in zfile.infolist():
            _decode_filename(zinfo)
            zfile.extract(zinfo, dst_dirpath)


def read_from_json_file(invoice_file_path: RdeFsPath) -> dict[str, Any]:  # pragma: no cover
    """A function that reads json file and returns the json object.

    Args:
        invoice_file_path (RdeFsPath): The path to the JSON file.

    Returns:
        dict[str, Any]: The parsed json object.
    """
    enc = detect_text_file_encoding(invoice_file_path)
    with open(invoice_file_path, encoding=enc) as f:
        invoiceObj = json.load(f)
    return invoiceObj


def write_to_json_file(invoiceFilePath: RdeFsPath, invoiceObj: dict[str, Any], enc: str = "utf_8"):  # pragma: no cover
    """Writes an content to a JSON file.

    Args:
        invoiceFilePath (RdeFsPath): Path to the destination JSON file.
        invoiceObj (dict[str, Any]): Invoice object to be serialized and written.
        enc (str): Encoding to use when writing the file. Defaults to "utf_8".
    """
    with open(invoiceFilePath, "w", encoding=enc) as f:
        json.dump(invoiceObj, f, indent=4, ensure_ascii=False)


class StorageDir:
    """A class to handle storage directory operations.

    It provides methods to generate and create
    directories for storing data, with support for dividing data into specific indexes.

    Attributes:
        __nDigit (int): The number of digits used for the divided data index. Fixed value.

    Note:
        In this system, the creation and support of the following folders are accommodated.
        Other folders can also be created, but they will not be reflected in the system:

        - invoice
        - invoice_patch
        - inputdata
        - invoice_patch
        - structured
        - temp
        - logs
        - meta
        - thumbnail
        - main_image
        - other_image
        - attachment
        - nonshared_raw
        - raw
        - tasksupport
    """

    __nDigit = 4  # 分割データインデックスの桁数。固定値

    @classmethod
    def get_datadir(cls, is_mkdir: bool, idx: int = 0):
        """Generates a data directory path based on an index and optionally creates it.

        This method generates a directory path under 'data' or 'data/divided' based on the provided index.
        If `is_mkdir` is True, the directory is created.

        Args:
            is_mkdir (bool): Flag to indicate whether to create the directory.
            idx (int): The index for the divided data. Default is 0, which refers to the base 'data' directory.

        Returns:
            str: The path of the generated data directory.
        """
        dir_basename = "data" if idx == 0 else os.path.join("data", "divided", f"{idx:0{cls.__nDigit}d}")
        if is_mkdir:
            os.makedirs(dir_basename, exist_ok=True)
        return dir_basename

    @classmethod
    def _make_data_basedir(cls, is_mkdir: bool, idx: int, dir_basename: str) -> pathlib.Path:
        """Creates and returns the path to a specified data base directory.

        This internal method is used to generate and optionally create a base directory for specific data types,
        such as 'invoice', 'logs', etc., under the data directory.

        Args:
            is_mkdir (bool): Flag to indicate whether to create the directory.
            idx (int): The index for the divided data.
            dir_basename (str): The base name of the directory to be created.

        Returns:
            pathlib.Path: The path of the created base directory.
        """
        target_dir = os.path.join(cls.get_datadir(is_mkdir, idx), dir_basename)
        if is_mkdir:
            os.makedirs(target_dir, exist_ok=True)
        return pathlib.Path(target_dir)

    @classmethod
    def get_specific_outputdir(cls, is_mkdir: bool, dir_basename: str, idx: int = 0):
        """Generates and optionally creates a specific output directory based on a base name and index.

        This method facilitates creating directories for specific outputs like 'invoice_patch', 'temp', etc.,
        within the structured data directories.

        Args:
            is_mkdir (bool): Flag to indicate whether to create the directory.
            dir_basename (str): The base name of the specific output directory.
            idx (int): The index for the divided data. Default is 0.

        Returns:
            pathlib.Path: The path of the specific output directory.
        """
        return cls._make_data_basedir(is_mkdir, idx, dir_basename)


class Meta:
    """This class initializes metadata from a definition file, with existing metadata loading not currently supported."""

    def __init__(
        self,
        metadef_filepath: RdeFsPath,
        *,
        metafilepath: Optional[RdeFsPath] = None,
    ):
        """Initializes the Meta class.

        This method supports either loading existing metadata (if `metafilepath` is specified)
        or creating new metadata (if `metaDefFilePath` is specified). Currently, the functionality
        to load existing metadata is not supported and will raise an error.

        Args:
            metadef_filepath (RdeFsPath): The file path for metadata definition, used for creating new metadata.
            metafilepath (Optional[RdeFsPath]): The file path for existing metadata, intended for future support
                                                in loading existing metadata. Currently not supported.

        Raises:
            StructuredError: If `metafilepath` is not None, as loading existing metadata is not supported yet.

        Note:
            The `metaDefFilterFunc` attribute is currently not in use and has been removed.

        Attributes:
            metaConst (dict[str, MetaItem]): A dictionary for constant metadata.
            metaVar (list[dict[str, MetaItem]]): A list of dictionaries for variable metadata.
            actions (list[str]): A list of actions.
            referedmap (dict[str, Optional[Union[str, list]]]): A dictionary mapping references.
            metaDef (dict[str, MetadataDefJson]): A dictionary for metadata definition, read from the metadata definition file.
        """
        self.metaConst: dict[str, MetaItem] = {}
        self.metaVar: list[dict[str, MetaItem]] = []
        self.actions: list[str] = []
        self.referedmap: dict[str, Optional[Union[str, list]]] = {}
        if metafilepath is not None:
            raise StructuredError("ERROR: not supported yet")
        self.metaDef: dict[str, MetadataDefJson] = self._read_metadef_file(metadef_filepath)

    def _read_metadef_file(self, metadef_filepath: RdeFsPath) -> dict[str, MetadataDefJson]:  # pragma: no cover
        """Reads the metadata definition file metadata-def.json.

        Args:
            metadef_filepath (RdeFsPath): The path of the metadata definition file.

        Returns:
            dict[str, MetadataDefJson]: Returns metadata-def.json as a dictionary.

        Caution:
            Unclear whether the processing of actions and units after l262 is currently necessary.
        """
        if metadef_filepath:
            enc = detect_text_file_encoding(metadef_filepath)
            with open(metadef_filepath, encoding=enc) as f:
                _tmp_metadef = json.load(f)
        else:
            _tmp_metadef = {}

        for _, vDef in _tmp_metadef.items():
            if vDef.get("action"):
                self.actions.append(vDef.get("action"))
            if vDef.get("unit"):
                outunit = vDef.get("unit")
                if not outunit.startswith("$"):
                    continue
                kRef = outunit[1:]
                self.referedmap[kRef] = None
        return _tmp_metadef

    def assignVals(
        self,
        entry_dict_meta: Union[MetaType, RepeatedMetaType],
        *,
        ignoreEmptyStrValue=True,
    ) -> "dict[str, set]":
        """Register the value of metadata.

        Perform validation and casting on the input metadata value in the specified format, and register it.
        The target format is validated using the key, format, and Unit specified in metadata-def.json.

        Args:
            entry_dict_meta (EntryMetaData): metadata(key/value) to register
            ignoreEmptyStrValue (bool, optional): When ignoreEmptyStrValue is True,
            even if the metadata value is an empty string, it is registered as a meta.
            However, if false, an empty string is not registered as a meta. Defaults to True.

        Raises:
            StructuredError: an exception is raised when the 'action' is included in the metadata-def.json.

        Returns:
            dict[str, set]: The key that could be registered as metadata is added to the object ret for storing the registration result.

        Caution!
        / Items with a metadata value of None to be registered are excluded from assignment.
        """
        ret = {"assigned": set()}  # type: ignore[var-annotated]

        # actionやrefered unit用に被参照値テーブルに登録(raw名)
        for kSrc, vSrc in entry_dict_meta.items():
            _vsrc = self.__convert_to_str(vSrc)
            self.__registerd_refered_table(kSrc, _vsrc)

        for kDef, vDef in self.metaDef.items():
            kSrc = kDef
            if kDef not in entry_dict_meta and "originalName" in vDef:
                kSrc = vDef["originalName"]
            if kSrc not in entry_dict_meta:
                continue

            vSrc = entry_dict_meta[kSrc]
            _vsrc = self.__convert_to_str(vSrc)

            if kDef:
                # actionやrefered unit用に被参照値テーブルに登録(meta名)
                self.__registerd_refered_table(kDef, _vsrc)

            action = vDef.get("action")
            if action:
                raise StructuredError("ERROR: this meta value should set by action")
            if vDef.get("variable"):
                self.__set_variable_metadata(kDef, _vsrc, vDef, ignoreEmptyStrValue)
            else:
                if vSrc is None:
                    continue
                if vSrc == "" and ignoreEmptyStrValue:
                    continue
                self.__set_const_metadata(kDef, _vsrc, vDef)
            ret["assigned"].add(kSrc)
            # 一つの値を複数個所に代入する可能性があるためbreakしない

        ret["unknown"] = {k for k in entry_dict_meta if k not in ret["assigned"]}
        return ret

    def _process_unit(self, vObj, idx):  # pragma: no cover
        strUnit = vObj.get("unit", "")
        # "unit"のうち、"$"から始まる他キー参照を実際に置き換える
        if strUnit.startswith("$"):
            srcKey = strUnit[1:]
            srcVal = self.referedmap[srcKey]
            if srcVal is None:
                # 参照先が存在しなかった場合は単位未設定の状態とする
                del vObj["unit"]
            elif isinstance(srcVal, str):
                vObj["unit"] = srcVal
            else:
                vObj["unit"] = srcVal[idx]

    def _process_action(self, vObj, k, idx):  # pragma: no cover
        # actionの処理
        strAct = self.metaDef[k].get("action")
        if not strAct:
            return

        for srcKey, srcVal in self.referedmap.items():
            if srcKey not in strAct:
                continue
            rVal = srcVal[idx] if isinstance(srcVal, list) else srcVal
            strAct = strAct.replace(srcKey, f'"{rVal}"' if isinstance(rVal, str) else str(rVal))
        vObj["value"] = eval(strAct)

    def __convert_to_str(self, value: Union[str, int, float, list]) -> Union[str, list[str]]:
        """Convert the given value to string or list of strings."""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, list):
            return list(map(str, value))
        return ""

    @catch_exception_with_message(error_message="ERROR: failed to generate metadata.json", error_code=50)
    def writeFile(self, metaFilePath, enc="utf_8"):
        """Writes the metadata to a file after processing units and actions.

        This method serializes the metadata into JSON format and writes it to the specified file.
        It processes units and actions for each metadata entry, sorts items according to 'metaDef',
        and outputs the sorted data to a file.

        The method also returns a list of keys from 'metaDef' that were not assigned values in the output.

        Args:
            metaFilePath (str): The file path where the metadata will be written.
            enc (str, optional): The encoding for the output file. Default is "utf_8".

        Returns:
            dict: A dictionary with keys 'assigned' and 'unknown'.
                'assigned' contains the set of keys that were assigned values,
                and 'unknown' contains the set of keys from 'metaDef' that were not used.

        Raises:
            CustomException: If the metadata generation fails, with a custom error message and error code.
        """
        outDict = json.loads(json.dumps({"constant": self.metaConst, "variable": self.metaVar}))

        for idx, kvDict in [(None, outDict["constant"])] + list(enumerate(outDict["variable"])):
            for k, vObj in kvDict.items():
                self._process_unit(vObj, idx)
                self._process_action(vObj, k, idx)

        # 項目をmetaDefに従ってソート
        outDict["constant"] = {k: outDict["constant"][k] for k in self.metaDef if k in outDict["constant"]}
        lvSort = []
        for dvOrg in outDict["variable"]:
            lvSort.append({k: dvOrg[k] for k in self.metaDef if k in dvOrg})
        outDict["variable"] = lvSort

        # ファイル出力
        with open(metaFilePath, "w", encoding=enc) as fOut:
            json.dump(outDict, fOut, indent=4, ensure_ascii=False)

        # metaDefのうち値の入らなかったキーのリストを返す
        ret = {"assigned": set(outDict["constant"].keys())}
        for dv in outDict["variable"]:
            ret["assigned"] = ret["assigned"].union(dv.keys())
        ret["unknown"] = {k for k in self.metaDef if k not in ret["assigned"]}

        return ret

    def __registerd_refered_table(self, key: str, value: Union[str, list[str]]) -> None:  # pragma: no cover
        """Registers the referenced value in the referred value table for actions and referred units, using the raw name.

        This method updates the referred value table with the provided key and value. If the key already exists in the table,
        its value is replaced. If the key does not exist and is found within any of the actions, it is added to the table.

        Args:
            key (str): The key to be registered in the referred value table. Typically represents an action or unit name.
            value (Union[str, list[str]]): The value to be registered in the referred value table. This can be a single string or a list of strings,
                representing the raw names to be associated with the key.

        Returns:
            None: This method does not return anything. It updates the referredmap attribute of the class.

        Note:
            This method is intended for internal use and not covered by automated testing (as indicated by 'pragma: no cover').
        """
        if key in self.referedmap:
            self.referedmap[key] = deepcopy(value)
        else:
            for strAct in self.actions:
                if key not in strAct:
                    continue
                self.referedmap[key] = deepcopy(value)

    def __set_variable_metadata(
        self,
        key: str,
        metavalues: Union[str, list[str]],
        metadefvalue: MetadataDefJson,
        opt_ignore_emptystr: bool,
    ) -> None:  # pragma: no cover
        outType = metadefvalue["schema"].get("type")
        outFmt = metadefvalue["schema"].get("format")
        orgType = metadefvalue.get("originalType")
        outUnit = metadefvalue.get("unit")
        if len(self.metaVar) < len(metavalues):
            self.metaVar += [{} for _ in range(len(metavalues) - len(self.metaVar))]
        for idx, vSrcElm in enumerate(metavalues):
            if vSrcElm is None:
                continue
            if vSrcElm == "" and opt_ignore_emptystr:
                continue
            self.metaVar[idx][key] = self._metadata_validation(vSrcElm, outType, outFmt, orgType, outUnit)

    def __set_const_metadata(
        self,
        key: str,
        metavalue: Union[str, list[str]],
        metadefvalue: MetadataDefJson,
    ) -> None:  # pragma: no cover
        outType = metadefvalue["schema"].get("type")
        outFmt = metadefvalue["schema"].get("format")
        orgType = metadefvalue.get("originalType")
        outUnit = metadefvalue.get("unit")
        if not isinstance(metavalue, list):
            self.metaConst[key] = self._metadata_validation(metavalue, outType, outFmt, orgType, outUnit)

    def _metadata_validation(
        self,
        vSrc: str,
        outType: Optional[str],
        outFmt: Optional[str],
        orgType: Optional[str],
        outUnit: Optional[str],
    ) -> "dict[str, Union[bool, int, float, str]]":  # pragma: no cover
        """Casts the input metadata to the specified format and performs validation to check.

        if it can be cast to the specified data type. The formats for various metadata are described in metadata-def.json.

        Args:
            vSrc (str): The value of the input metadata.
            outType (Optional[str]): The data type of the converted metadata.
            outFmt (Optional[str]): The format of the converted metadata.
            orgType (Optional[str]): The data type of the original metadata.
            outUnit (Optional[str]): The unit of the converted metadata.

        Returns:
            dict[str, Union[bool, int, float, str]]: Returns the conversion result in the form of metadata for metadata.json.

        Note:
            original func: _vDict()
        """
        vSrc = vSrc.strip()

        if orgType is None:
            _casted_value = self._cast_value(vSrc, outType, outFmt)
        elif orgType in ["integer", "number"]:
            # 単位付き文字列が渡されても単位の代入は本関数内では扱わない。必要に応じて別途代入する事。
            valpair = _split_value_unit(vSrc)
            vStr = valpair.value
            # 解釈可能かチェック。不可能だった場合は例外スローされるため、
            # 例外なく処理終了できるかのみに興味がある
            _casted_value = self._cast_value(vStr, orgType, outFmt)
        else:
            vStr = vSrc
            # 解釈可能かチェック。不可能だった場合は例外スローされるため、
            # 例外なく処理終了できるかのみに興味がある
            _casted_value = self._cast_value(vStr, orgType, outFmt)

        if outUnit:
            return {
                "value": _casted_value,
                "unit": outUnit,
            }
        else:
            return {"value": _casted_value}

    def _cast_value(self, valStr: str, outType: Optional[str], outFmt: Optional[str]) -> Union[bool, int, float, str]:  # pragma: no cover
        """The function formats the string valStr based on outType and outFmt and returns the formatted value.

        The function returns a formatted value of the string valStr according to
        the specified outType and outFmt. The outType must be a string ("string")
        for outFmt to be used. If valStr contains a value with units,
        the assignment of units is not handled within this function.
        It should be assigned separately as needed.

        Args:
            valStr (str): String to be converted of type
            outType (str): Type information at output
            outFmt (str): Formatting at output (related to date data)
        """

        def _tryCast(valStr, tp):
            try:
                return tp(valStr)
            except Exception:
                return None

        if outType == "boolean":
            if _tryCast(valStr, bool) is not None:
                return bool(valStr)
        elif outType == "integer":
            # 単位付き文字列が渡されても単位の代入は本関数内では扱わない。必要に応じて別途代入する事。
            val_unit_pair = _split_value_unit(valStr)
            if _tryCast(val_unit_pair.value, int) is not None:
                return int(val_unit_pair.value)
        elif outType == "number":
            # 単位付き文字列が渡されても単位の代入は本関数内では扱わない。必要に応じて別途代入する事。
            val_unit_pair = _split_value_unit(valStr)
            if _tryCast(val_unit_pair.value, int) is not None:
                return int(val_unit_pair.value)
            if _tryCast(val_unit_pair.value, float) is not None:
                return float(val_unit_pair.value)
        elif outType == "string":
            if not outFmt:
                return valStr
            elif outFmt == "date-time":
                # Do not discard timezone information if it is already attached.
                dtObj = dateutil.parser.parse(valStr)
                return dtObj.isoformat()
            elif outFmt == "date":
                # Do not discard timezone information if it is already attached.
                dtObj = dateutil.parser.parse(valStr)
                return dtObj.strftime("%Y-%m-%d")
            elif outFmt == "time":
                # Do not discard timezone information if it is already attached.
                dtObj = dateutil.parser.parse(valStr)
                return dtObj.strftime("%H:%M:%S")
            else:
                raise StructuredError("ERROR: unknown format in metaDef")
        else:
            raise StructuredError("ERROR: unknown value type in metaDef")
        raise StructuredError("ERROR: failed to cast metaDef value")


def castVal(valStr: str, outType: Optional[str], outFmt: Optional[str]) -> Union[bool, int, float, str]:
    """The function formats the string valStr based on outType and outFmt and returns the formatted value.

    The function returns a formatted value of the string valStr according to
    the specified outType and outFmt. The outType must be a string ("string")
    for outFmt to be used. If valStr contains a value with units,
    the assignment of units is not handled within this function.
    It should be assigned separately as needed.

    Args:
        valStr (str): String to be converted of type
        outType (str): Type information at output
        outFmt (str): Formatting at output (related to date data)
    """

    def _tryCast(valStr, tp):
        try:
            return tp(valStr)
        except Exception:
            return None

    if outType == "boolean":
        if _tryCast(valStr, bool) is not None:
            return bool(valStr)
    elif outType == "integer":
        # 単位付き文字列が渡されても単位の代入は本関数内では扱わない。必要に応じて別途代入する事。
        val_unit_pair = _split_value_unit(valStr)
        if _tryCast(val_unit_pair.value, int) is not None:
            return int(val_unit_pair.value)
    elif outType == "number":
        # 単位付き文字列が渡されても単位の代入は本関数内では扱わない。必要に応じて別途代入する事。
        val_unit_pair = _split_value_unit(valStr)
        if _tryCast(val_unit_pair.value, int) is not None:
            return int(val_unit_pair.value)
        if _tryCast(val_unit_pair.value, float) is not None:
            return float(val_unit_pair.value)
    elif outType == "string":
        if not outFmt:
            return valStr
        elif outFmt == "date-time":
            # Do not discard timezone information if it is already attached.
            dtObj = dateutil.parser.parse(valStr)
            return dtObj.isoformat()
        elif outFmt == "date":
            # Do not discard timezone information if it is already attached.
            dtObj = dateutil.parser.parse(valStr)
            return dtObj.strftime("%Y-%m-%d")
        elif outFmt == "time":
            # Do not discard timezone information if it is already attached.
            dtObj = dateutil.parser.parse(valStr)
            return dtObj.strftime("%H:%M:%S")
        else:
            raise StructuredError("ERROR: unknown format in metaDef")
    else:
        raise StructuredError("ERROR: unknown value type in metaDef")
    raise StructuredError("ERROR: failed to cast metaDef value")


def dict2meta(metadef_filepath: pathlib.Path, metaout_filepath: pathlib.Path, const_info: MetaType, val_info: MetaType) -> dict[str, set[Any]]:
    """Converts dictionary data into metadata and writes it to a specified file.

    This function takes metadata definitions and dictionary information for constants and variables,
    then creates a Meta object to process and write this data to a metadata output file.

    Args:
        metadef_filepath (pathlib.Path): The file path to the metadata definition file.
                                        This file defines the structure and expected types of the metadata.
        metaout_filepath (pathlib.Path): The file path where the processed metadata should be written.
        const_info (MetaType): A dictionary containing constant metadata information.
                                This should match the structure defined in the metadef_filepath.
        val_info (MetaType): A dictionary containing variable metadata information.
                            This too should align with the structure defined in the metadef_filepath.

    Returns:
        dict: A dictionary containing information about the assigned and unknown metadata fields.
                The 'assigned' key contains a set of fields that were successfully assigned values,
                while the 'unknown' key contains a set of fields defined in the metadata definition but not present in the input dictionaries.

    Note:
        MetaType is expected to be a dictionary or a similar structure containing metadata information.
    """
    metaObj = Meta(metadef_filepath)
    metaObj.assignVals(const_info)
    metaObj.assignVals(val_info)

    ret = metaObj.writeFile(metaout_filepath)
    return ret
