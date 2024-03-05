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


def __copy_main_img_to_thumb(out_dir_thumb_img: str, source_img_path: str):
    """Copies the main image to the thumbnail directory.

    Args:
        out_dir_thumb_img (str): The directory path where the thumbnail image will be saved.
        source_img_path (str): The path of the source image file.

    """
    basename = os.path.basename(source_img_path)
    thumb_img_path = os.path.join(out_dir_thumb_img, f"!_{basename}")
    shutil.copy(source_img_path, thumb_img_path)


def __copy_other_img_to_thumb(out_dir_thumb_img: str, source_img_paths: list[str]):
    """Copies the other images to the thumbnail directory.

    Args:
        out_dir_thumb_img (str): The directory path where the thumbnail images will be saved.
        source_img_paths (list[str]): The list of paths of the source image files.

    """
    for path in source_img_paths:
        basename = os.path.basename(path)
        thumb_img_path = os.path.join(out_dir_thumb_img, basename)
        shutil.copy(path, thumb_img_path)


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
    img_path_main = list(itertools.chain.from_iterable(img_paths_main))

    __main_img_path: str = ""
    __other_from_main_img: list[str] = []
    if len(img_path_main) > 1:
        __main_img_path, __other_from_main_img = img_path_main[0], img_path_main[1:]
    elif len(img_path_main) == 1:
        __other_from_main_img = []
        __main_img_path = img_path_main[0]

    if __main_img_path:
        __copy_main_img_to_thumb(out_dir_thumb_img, __main_img_path)
    if __other_from_main_img:
        __copy_other_img_to_thumb(out_dir_thumb_img, __other_from_main_img)

    if out_dir_other_img:
        __img_paths_other = [glob(os.path.join(out_dir_other_img, "*" + ext)) for ext in img_exts]
        img_paths_other = list(itertools.chain.from_iterable(__img_paths_other))
        __copy_other_img_to_thumb(out_dir_thumb_img, img_paths_other)
