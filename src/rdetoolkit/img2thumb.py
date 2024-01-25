# ---------------------------------------------------------
# Copyright (c) 2022, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
# ---------------------------------------------------------
# coding: utf-8

import os
import shutil
from glob import glob
from typing import Optional

from rdetoolkit.exceptions import catch_exception_with_message


@catch_exception_with_message(errro_message="ERROR: failed to copy image files", error_code=50)
def copy_images_to_thumbnail(out_dir_thumb_img: str, out_dir_main_img: str, *, out_dir_other_img: Optional[str] = None, imgExt: str = ".png") -> None:
    """Copy the image files in the other image folder and the main image folder to the thumbnail folder.

    Args:
        out_dir_thumb_img (str): directory path where thumbnail image is saved
        out_dir_main_img (str): directory path where main image is saved
        out_dir_other_img (str, optional): directory path where other images are saved. Defaults to None.
        imgExt (str, optional): image file extension.
    """
    # Thumbnail images
    for fpathSrc in glob(os.path.join(out_dir_main_img, "*" + imgExt)):
        fBaseName = os.path.basename(fpathSrc)
        fpathThumbIImageM = os.path.join(out_dir_thumb_img, f"!_{fBaseName}")
        shutil.copy(fpathSrc, fpathThumbIImageM)
    if out_dir_other_img:
        for fpathSrc in glob(os.path.join(out_dir_other_img, "*" + imgExt)):
            shutil.copy(fpathSrc, out_dir_thumb_img)
