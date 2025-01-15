from pathlib import Path
from rdetoolkit.core import resize_image_aspect_ratio as resize_image_aspect_ratio
from rdetoolkit.errors import catch_exception_with_message as catch_exception_with_message
from rdetoolkit.exceptions import StructuredError as StructuredError

def copy_images_to_thumbnail(out_dir_thumb_img: str | Path, out_dir_main_img: str | Path, *, target_image_name: str | None = None, img_ext: str | None = None) -> None: ...
def resize_image(path: str | Path, width: int = 640, height: int = 480, output_path: str | Path | None = None) -> str: ...
