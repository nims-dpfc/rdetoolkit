from pydantic import BaseModel, Field as Field, RootModel
from typing import Any, Final

MAX_VALUE_SIZE: Final[int]

class Variable(BaseModel):
    variable: dict[str, Any]
    @classmethod
    def check_value_size(cls, v: dict[str, Any]) -> dict[str, Any]: ...

class MetaValue(BaseModel):
    value: Any
    unit: str | None
    @classmethod
    def check_value_size(cls, v: Any) -> Any: ...

class ValidableItems(RootModel):
    root: list[dict[str, MetaValue]]

class MetadataItem(BaseModel):
    constant: dict[str, MetaValue]
    variable: ValidableItems
