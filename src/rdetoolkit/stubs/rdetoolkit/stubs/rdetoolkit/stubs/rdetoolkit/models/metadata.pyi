from pydantic import BaseModel, RootModel
from typing import Any, Final, Optional

MAX_VALUE_SIZE: Final[int]

class Variable(BaseModel):
    variable: dict[str, Any]
    @classmethod
    def check_value_size(cls, v) -> None: ...

class MetaValue(BaseModel):
    value: Any
    unit: Optional[str]
    @classmethod
    def check_value_size(cls, v) -> None: ...

class ValidableItems(RootModel):
    root: list[dict[str, MetaValue]]

class MetadataItem(BaseModel):
    constant: Optional[dict[str, MetaValue]]
    variable: ValidableItems
