from __future__ import annotations

import itertools
import os
import shutil
from glob import glob

from rdetoolkit.exceptions import catch_exception_with_message


def __copy_img_to_thumb(out_dir_thumb_img: str, source_img_paths: str | list[str]):
    """Copies the other images to the thumbnail directory.

    Args:
        out_dir_thumb_img (str): The directory path where the thumbnail images will be saved.
        source_img_paths (str | list[str]): The list of paths of the source image files.

    """
    if isinstance(source_img_paths, str):
        source_img_paths = [source_img_paths]
    for path in source_img_paths:
        basename = os.path.basename(path)
        thumb_img_path = os.path.join(out_dir_thumb_img, basename)
        shutil.copy(path, thumb_img_path)


def __find_img_path(dirname: str, target_name: str) -> str:
    search_pattern = os.path.join(dirname, "**", target_name)
    matching_files = list(glob(search_pattern, recursive=True))
    if matching_files:
        return matching_files[0]
    return ""


@catch_exception_with_message(error_message="ERROR: failed to copy image files", error_code=50)
def copy_images_to_thumbnail(out_dir_thumb_img: str, out_dir_main_img: str, *, target_image_name: str | None = None, img_ext: str | None = None) -> None:
    """Copy the image files in the other image folder and the main image folder to the thumbnail folder.

    Args:
        out_dir_thumb_img (str): directory path where thumbnail image is saved
        out_dir_main_img (str): directory path where main image is saved
        target_image_name (str, optional): Specify the name of the image file to be copied to the thumbnail folder.
        img_ext (str, optional): image file extension.
    """
    img_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"] if img_ext is None else [img_ext]

    img_paths_main = [glob(os.path.join(out_dir_main_img, "*" + ext)) for ext in img_exts]
    img_path_main = list(itertools.chain.from_iterable(img_paths_main))

    # When there are multiple images in the main image folder, copy one at the leading index as the representative image.
    __main_img_path: str = ""
    if target_image_name is not None:
        __main_img_path = __find_img_path(out_dir_main_img, target_image_name)
    elif len(img_path_main) >= 1:
        __main_img_path = img_path_main[0]

    if __main_img_path:
        __copy_img_to_thumb(out_dir_thumb_img, __main_img_path)
