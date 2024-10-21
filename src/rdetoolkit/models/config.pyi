from pydantic import BaseModel

class SystemSettings(BaseModel):
    extended_mode: str | None
    save_raw: bool
    save_nonshared_raw: bool
    save_thumbnail_image: bool
    magic_variable: bool

class MultiDataTileSettings(BaseModel):
    ignore_errors: bool

class Config(BaseModel, extra='allow'):
    system: SystemSettings
    multidata_tile: MultiDataTileSettings | None
