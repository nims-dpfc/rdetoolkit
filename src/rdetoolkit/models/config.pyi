from __future__ import annotations

from pydantic import BaseModel


class Config(BaseModel, extra="allow"):
    extended_mode: str | None
    save_raw: bool
    save_thumbnail_image: bool
    magic_variable: bool
