import json
from typing import Any, Optional

from rdetoolkit.models.metadata import MetadataDefItem


def metadata_def_json_validator(*, path: Optional[str] = None, json_obj: Optional[dict[str, Any]] = None) -> MetadataDefItem:
    """Validator for metadata_def.json.

    Args:
        path (str, optional): File path of metadata_def.json. Defaults to None.
        json_obj (dict[str, Any], optional): Json Object of metadata_def.json. Defaults to None.

    Retrun:
        MetadataDefItem: The validated metadata_def.json object.

    Raises:
        ValueError: If neither 'path' nor 'json_obj' is provided, or if both are provided.

    Note:
        Either 'path' or 'json_obj' must be provided, but not both.
    """
    if path is None and json_obj is None:
        raise ValueError("At least one of 'path' or 'json_obj' must be provided")
    elif path is not None and json_obj is not None:
        raise ValueError("Both 'path' and 'json_obj' cannot be provided at the same time")

    if path is not None:
        with open(path, encoding="utf-8") as f:
            __data = json.load(f)
    elif json_obj is not None:
        __data = json_obj
    else:
        raise ValueError("Unexpected error")

    return MetadataDefItem(**__data)
