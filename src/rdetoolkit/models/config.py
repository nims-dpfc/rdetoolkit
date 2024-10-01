from __future__ import annotations

from pydantic import BaseModel, Field


class Config(BaseModel, extra="allow"):
    """The configuration class used in RDEToolKit.

    Attributes:
        extended_mode (Optional[str]): The mode to run the RDEToolKit in. It can be either 'rdeformat' or 'MultiDataTile'. If not specified, it defaults to None.
        save_raw (bool): A boolean flag that indicates whether to automatically save raw data to the raw directory. It defaults to True.
        save_thumbnail_image (bool): A boolean flag that indicates whether to automatically save the main image to the thumbnail directory. It defaults to False.
        magic_variable (bool): A boolean flag that indicates whether to use the feature where specifying '${filename}' as the data name results in the filename being transcribed as the data name. It defaults to False.
    """
    extended_mode: str | None = Field(default=None, description="The mode to run the RDEtoolkit in. select: rdeformat, MultiDataTile")
    save_raw: bool = Field(default=True, description="Auto Save raw data to the raw directory")
    save_thumbnail_image: bool = Field(default=False, description="Auto Save main image to the thumbnail directory")
    magic_variable: bool = Field(
        default=False,
        description="The feature where specifying '${filename}' as the data name results in the filename being transcribed as the data name.",
    )
