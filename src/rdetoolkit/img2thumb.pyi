from pathlib import Path
from rdetoolkit.exceptions import catch_exception_with_message as catch_exception_with_message


def copy_images_to_thumbnail(out_dir_thumb_img: str | Path, out_dir_main_img: str | Path, *, target_image_name: str | None = ..., img_ext: str | None = ...) -> None:
    pass


def resize_image(path: str | Path, width: int = 640, height: int = 480, output_path: str | Path | None = None) -> str:
    pass
