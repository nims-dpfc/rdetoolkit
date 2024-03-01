# ---------------------------------------------------------
# Copyright (c) 2022, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
# ---------------------------------------------------------
# coding: utf-8

import itertools
import os
import shutil
from glob import glob
from typing import Optional

from rdetoolkit.exceptions import catch_exception_with_message


@catch_exception_with_message(error_message="ERROR: failed to copy image files", error_code=50)
def copy_images_to_thumbnail(out_dir_thumb_img: str, out_dir_main_img: str, *, out_dir_other_img: Optional[str] = None, imgExt: Optional[str] = None) -> None:
    """Copy the image files in the other image folder and the main image folder to the thumbnail folder.

    Args:
        out_dir_thumb_img (str): directory path where thumbnail image is saved
        out_dir_main_img (str): directory path where main image is saved
        out_dir_other_img (str, optional): directory path where other images are saved. Defaults to None.
        imgExt (str, optional): image file extension.
    """
    if imgExt is None:
        img_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"]

    img_paths_main = [glob(os.path.join(out_dir_main_img, "*" + ext)) for ext in img_exts]
    if out_dir_other_img:
        img_paths_other = [glob(os.path.join(out_dir_other_img, "*" + ext)) for ext in img_exts]
    else:
        img_paths_other = []
    img_paths_main = [glob(os.path.join(out_dir_main_img, "*" + ext)) for ext in img_exts]
    img_paths = list(itertools.chain.from_iterable(img_paths_main + img_paths_other))

    for path in img_paths:
        basename = os.path.basename(path)
        thumb_img_path = os.path.join(out_dir_thumb_img, f"!_{basename}")
        shutil.copy(path, thumb_img_path)
