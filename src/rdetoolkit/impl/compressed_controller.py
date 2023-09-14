# ---------------------------------------------------------
# Copyright (c) 2023, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
#
# Contributor:
#     Hayato Sonokawa
# ---------------------------------------------------------
# coding: utf-8

import os
import shutil
from pathlib import Path
from typing import List, Tuple, Union

import pandas as pd

from src.rdetoolkit.exceptions import StructuredError
from src.rdetoolkit.interfaces.filechecker import ICompressedFileStructParser
from src.rdetoolkit.invoiceFile import checkExistRawFiles


class CompressedFlatFileParser(ICompressedFileStructParser):
    """Parser for compressed flat files, providing functionality to read and extract the contents.

    This parser specifically deals with flat files that are compressed. It extracts the files
    and ensures they match the expected structure described in an xlsx invoice.

    Attributes:
        xlsx_invoice (pd.DataFrame): DataFrame representing the expected structure or content description
            of the compressed files.
    """

    def __init__(self, xlsx_invoice: pd.DataFrame):
        self.xlsx_invoice = xlsx_invoice

    def read(self, zipfile: Path, target_path: Path) -> List[Tuple[Path, ...]]:
        """Extracts the contents of the zipfile to the target path and checks their existence
        against the Excelinvoice.

        Args:
            zipfile (Path): Path to the compressed flat file to be read.
            target_path (Path): Destination directory where the zipfile will be extracted to.

        Returns:
            List[Tuple[Path, ...]]: A list of tuples containing file paths. Each tuple
            represents files from the compressed archive that matched the xlsx_invoice structure.
        """
        _extracted_files = self._unpacked(zipfile, target_path)
        return [(f,) for f in checkExistRawFiles(self.xlsx_invoice, _extracted_files)]

    def _unpacked(self, zipfile: Union[Path, str], target_dir: Union[Path, str]):
        if isinstance(target_dir, str):
            target_dir = Path(target_dir)
        shutil.unpack_archive(zipfile, target_dir)
        return [f for f in target_dir.glob("**/*") if f.is_file()]


class CompressedFolderParser(ICompressedFileStructParser):
    """Parser for compressed folders, extracting contents and ensuring they match an expected structure.

    This parser is specifically designed for compressed folders. It extracts the content
    and verifies against a provided xlsx invoice structure.

    Attributes:
        xlsx_invoice (pd.DataFrame): DataFrame representing the expected structure or content description
            of the compressed folder contents.
    """

    def __init__(self, xlsx_invoice: pd.DataFrame):
        self.xlsx_invoice = xlsx_invoice

    def read(self, zipfile: Path, target_path: Path) -> List[Tuple[Path, ...]]:
        """Extracts the contents of the zipfile and returns validated file paths.

        Args:
            zipfile (Path): Path to the compressed folder to be read.
            target_path (Path): Destination directory where the zipfile will be extracted.

        Returns:
            List[Tuple[Path, ...]]: A list of tuples containing file paths that have been
            validated based on unique directory names.
        """
        _ = self._unpacked(zipfile, target_path)
        safe_verification_files = self.validation_uniq_dirname(target_path, exclude_names=["invoice_org.json"])
        return [tuple(f) for f in safe_verification_files.values()]

    def _unpacked(self, zipfile: Union[Path, str], target_dir: Union[Path, str]):
        if isinstance(target_dir, str):
            target_dir = Path(target_dir)
        shutil.unpack_archive(zipfile, target_dir)
        return [f for f in target_dir.glob("**/*") if f.is_file()]

    def validation_uniq_dirname(self, target_path: Union[str, Path], exclude_names: list[str]) -> dict[str, list[Path]]:
        """Check if there are any non-unique directory names under the target directory

        Args:
            target_path (Union[str, Path]): The directory path to scan
            exclude_names (list[str]): Excluded files

        Raises:
            StructuredError: An exception is raised when duplicate directory names are detected

        Returns:
            dict[str, Path]: Returns the unique directory names and a list of files under each directory

        Note:
            This function checks for the existence of folders with the same name,
            differing only in case (e.g., 'folder1' and 'Folder1'). In a Unix-based filesystem,
            such folders can coexist when creating a zip file. However, Windows does not allow
            for this coexistence when downloading and unzipping the file, leading to an unzip
            failure in my environment. Therefore, it's necessary to check for folders whose names
            differ only in case.
        """
        verification_files: dict[str, list[Path]] = {}
        unique_dirname_set = set()
        for dir, _, fnames in os.walk(target_path):
            fnames = [f for f in fnames if f not in exclude_names]
            if not fnames:
                continue
            dir = str(dir).lower()
            if dir in unique_dirname_set:
                raise StructuredError(f'ERROR: data directory should have unique name but same name found "{dir}"')
            unique_dirname_set.add(dir)
            verification_files[dir] = [Path(dir) / Path(f) for f in fnames]

        return verification_files


def parse_compressedfile_mode(
    xlsx_invoice: pd.DataFrame,
) -> ICompressedFileStructParser:
    """Parses the mode of a compressed file and returns the corresponding parser object.

    Args:
        xlsx_invoice (pandas.DataFrame): The invoice data in Excel format.

    Returns:
        ICompressedFileStructParser: An instance of the compressed file structure parser.
    """
    if "data_file_names/name" in xlsx_invoice.columns:
        # File Mode
        return CompressedFlatFileParser(xlsx_invoice)
    else:
        # Folder Mode
        return CompressedFolderParser(xlsx_invoice)
