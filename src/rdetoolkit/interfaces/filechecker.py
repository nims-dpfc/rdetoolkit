# ---------------------------------------------------------
# Copyright (c) 2023, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
#
# Contributor:
#     Hayato Sonokawa
# ---------------------------------------------------------
# coding: utf-8

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple

from src.rdetoolkit.models.rde2types import ZipFilesPathList, unZipFilesPathList, RawFiles


class IInputFileHelper(ABC):
    """
    An abstract interface representing a helper for input file operations.

    This interface defines the expected operations to handle and process zip files
    among a list of input files.

    Methods:
        get_zipfiles(input_files: list[Path]) -> ZipFilesPathList:
        unpacked(zipfile: Path, target_dir: Path) -> unZipFilesPathList:
    """

    @abstractmethod
    def get_zipfiles(self, input_files: list[Path]) -> ZipFilesPathList:
        raise NotImplementedError

    @abstractmethod
    def unpacked(self, zipfile: Path, target_dir: Path) -> unZipFilesPathList:
        raise NotImplementedError


class IInputFileChecker(ABC):
    @abstractmethod
    def parse(self, src_input_path: Path) -> tuple[RawFiles, Optional[Path]]:
        raise NotImplementedError


class ICompressedFileStructParser(ABC):
    @abstractmethod
    def read(self, zipfile: Path, target_path: Path) -> List[Tuple[Path, ...]]:
        raise NotImplementedError
