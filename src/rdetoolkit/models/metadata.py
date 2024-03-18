from typing import Any, Optional

from pydantic import BaseModel, RootModel, field_validator


class Variable(BaseModel):
    """Metadata class for the 'variable' attribute."""

    variable: dict[str, Any]

    @field_validator("variable")
    def check_value_size(cls, v):
        """Validator that verifies that the size of the 'variable' type metadata value does not exceed 1024 bytes.

        Args:
            v (dict[str, Any]): Metadata of 'variable'

        Raises:
            ValueError: Exception error if the value of the metadata is more than 1024 bytes
        """
        for value in v.values():
            if not isinstance(v, str):
                continue
            if len(str(value).encode("utf-8")) > 1024:
                raise ValueError(f"Value size exceeds 1024 bytes: {v}")
        return v


class MetaValue(BaseModel):
    """Metadata class for the 'value' and 'unit' attributes."""

    value: Any
    unit: Optional[str] = None

    @field_validator("value")
    def check_value_size(cls, v):
        """Validator that verifies that the size of the 'value' does not exceed 1024 bytes if it is a string.

        Args:
            v (dict[str, Any]): Value of the metadata

        Raises:
            ValueError: Exception error if the value of the metadata is more than 1024 bytes
        """
        if not isinstance(v, str):
            return v
        if len(str(v).encode("utf-8")) > 1024:
            raise ValueError("Value size exceeds 1024 bytes")
        return v


ValidableItems = RootModel[list[dict[str, MetaValue]]]


class MetadataDefItem(BaseModel):
    """metadata-def.json class."""

    constant: dict[str, MetaValue]
    variable: ValidableItems
