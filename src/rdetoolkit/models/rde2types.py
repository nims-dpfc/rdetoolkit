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
    inputdata: Path
    invoice: Path
    tasksupport: Path

    @property
    def defualt_csv(self) -> Path:
        if self.tasksupport:
            tasksupport = self.tasksupport
        else:
            tasksupport = Path("data", "tasksupport")
        return tasksupport.joinpath("default_value.csv")


@dataclass
class RdeOutputResourcePath:
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
