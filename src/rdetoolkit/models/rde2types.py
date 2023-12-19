# ---------------------------------------------------------
# Copyright (c) 2022, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
#
# Contributor:
#     Hayato Sonokawa
# ---------------------------------------------------------
# coding: utf-8

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypedDict, Union


ZipFilesPathList = list[Path]
unZipFilesPathList = list[Path]
ExcelInvoicePathList = list[Path]
OtherFilesPathList = list[Path]
PathTuple = tuple[Path, ...]
InputFilesGroup = tuple[ZipFilesPathList, ExcelInvoicePathList, OtherFilesPathList]
RawFiles = list[PathTuple]
MetaType = dict[str, Union[str, int, float, list]]
RepeatedMetaType = dict[str, list[Union[str, int, float]]]
MetaItem = dict[str, Union[str, int, float, bool]]
RdeFsPath = Union[str, Path]


@dataclass
class RdeFormatFlags:
    _is_rdeformat_enabled: bool = False
    _is_multifile_enabled: bool = False

    def __post_init__(self):
        self.is_rdeformat_enabled = os.path.exists("data/tasksupport/rdeformat.txt")
        self.is_multifile_enabled = os.path.exists("data/tasksupport/multifile.txt")

    @property
    def is_rdeformat_enabled(self):
        return self._is_rdeformat_enabled

    @is_rdeformat_enabled.setter
    def is_rdeformat_enabled(self, value):
        if value and self.is_multifile_enabled:
            raise ValueError("both flags cannot be True")
        self._is_rdeformat_enabled = value

    @property
    def is_multifile_enabled(self):
        return self._is_multifile_enabled

    @is_multifile_enabled.setter
    def is_multifile_enabled(self, value):
        if value and self.is_rdeformat_enabled:
            raise ValueError("both flags cannot be True")
        self._is_multifile_enabled = value


@dataclass
class RdeInputDirPaths:
    """A data class that holds folder paths used for input in the RDE.
    It manages the folder paths for input data necessary for the RDE.

    Attributes:
        inputdata (Path): Path to the folder where input data is stored.
        invoice (Path): Path to the folder where invoice.json is stored.
        tasksupport (Path): Path to the folder where task support data is stored.

    Properties:
        defualt_csv (Path): Provides the path to the 'default_value.csv' file. If `tasksupport` is specified, it uses the path under it; otherwise, it uses the default path under 'data/tasksupport'.
    """
    inputdata: Path
    invoice: Path
    tasksupport: Path

    @property
    def defualt_csv(self) -> Path:
        """Returns the path to the 'default_value.csv' file.
        If `tasksupport` is set, this path is used.
        If not set, the default path under 'data/tasksupport' is used.

        Returns:
            Path: Path to the 'default_value.csv' file.
        """
        if self.tasksupport:
            tasksupport = self.tasksupport
        else:
            tasksupport = Path("data", "tasksupport")
        return tasksupport.joinpath("default_value.csv")


@dataclass
class RdeOutputResourcePath:
    """A data class that holds folder paths used as output destinations for RDE.
    It maintains the paths for various files used in the structuring process.

    Attributes:
        raw (Path): Path where raw data is stored.
        rawfiles (tuple[Path, ...]): Holds a tuple of input file paths, such as those unzipped, for a single tile of data.
        struct (Path): Path for storing structured data.
        main_image (Path): Path for storing the main image file.
        other_image (Path): Path for storing other image files.
        meta (Path): Path for storing metadata files.
        thumbnail (Path): Path for storing thumbnail image files.
        logs (Path): Path for storing log files.
        invoice (Path): Path for storing invoice files.
        invoice_schema_json (Path): Path for the invoice.schema.json file.
        invoice_org (Path): Path for storing the backup of invoice.json.
        temp (Optional[Path]): Path for storing temporary files.
        invoice_patch (Optional[Path]): Path for storing modified invoice files.
        attachment (Optional[Path]): Path for storing attachment files.
"""
    raw: Path
    rawfiles: tuple[Path, ...]
    struct: Path
    main_image: Path
    other_image: Path
    meta: Path
    thumbnail: Path
    logs: Path
    invoice: Path
    invoice_schema_json: Path
    invoice_org: Path
    temp: Optional[Path] = None
    invoice_patch: Optional[Path] = None
    attachment: Optional[Path] = None
    nonshared_raw: Optional[Path] = None


class Name(TypedDict):
    ja: str
    en: str


class Schema(TypedDict, total=False):
    type: str
    format: str


class MetadataDefJson(TypedDict):
    name: Name
    schema: Schema
    unit: str
    description: str
    uri: str
    originalName: str
    originalType: str
    mode: str
    order: str
    valiable: int
    _feature: bool
    action: str


@dataclass
class ValueUnitPair:
    value: str
    unit: str
