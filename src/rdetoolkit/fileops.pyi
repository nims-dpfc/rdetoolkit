from _typeshed import Incomplete as Incomplete
from pathlib import Path
from typing import Any

logger: Incomplete

def readf_json(path: str | Path) -> dict[str, Any]: ...
def writef_json(path: str | Path, obj: dict[str, Any], *, enc: str = 'utf_8') -> dict[str, Any]: ...
