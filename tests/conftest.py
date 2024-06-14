import os
import pathlib
import shutil
import zipfile
from typing import Generator

import pytest
import yaml

pytest_plugins = (
    "tests.fixtures.excelinvoice",
    "tests.fixtures.invoice",
    "tests.fixtures.schema",
    "tests.fixtures.metadata_json",
)


@pytest.fixture
def inputfile_single() -> Generator[str, None, None]:
    """Create a temporary file for test input"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    # setup
    empty_single_file = pathlib.Path(input_dir, "test_single.txt")
    empty_single_file.touch()
    yield str(empty_single_file)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_multi() -> Generator[list[pathlib.Path], None, None]:
    """Create multiple files temporarily for test input"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    # setup
    empty_child_file_1 = pathlib.Path(input_dir, "test_child1.txt")
    empty_child_file_1.touch()
    empty_child_file_2 = pathlib.Path(input_dir, "test_child2.txt")
    empty_child_file_2.touch()

    yield [empty_child_file_1, empty_child_file_2]

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_zip_with_file() -> Generator[str, None, None]:
    """ファイルのみを圧縮したzip"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_zip_root_foldername = pathlib.Path("test_input_multi.zip")
    test_zip_filepath = pathlib.Path(input_dir, test_zip_root_foldername)

    compressed_filepath1 = pathlib.Path("test_child1.txt")
    compressed_filepath1.touch()

    # setup
    with zipfile.ZipFile(str(test_zip_filepath), "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(str(compressed_filepath1))

    yield str(test_zip_filepath)

    # teardown
    if os.path.exists(compressed_filepath1):
        os.remove(str(compressed_filepath1))
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_zip_with_folder() -> Generator[str, None, None]:
    """単一のフォルダを圧縮したzip"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_zip_filepath = pathlib.Path(input_dir, "test_input_multi")

    zip_root_dirpath = pathlib.Path("compdir")
    compressed_filepath1 = pathlib.Path(zip_root_dirpath, "test_child1.txt")
    compressed_filepath2 = pathlib.Path(zip_root_dirpath, "test_child2.txt")

    # setup
    zip_root_dirpath.mkdir(exist_ok=True)
    compressed_filepath1.touch()
    compressed_filepath2.touch()
    zip_file = shutil.make_archive(str(test_zip_filepath), format="zip", root_dir=zip_root_dirpath)

    yield str(zip_file)

    # teardown
    if os.path.exists(zip_root_dirpath):
        shutil.rmtree(zip_root_dirpath)
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_mac_zip_with_folder() -> Generator[str, None, None]:
    """mac特有のファイルを含むファイルを圧縮したzip"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_zip_filepath = pathlib.Path(input_dir, "test_input_multi")

    zip_root_dirpath = pathlib.Path("compdir")
    compressed_filepath1 = pathlib.Path(zip_root_dirpath, "test_child1.txt")
    compressed_filepath2 = pathlib.Path(zip_root_dirpath, ".DS_Store")
    macfolder = pathlib.Path(zip_root_dirpath, "__MACOSX")
    macfolder.mkdir(parents=True, exist_ok=True)
    compressed_filepath3 = pathlib.Path(macfolder, "dummy.txt")

    # setup
    zip_root_dirpath.mkdir(exist_ok=True)
    compressed_filepath1.touch()
    compressed_filepath2.touch()
    compressed_filepath3.touch()
    zip_file = shutil.make_archive(str(test_zip_filepath), format="zip", root_dir=zip_root_dirpath)
    zip_file = shutil.make_archive(str(test_zip_filepath), format="zip", root_dir=zip_root_dirpath)

    yield str(zip_file)

    # teardown
    if os.path.exists(zip_root_dirpath):
        shutil.rmtree(zip_root_dirpath)
    if macfolder.exists():
        shutil.rmtree(macfolder)
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_microsoft_tempfile_zip_with_folder() -> Generator[str, None, None]:
    """Microsoft特有のファイルを一時ファイル含むファイルを圧縮したzip"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_zip_filepath = pathlib.Path(input_dir, "test_input_multi")

    zip_root_dirpath = pathlib.Path("compdir")
    compressed_filepath1 = pathlib.Path(zip_root_dirpath, "test_child1.txt")
    ms_temp_xlsx = pathlib.Path(zip_root_dirpath, "~$temp.xlsx")
    ms_temp_pptx = pathlib.Path(zip_root_dirpath, "~$temp.pptx")
    ms_temp_docx = pathlib.Path(zip_root_dirpath, "~$temp.docx")

    # setup
    zip_root_dirpath.mkdir(exist_ok=True)
    compressed_filepath1.touch()
    ms_temp_docx.touch()
    ms_temp_pptx.touch()
    ms_temp_xlsx.touch()
    zip_file = shutil.make_archive(str(test_zip_filepath), format="zip", root_dir=zip_root_dirpath)

    yield str(zip_file)

    # teardown
    if os.path.exists(zip_root_dirpath):
        shutil.rmtree(zip_root_dirpath)
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_zip_with_folder_multi() -> Generator[str, None, None]:
    """フォルダを複数圧縮したzip"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_zip_filepath = pathlib.Path(input_dir, "test_input_multi")

    zip_root_dirpath1 = pathlib.Path("pack", "data1")
    zip_root_dirpath2 = pathlib.Path("pack", "data2")
    compressed_filepath1 = pathlib.Path(zip_root_dirpath1, "test_child1.txt")
    compressed_filepath2 = pathlib.Path(zip_root_dirpath2, "test_child2.txt")

    # setup
    zip_root_dirpath1.mkdir(exist_ok=True, parents=True)
    zip_root_dirpath2.mkdir(exist_ok=True, parents=True)
    compressed_filepath1.touch()
    compressed_filepath2.touch()
    zip_file = shutil.make_archive(str(test_zip_filepath), format="zip", root_dir="pack")
    yield str(zip_file)

    # teardown
    if os.path.exists(zip_root_dirpath1):
        shutil.rmtree(zip_root_dirpath1)
    if os.path.exists(zip_root_dirpath2):
        shutil.rmtree(zip_root_dirpath2)
    if os.path.exists("pack"):
        shutil.rmtree("pack")
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def tasksupport() -> Generator[list[str], None, None]:
    tasksupport_dir = pathlib.Path("data", "tasksupport")
    tasksupport_dir.mkdir(parents=True, exist_ok=True)
    empty_defcsv = pathlib.Path(tasksupport_dir, "default_value.csv")
    empty_defcsv.touch()
    empty_schema = pathlib.Path(tasksupport_dir, "invoice.schema.json")
    empty_schema.touch()
    empty_defjson = pathlib.Path(tasksupport_dir, "metadata-def.json")
    empty_defjson.touch()

    dirname = pathlib.Path("data/tasksupport")
    data = {"extended_mode": None, "save_raw": True, "save_thumbnail_image": True, "magic_variable": False}
    test_yaml_path = dirname.joinpath("rdeconfig.yml")
    with open(test_yaml_path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    yield [str(empty_defcsv), str(empty_schema), str(empty_defjson), str(test_yaml_path)]

    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def tasksupport_empty_config() -> Generator[list[str], None, None]:
    tasksupport_dir = pathlib.Path("data", "tasksupport")
    tasksupport_dir.mkdir(parents=True, exist_ok=True)
    empty_defcsv = pathlib.Path(tasksupport_dir, "default_value.csv")
    empty_defcsv.touch()
    empty_schema = pathlib.Path(tasksupport_dir, "invoice.schema.json")
    empty_schema.touch()
    empty_defjson = pathlib.Path(tasksupport_dir, "metadata-def.json")
    empty_defjson.touch()

    dirname = pathlib.Path("data/tasksupport")
    data = {}
    test_yaml_path = dirname.joinpath("rdeconfig.yml")
    with open(test_yaml_path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    yield [str(empty_defcsv), str(empty_schema), str(empty_defjson), str(test_yaml_path)]

    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def inputfile_rdeformat() -> Generator[str, None, None]:
    """rdeformat用のフォルダ群を圧縮 (1ファイル入力/dividedなし)"""
    output_struct_dir_names = ("inputdata", "invoice", "raw", "main_image", "other_image", "thumbnail", "structured", "meta", "logs", "tasksupport")
    for name in output_struct_dir_names:
        _dir = pathlib.Path("data", name)
        _dir.mkdir(parents=True, exist_ok=True)

    compressed_filepath1 = pathlib.Path("data", "inputdata", "test_child1.txt")
    compressed_filepath1.touch()

    compressed_raw_filepath = pathlib.Path("data", "raw", "test_child1.txt")
    compressed_raw_filepath.touch()

    compressed_struct_filepath = pathlib.Path("data", "structured", "test.csv")
    compressed_struct_filepath.touch()

    zip_file = shutil.make_archive("rdeformat_pack", format="zip", root_dir="data")
    if os.path.exists("data"):
        shutil.rmtree("data")

    # setup
    output_struct_dir_names_min = ("inputdata", "invoice", "tasksupport")
    for name in output_struct_dir_names_min:
        _dir = pathlib.Path("data", name)
        _dir.mkdir(parents=True, exist_ok=True)
    shutil.move(zip_file, pathlib.Path("data", "inputdata"))
    rdeformat_flag_filepath = pathlib.Path("data", "tasksupport", "rdeformat.txt")
    rdeformat_flag_filepath.touch()

    yield str(zip_file)

    # teardown
    if os.path.exists(zip_file):
        shutil.rmtree(zip_file)
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def inputfile_rdeformat_divived() -> Generator[str, None, None]:
    """rdeformat用のフォルダ群を圧縮 (複数ファイル入力/divided)"""
    output_struct_dir_names = ("inputdata", "invoice", "raw", "main_image", "other_image", "thumbnail", "structured", "meta", "logs", "tasksupport")
    # root directory
    for name in output_struct_dir_names:
        _dir = pathlib.Path("data", name)
        _dir.mkdir(parents=True, exist_ok=True)

        if name == "inputdata":
            comp_input = pathlib.Path("data", "inputdata", "test_file0.txt")
            comp_input.touch()
        elif name == "raw":
            comp_raw = pathlib.Path("data", "raw", "test_file0.txt")
            comp_raw.touch()
        elif name == "structured":
            comp_struct = pathlib.Path("data", "structured", "test.csv")
            comp_struct.touch()

    # diveided directory
    for idx in range(1, 3):
        for name in output_struct_dir_names:
            _dir = pathlib.Path("data", "divided", f"{idx:04}", name)
            _dir.mkdir(parents=True, exist_ok=True)
        comp_input = pathlib.Path("data", "divided", f"{idx:04}", "inputdata", f"test_file{idx}.txt")
        comp_input.touch()
        comp_raw = pathlib.Path("data", "divided", f"{idx:04}", "raw", f"test_file{idx}.txt")
        comp_raw.touch()
        comp_struct = pathlib.Path("data", "divided", f"{idx:04}", "structured", f"test_file{idx}.csv")
        comp_struct.touch()

    zip_file = shutil.make_archive("rdeformat_pack", format="zip", root_dir="data")
    if os.path.exists("data"):
        shutil.rmtree("data")

    # setup
    output_struct_dir_names_min = ("inputdata", "invoice", "tasksupport")
    for name in output_struct_dir_names_min:
        _dir = pathlib.Path("data", name)
        _dir.mkdir(parents=True, exist_ok=True)
    shutil.move(zip_file, pathlib.Path("data", "inputdata"))
    rdeformat_flag_filepath = pathlib.Path("data", "tasksupport", "rdeformat.txt")
    rdeformat_flag_filepath.touch()

    yield str(zip_file)

    # teardown
    if os.path.exists(zip_file):
        shutil.rmtree(zip_file)
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def inputfile_multimode() -> Generator[str, None, None]:
    """multiモード"""
    os.makedirs(os.path.join("data", "tasksupport"), exist_ok=True)
    multi_flag_filepath = pathlib.Path("data", "tasksupport", "multifile.txt")
    multi_flag_filepath.touch()

    yield str(multi_flag_filepath)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")
