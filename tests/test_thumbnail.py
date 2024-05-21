import os
import shutil
from pathlib import Path

import pytest
from rdetoolkit.img2thumb import copy_images_to_thumbnail


@pytest.fixture
def dummy_out_dir_thumb():
    temp_dir_path = Path("tests", "img")
    temp_dir_path.mkdir(parents=True, exist_ok=True)

    OUT_DIR_THUB_IMG = temp_dir_path.joinpath("thumb_img")
    OUT_DIR_THUB_IMG.mkdir(parents=True, exist_ok=True)

    yield OUT_DIR_THUB_IMG

    if os.path.exists(temp_dir_path):
        shutil.rmtree(temp_dir_path)


@pytest.fixture
def dummy_out_dir_main():
    temp_dir_path = Path("tests", "img")
    temp_dir_path.mkdir(parents=True, exist_ok=True)

    OUT_DIR_MAIN_IMG = temp_dir_path.joinpath("main_img")
    OUT_DIR_MAIN_IMG.mkdir(parents=True, exist_ok=True)

    yield OUT_DIR_MAIN_IMG

    if os.path.exists(temp_dir_path):
        shutil.rmtree(temp_dir_path)


@pytest.fixture
def dummy_out_dir_other():
    temp_dir_path = Path("tests", "img")
    temp_dir_path.mkdir(parents=True, exist_ok=True)

    OUT_DIR_OTHER_IMG = temp_dir_path.joinpath("other_img")
    OUT_DIR_OTHER_IMG.mkdir(parents=True, exist_ok=True)

    yield OUT_DIR_OTHER_IMG

    if os.path.exists(temp_dir_path):
        shutil.rmtree(temp_dir_path)


def test_copy_images_to_thumbnail(dummy_out_dir_thumb, dummy_out_dir_main, dummy_out_dir_other):
    """Main画像フォルダにあるファイル1つがサムネイルフォルダにファイルがコピーされるかテスト"""
    # ダミー画像ファイルを作成
    with open(dummy_out_dir_main.joinpath("dummy_main_img.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_other.joinpath("dummy_other_img.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_other.joinpath("dummy_other_img2.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_other.joinpath("dummy_other_img3.png"), "w") as f:
        f.write("dummy")
    # 関数を実行
    copy_images_to_thumbnail(dummy_out_dir_thumb, dummy_out_dir_main)

    assert len(list(dummy_out_dir_thumb.glob("*"))) == 1


def test_only_one_representative_image_exists(dummy_out_dir_thumb, dummy_out_dir_main, dummy_out_dir_other):
    """thumbnailフォルダにファイル名!_とついたファイル数が0かチェックするテスト
    RDE v5に伴う仕様の変更により、!_をファイルの先頭に付与する必要がなくなったため
    """
    # ダミー画像ファイルを作成
    with open(dummy_out_dir_main.joinpath("dummy_main_img.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_other.joinpath("dummy_other_img.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_other.joinpath("dummy_other_img2.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_other.joinpath("dummy_other_img3.png"), "w") as f:
        f.write("dummy")
    # 関数を実行
    copy_images_to_thumbnail(dummy_out_dir_thumb, dummy_out_dir_main)

    representative_imgs = list(dummy_out_dir_thumb.glob("!_*"))
    assert len(representative_imgs) == 0


def test_specifying_a_file(dummy_out_dir_thumb, dummy_out_dir_main, dummy_out_dir_other):
    """main_imageに存在する指定したファイル名の画像が代表画像にコピーされるかテスト
    """
    # ダミー画像ファイルを作成
    with open(dummy_out_dir_main.joinpath("dummy_main_img1.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_main.joinpath("dummy_main_img2.png"), "w") as f:
        f.write("dummy")
    with open(dummy_out_dir_main.joinpath("dummy_main_img3.png"), "w") as f:
        f.write("dummy")
    # 関数を実行
    copy_images_to_thumbnail(dummy_out_dir_thumb, dummy_out_dir_main, target_image_name="dummy_main_img3.png")

    assert dummy_out_dir_thumb.joinpath("dummy_main_img3.png").exists()


def test_copy_images_to_thumbnail_mismatch_extension(dummy_out_dir_thumb, dummy_out_dir_main):
    """拡張子が指定と違った場合、ファイルがコピーされないことを確認するテスト"""
    # ダミー画像ファイルを作成
    with open(dummy_out_dir_main.joinpath("dummy_main_img.jpg"), "w") as f:
        f.write("dummy")
    # 関数を実行
    copy_images_to_thumbnail(dummy_out_dir_thumb, dummy_out_dir_main)

    assert not os.path.isfile(dummy_out_dir_thumb.joinpath("!_dummy_main_img.png"))
