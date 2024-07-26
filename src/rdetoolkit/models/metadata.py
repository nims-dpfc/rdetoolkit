from __future__ import annotations

from typing import Any, Final

from pydantic import BaseModel, RootModel, field_validator

MAX_VALUE_SIZE: Final[int] = 1024


class Variable(BaseModel):
    """Metadata class for the 'variable' attribute."""

    variable: dict[str, Any]

    @field_validator("variable")
    @classmethod
    def check_value_size(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validator that verifies that the size of the 'variable' type metadata value does not exceed 1024 bytes.

        Args:
            v (dict[str, Any]): Metadata of 'variable'

        Raises:
            ValueError: Exception error if the value of the metadata is more than 1024 bytes
        """
        for value in v.values():
            if not isinstance(v, str):
                continue
            if len(str(value).encode("utf-8")) > MAX_VALUE_SIZE:
                emsg = f"Value size exceeds {MAX_VALUE_SIZE} bytes: {v}"
                raise ValueError(emsg)
        return v


class MetaValue(BaseModel):
    """Metadata class for the 'value' and 'unit' attributes."""

    value: Any
    unit: str | None = None

    @field_validator("value")
    @classmethod
    def check_value_size(cls, v: Any) -> Any:
        """Validator that verifies that the size of the 'value' does not exceed 1024 bytes if it is a string.

        Args:
            v (dict[str, Any]): Value of the metadata

        Raises:
            ValueError: Exception error if the value of the metadata is more than 1024 bytes
        """
        if not isinstance(v, str):
            return v
        if len(str(v).encode("utf-8")) > MAX_VALUE_SIZE:
            emsg = f"Value size exceeds {MAX_VALUE_SIZE} bytes"
            raise ValueError(emsg)
        return v


class ValidableItems(RootModel):
    """A class representing validatable items of metadata.

    This class inherits from `RootModel`, and the `root` attribute holds a list of dictionaries,
    where each dictionary has a string as a key and a `MetaValue` as a value.

    Attributes:
        root (list[dict[str, MetaValue]]): A list of validatable items of metadata.
    """

    root: list[dict[str, MetaValue]]


class MetadataItem(BaseModel):
    """metadata-def.json class.

    Stores metadata extracted by the data structuring process.

    Attributes:
        constant (dict[str, MetaValue]): A set of metadata common to all measurements.
        variable (ValidableItems): An array of metadata sets that vary with each measurement.
    """

    constant: dict[str, MetaValue]
    variable: ValidableItems
