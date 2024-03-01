import abc
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple

from rdetoolkit.models.rde2types import RawFiles as RawFiles
from rdetoolkit.models.rde2types import ZipFilesPathList as ZipFilesPathList
from rdetoolkit.models.rde2types import unZipFilesPathList as unZipFilesPathList

class IInputFileHelper(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def get_zipfiles(self, input_files: list[Path]) -> ZipFilesPathList: ...
    @abstractmethod
    def unpacked(self, zipfile: Path, target_dir: Path) -> unZipFilesPathList: ...

class IInputFileChecker(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def parse(self, src_input_path: Path) -> tuple[RawFiles, Optional[Path]]: ...

class ICompressedFileStructParser(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def read(self, zipfile: Path, target_path: Path) -> List[Tuple[Path, ...]]: ...
