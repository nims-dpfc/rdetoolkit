import csv
import json
import os
import pathlib
import re
import zipfile
from copy import deepcopy
from typing import Any, Final, Optional, TypedDict, Union, cast

import chardet  # for following failure cases
import dateutil.parser
from chardet.universaldetector import UniversalDetector
from charset_normalizer import detect

from rdetoolkit.exceptions import StructuredError, catch_exception_with_message
from rdetoolkit.models.rde2types import MetadataDefJson, MetaItem, MetaType, RdeFsPath, RepeatedMetaType, ValueUnitPair

LANG_ENC_FLAG: Final[int] = 0x800


class _ChardetType(TypedDict):
    encoding: str
    language: str
    confidence: float


def get_default_values(default_values_filepath):
    """Reads default values from a default_value.csv file and returns them as a dictionary.

    This function opens a file specified by 'default_values_filepath', detects its encoding,
    and reads its content as a CSV. Each row in the CSV file should have 'key' and 'value' columns.
    The function constructs and returns a dictionary mapping keys to their corresponding values.

    Args:
        default_values_filepath (str | Path): The file path to the CSV file containing default values.

    Returns:
        dict: A dictionary containing the keys and their corresponding default values.
    """
    dct_default_values = {}
    with open(default_values_filepath, "rb") as rf:
        enc_default_values_data = rf.read()
    enc = chardet.detect(enc_default_values_data)["encoding"]
    with open(default_values_filepath, encoding=enc) as fin:
        for row in csv.DictReader(fin):
            dct_default_values[row["key"]] = row["value"]
    return dct_default_values


class CharDecEncoding:
    """A class to handle character encoding detection and conversion for text files."""

    USUAL_ENCs = ("ascii", "shift_jis", "utf_8", "utf_8_sig", "euc_jp")

    @classmethod
    def detect_text_file_encoding(cls, text_filepath: RdeFsPath) -> str:
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

        with open(text_filepath, "rb") as tf:
            bcontents = tf.read()
        _cast_detect_ret: _ChardetType = cast(_ChardetType, detect(bcontents))
        enc = _cast_detect_ret["encoding"].replace("-", "_").lower() if _cast_detect_ret["encoding"] is not None else ""

        if enc not in cls.USUAL_ENCs:
            enc = cls.__detect(text_filepath)
        if enc == "shift_jis":
            enc = "cp932"
        return enc

    @classmethod
    def __detect(cls, text_filepath: str) -> str:
        """Detect the encoding of a given text file using chardet.

        Args:
            text_filepath (str): Path to the text file to be analyzed.

        Returns:
            str: The detected encoding of the text file.
        """
        detector = UniversalDetector()

        try:
            with open(text_filepath, mode="rb") as f:
                while True:
                    binary = f.readline()
                    if binary == b"":
                        break
                    detector.feed(binary)
                    if detector.done:
                        break
        finally:
            detector.close()

        ret = detector.result["encoding"]
        if ret:
            return ret.replace("-", "_").lower()
        else:
            return ""


def _split_value_unit(target_char: str) -> ValueUnitPair:  # pragma: no cover
    """Split units and values from input characters.

    Args:
        target_char (str): String combining values and units

    Returns:
        ValueUnitPair: Result of splitting values and units
    """
    valpair = ValueUnitPair(value="", unit="")
    valleft = str(target_char).strip()
    ptn1 = r"^[+-]?[0-9]*\.?[0-9]*"  # 実数部の正規表現
    ptn2 = r"[eE][+-]?[0-9]+"  # 指数部の正規表現
    r1 = re.match(ptn1, valleft)
    if r1:
        _v = r1.group()
        valleft = valleft[r1.end() :]
        r2 = re.match(ptn2, valleft)
        if r2:
            _v += r2.group()
            valpair.value = _v
            valpair.unit = valleft[r2.end() :]
        else:
            valpair.value = _v.strip()
            valpair.unit = valleft.strip()
    else:
        valpair.unit = valleft.strip()
    return valpair


def _decode_filename(info: zipfile.ZipInfo) -> None:  # pragma: no cover
    """Helper: Decode the file name of `ZipInfo` using Shift JIS (SJIS) encoding.

    Args:
        info (zipfile.ZipInfo): The `ZipInfo` object containing the file information.
    """
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
    enc = CharDecEncoding.detect_text_file_encoding(invoice_file_path)
    with open(invoice_file_path, encoding=enc) as f:
        invoiceobj = json.load(f)
    return invoiceobj


def write_to_json_file(invoicefile_path: RdeFsPath, invoiceobj: dict[str, Any], enc: str = "utf_8"):  # pragma: no cover
    """Writes an content to a JSON file.

    Args:
        invoicefile_path (RdeFsPath): Path to the destination JSON file.
        invoiceobj (dict[str, Any]): Invoice object to be serialized and written.
        enc (str): Encoding to use when writing the file. Defaults to "utf_8".
    """
    with open(invoicefile_path, "w", encoding=enc) as f:
        json.dump(invoiceobj, f, indent=4, ensure_ascii=False)


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
            enc = CharDecEncoding.detect_text_file_encoding(metadef_filepath)
            with open(metadef_filepath, encoding=enc) as f:
                _tmp_metadef = json.load(f)
        else:
            _tmp_metadef = {}

        for _, vdef in _tmp_metadef.items():
            if vdef.get("action"):
                self.actions.append(vdef.get("action"))
            if vdef.get("unit"):
                outunit = vdef.get("unit")
                if not outunit.startswith("$"):
                    continue
                keyref = outunit[1:]
                self.referedmap[keyref] = None
        return _tmp_metadef

    def assign_vals(
        self,
        entry_dict_meta: Union[MetaType, RepeatedMetaType],
        *,
        ignore_empty_strvalue=True,
    ) -> "dict[str, set]":
        """Register the value of metadata.

        Perform validation and casting on the input metadata value in the specified format, and register it.
        The target format is validated using the key, format, and Unit specified in metadata-def.json.

        Args:
            entry_dict_meta (EntryMetaData): metadata(key/value) to register
            ignore_empty_strvalue (bool, optional): When ignore_empty_strvalue is True,
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

        # Register referred values in the reference table for actions and referred units (raw names)
        self.__register_refered_values(entry_dict_meta)

        for kdef, vdef in self.metaDef.items():
            keysrc = self.__get_source_key(kdef, vdef, entry_dict_meta)
            if keysrc is None:
                continue

            vsrc = entry_dict_meta[keysrc]
            _vsrc = self.__convert_to_str(vsrc)

            if kdef:
                # Register referred values in the reference table for actions and referred units (meta names)
                self.__registerd_refered_table(kdef, _vsrc)

            self.__process_meta_value(kdef, vdef, _vsrc, ignore_empty_strvalue)
            ret["assigned"].add(keysrc)
            # Do not break because a single value may be assigned to multiple places

        ret["unknown"] = {k for k in entry_dict_meta if k not in ret["assigned"]}
        return ret

    def __register_refered_values(self, entry_dict_meta: Union[MetaType, RepeatedMetaType]) -> None:
        """Register referred values in the reference table.

        This method converts the values from the input metadata dictionary to strings
        and registers them in the referred values table using the original keys.

        Args:
            entry_dict_meta (Union[MetaType, RepeatedMetaType]): The metadata dictionary
            containing key-value pairs to be registered.

        """
        for keysrc, vsrc in entry_dict_meta.items():
            _vsrc = self.__convert_to_str(vsrc)
            self.__registerd_refered_table(keysrc, _vsrc)

    def __get_source_key(self, kdef: str, vdef: MetadataDefJson, entry_dict_meta: Union[MetaType, RepeatedMetaType]) -> Optional[str]:
        keysrc = kdef
        if kdef not in entry_dict_meta and "originalName" in vdef:
            keysrc = vdef["originalName"]
        if keysrc not in entry_dict_meta:
            return None
        return keysrc

    def __process_meta_value(self, kdef: str, vdef: MetadataDefJson, _vsrc: Union[str, list[str]], ignore_empty_strvalue: bool) -> None:
        if vdef.get("action"):
            raise StructuredError("ERROR: this meta value should set by action")

        if vdef.get("variable"):
            self.__set_variable_metadata(kdef, _vsrc, vdef, ignore_empty_strvalue)
        else:
            if _vsrc is None or (_vsrc == "" and ignore_empty_strvalue):
                return
            self.__set_const_metadata(kdef, _vsrc, vdef)

    def _process_unit(self, vobj, idx):  # pragma: no cover
        _unit = vobj.get("unit", "")
        # "unit"のうち、"$"から始まる他キー参照を実際に置き換える
        if _unit.startswith("$"):
            srckey = _unit[1:]
            srcval = self.referedmap[srckey]
            if srcval is None:
                # 参照先が存在しなかった場合は単位未設定の状態とする
                del vobj["unit"]
            elif isinstance(srcval, str):
                vobj["unit"] = srcval
            else:
                vobj["unit"] = srcval[idx]

    def _process_action(self, vobj, k, idx):  # pragma: no cover
        # actionの処理
        stract = self.metaDef[k].get("action")
        if not stract:
            return

        for srckey, srcval in self.referedmap.items():
            if srckey not in stract:
                continue
            realval = srcval[idx] if isinstance(srcval, list) else srcval
            stract = stract.replace(srckey, f'"{realval}"' if isinstance(realval, str) else str(realval))
        vobj["value"] = eval(stract)

    def __convert_to_str(self, value: Union[str, int, float, list]) -> Union[str, list[str]]:
        """Convert the given value to string or list of strings."""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, list):
            return list(map(str, value))
        return ""

    @catch_exception_with_message(error_message="ERROR: failed to generate metadata.json", error_code=50)
    def writefile(self, meta_filepath, enc="utf_8"):
        """Writes the metadata to a file after processing units and actions.

        This method serializes the metadata into JSON format and writes it to the specified file.
        It processes units and actions for each metadata entry, sorts items according to 'metaDef',
        and outputs the sorted data to a file.

        The method also returns a list of keys from 'metaDef' that were not assigned values in the output.

        Args:
            meta_filepath (str): The file path where the metadata will be written.
            enc (str, optional): The encoding for the output file. Default is "utf_8".

        Returns:
            dict: A dictionary with keys 'assigned' and 'unknown'.
                'assigned' contains the set of keys that were assigned values,
                and 'unknown' contains the set of keys from 'metaDef' that were not used.

        Raises:
            CustomException: If the metadata generation fails, with a custom error message and error code.
        """
        outdict = json.loads(json.dumps({"constant": self.metaConst, "variable": self.metaVar}))

        for idx, kvdict in [(None, outdict["constant"])] + list(enumerate(outdict["variable"])):
            for k, vobj in kvdict.items():
                self._process_unit(vobj, idx)
                self._process_action(vobj, k, idx)

        # 項目をmetaDefに従ってソート
        outdict["constant"] = self.__sort_by_metadef(outdict["constant"])
        outdict["variable"] = [self.__sort_by_metadef(dvOrg) for dvOrg in outdict["variable"]]

        # ファイル出力
        with open(meta_filepath, "w", encoding=enc) as fout:
            json.dump(outdict, fout, indent=4, ensure_ascii=False)

        # metaDefのうち値の入らなかったキーのリストを返す
        assigned_keys = set(outdict["constant"].keys()).union(*(dv.keys() for dv in outdict["variable"]))
        unkown_keys = {k for k in self.metaDef if k not in assigned_keys}

        return {"assigned": assigned_keys, "unknown": unkown_keys}

    def __sort_by_metadef(self, data_dict: dict[str, Any]) -> dict[str, Any]:
        return {k: data_dict[k] for k in self.metaDef if k in data_dict}

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
            for stract in self.actions:
                if key not in stract:
                    continue
                self.referedmap[key] = deepcopy(value)

    def __set_variable_metadata(
        self,
        key: str,
        metavalues: Union[str, list[str]],
        metadefvalue: MetadataDefJson,
        opt_ignore_emptystr: bool,
    ) -> None:  # pragma: no cover
        outtype = metadefvalue["schema"].get("type")
        outfmt = metadefvalue["schema"].get("format")
        orgtype = metadefvalue.get("originalType")
        outunit = metadefvalue.get("unit")
        if len(self.metaVar) < len(metavalues):
            self.metaVar += [{} for _ in range(len(metavalues) - len(self.metaVar))]
        for idx, val_src_element in enumerate(metavalues):
            if val_src_element is None:
                continue
            if val_src_element == "" and opt_ignore_emptystr:
                continue
            self.metaVar[idx][key] = self._metadata_validation(val_src_element, outtype, outfmt, orgtype, outunit)

    def __set_const_metadata(
        self,
        key: str,
        metavalue: Union[str, list[str]],
        metadefvalue: MetadataDefJson,
    ) -> None:  # pragma: no cover
        outtype = metadefvalue["schema"].get("type")
        outfmt = metadefvalue["schema"].get("format")
        orgtype = metadefvalue.get("originalType")
        outunit = metadefvalue.get("unit")
        if not isinstance(metavalue, list):
            self.metaConst[key] = self._metadata_validation(metavalue, outtype, outfmt, orgtype, outunit)

    def _metadata_validation(
        self,
        vsrc: str,
        outtype: Optional[str],
        outfmt: Optional[str],
        orgtype: Optional[str],
        outunit: Optional[str],
    ) -> "dict[str, Union[bool, int, float, str]]":  # pragma: no cover
        """Casts the input metadata to the specified format and performs validation to check.

        if it can be cast to the specified data type. The formats for various metadata are described in metadata-def.json.

        Args:
            vsrc (str): The value of the input metadata.
            outtype (Optional[str]): The data type of the converted metadata.
            outfmt (Optional[str]): The format of the converted metadata.
            orgtype (Optional[str]): The data type of the original metadata.
            outunit (Optional[str]): The unit of the converted metadata.

        Returns:
            dict[str, Union[bool, int, float, str]]: Returns the conversion result in the form of metadata for metadata.json.

        Note:
            original func: _vDict()
        """
        vsrc = vsrc.strip()

        if orgtype is None:
            _casted_value = castval(vsrc, outtype, outfmt)
        elif orgtype in ["integer", "number"]:
            # 単位付き文字列が渡されても単位の代入は本関数内では扱わない。必要に応じて別途代入する事。
            valpair = _split_value_unit(vsrc)
            vstr = valpair.value
            # 解釈可能かチェック。不可能だった場合は例外スローされるため、
            # 例外なく処理終了できるかのみに興味がある
            _casted_value = castval(vstr, orgtype, outfmt)
        else:
            vstr = vsrc
            # 解釈可能かチェック。不可能だった場合は例外スローされるため、
            # 例外なく処理終了できるかのみに興味がある
            _casted_value = castval(vstr, orgtype, outfmt)

        if outunit:
            return {
                "value": _casted_value,
                "unit": outunit,
            }
        else:
            return {"value": _casted_value}


def castval(valstr: str, outtype: Optional[str], outfmt: Optional[str]) -> Union[bool, int, float, str]:
    """The function formats the string valstr based on outtype and outfmt and returns the formatted value.

    The function returns a formatted value of the string valstr according to
    the specified outtype and outfmt. The outtype must be a string ("string")
    for outfmt to be used. If valstr contains a value with units,
    the assignment of units is not handled within this function.
    It should be assigned separately as needed.

    Args:
        valstr (str): String to be converted of type
        outtype (str): Type information at output
        outfmt (str): Formatting at output (related to date data)
    """

    def _trycast(valstr, tp):
        try:
            return tp(valstr)
        except Exception:
            return None

    def _convert_to_date_format(value: str, fmt: str) -> str:
        dtobj = dateutil.parser.parse(value)
        if fmt == "date-time":
            return dtobj.isoformat()
        elif fmt == "date":
            return dtobj.strftime("%Y-%m-%d")
        elif fmt == "time":
            return dtobj.strftime("%H:%M:%S")
        else:
            raise StructuredError("ERROR: unknown format in metaDef")

    if outtype == "boolean":
        if _trycast(valstr, bool) is not None:
            return bool(valstr)

    elif outtype == "integer":
        # Even if a string with units is passed, the assignment of units is not handled in this function. Assign units separately as necessary.
        val_unit_pair = _split_value_unit(valstr)
        if _trycast(val_unit_pair.value, int) is not None:
            return int(val_unit_pair.value)

    elif outtype == "number":
        # Even if a string with units is passed, the assignment of units is not handled in this function. Assign units separately as necessary.
        val_unit_pair = _split_value_unit(valstr)
        if _trycast(val_unit_pair.value, int) is not None:
            return int(val_unit_pair.value)
        if _trycast(val_unit_pair.value, float) is not None:
            return float(val_unit_pair.value)

    elif outtype == "string":
        if not outfmt:
            return valstr
        return _convert_to_date_format(valstr, outfmt)

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
    meta_obj = Meta(metadef_filepath)
    meta_obj.assign_vals(const_info)
    meta_obj.assign_vals(val_info)

    ret = meta_obj.writefile(metaout_filepath)
    return ret
