from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple

from rdetoolkit.models.rde2types import RawFiles, ZipFilesPathList, unZipFilesPathList


class IInputFileHelper(ABC):
    """An abstract interface representing a helper for input file operations.

    This interface defines the expected operations to handle and process zip files
    among a list of input files.

    Methods:
        get_zipfiles(input_files: list[Path]) -> ZipFilesPathList:
        unpacked(zipfile: Path, target_dir: Path) -> unZipFilesPathList:
    """

    @abstractmethod
    def get_zipfiles(self, input_files: list[Path]) -> ZipFilesPathList:
        """Retrieves a list of paths to zip files from a list of input file paths.

        Args:
            input_files (list[Path]): A list of file paths to search for zip files.

        Returns:
            ZipFilesPathList: A list of paths pointing to the found zip files.
        """
        raise NotImplementedError

    @abstractmethod
    def unpacked(self, zipfile: Path, target_dir: Path) -> unZipFilesPathList:
        """Unpacks a specified zip file into a target directory and returns a list of paths to the unpacked files.

        Args:
            zipfile (Path): The path to the zip file to be unpacked.
            target_dir (Path): The directory where the zip file contents will be unpacked.

        Returns:
            unZipFilesPathList: A list of paths to the unpacked files.
        """
        raise NotImplementedError


class IInputFileChecker(ABC):
    """An abstract interface for checking and parsing input files.

    This interface is designed to define the structure for classes that handle the parsing
    of source input files. It's responsible for validating and extracting necessary information
    from these files.
    """

    @abstractmethod
    def parse(self, src_input_path: Path) -> tuple[RawFiles, Optional[Path]]:
        """Parses the given source input path and extracts relevant information.

        This method should analyze the file or files located at the specified path and extract
        essential data needed for further processing.

        Args:
            src_input_path (Path): The path to the source input file(s).

        Returns:
            tuple[RawFiles, Optional[Path]]: A tuple where the first element is the extracted raw file data,
                                            and the second element is an optional path to additional relevant data.
        """
        raise NotImplementedError


class ICompressedFileStructParser(ABC):
    """An abstract interface for parsing the structure of compressed files.

    This interface defines the expected operations for classes that are responsible for
    reading and understanding the structure of compressed files (like zip files), especially
    focusing on how these files are organized internally.
    """

    @abstractmethod
    def read(self, zipfile: Path, target_path: Path) -> List[Tuple[Path, ...]]:
        """Reads and parses the structure of the compressed file.

        This method should open and inspect the contents of a compressed file, extracting
        information about its internal structure, such as file paths and organization.

        Args:
            zipfile (Path): The path to the compressed file to be read.
            target_path (Path): The path where the contents of the compressed file might be extracted or analyzed.

        Returns:
            List[Tuple[Path, ...]]: A list of tuples, each containing paths or other relevant data extracted from the compressed file.
        """
        raise NotImplementedError
