from _typeshed import Incomplete
from pathlib import Path
from rdetoolkit.core import detect_encoding as detect_encoding
from rdetoolkit.exceptions import StructuredError as StructuredError
from rdetoolkit.rdelogger import get_logger as get_logger
from typing import Any

logger: Incomplete

def readf_json(path: str | Path) -> dict[str, Any]: ...
def writef_json(path: str | Path, obj: dict[str, Any], *, enc: str = 'utf_8') -> dict[str, Any]: ...
