import os
import pathlib
import platform
import shutil
from unittest import mock

import pandas as pd
import pytest
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.impl.compressed_controller import (
    CompressedFlatFileParser,
    CompressedFolderParser,
)


@pytest.fixture
def temp_dir():
    os.makedirs("tests/temp", exist_ok=True)
    yield "tests/temp"
    shutil.rmtree("tests/temp")


class TestCompressedFlatFileParser:
    @mock.patch("rdetoolkit.impl.compressed_controller.check_exist_rawfiles")
    def test_read(self, mocker, inputfile_zip_with_file, temp_dir):
        xlsx_invoice = pd.DataFrame()
        expected_files = [(pathlib.Path(temp_dir, "test_child1.txt"),)]

        mocker.return_value = [pathlib.Path(temp_dir, "test_child1.txt")]
        parser = CompressedFlatFileParser(xlsx_invoice)
        files = parser.read(inputfile_zip_with_file, temp_dir)
        assert files == expected_files


class TestCompressedFolderParser:
    def test_read(self, inputfile_zip_with_folder, temp_dir):
        xlsx_invoice = pd.DataFrame()
        parser = CompressedFolderParser(xlsx_invoice)
        files = parser.read(pathlib.Path(inputfile_zip_with_folder), pathlib.Path(temp_dir))

        assert len(files) == 1
        assert len(files[0]) == 2

    def test_unpacked(self, inputfile_zip_with_folder, temp_dir):
        xlsx_invoice = pd.DataFrame()
        parser = CompressedFolderParser(xlsx_invoice)
        files = parser._unpacked(inputfile_zip_with_folder, temp_dir)
        assert len(files) == 2
        assert {f.name for f in files} == {"test_child2.txt", "test_child1.txt"}

    def test_mac_specific_file_unpacked(self, inputfile_mac_zip_with_folder, temp_dir):
        # mac特有のファイルを除外できるかテスト
        xlsx_invoice = pd.DataFrame()
        parser = CompressedFolderParser(xlsx_invoice)
        files = parser._unpacked(inputfile_mac_zip_with_folder, temp_dir)
        assert len(files) == 1
        assert {f.name for f in files} == {"test_child1.txt"}

    def test_microsoft_temp_file_unpacked(self, inputfile_microsoft_tempfile_zip_with_folder, temp_dir):
        # Microfsoft特有のファイルを除外できるかテスト
        xlsx_invoice = pd.DataFrame()
        parser = CompressedFolderParser(xlsx_invoice)
        files = parser._unpacked(inputfile_microsoft_tempfile_zip_with_folder, temp_dir)
        assert len(files) == 1
        assert {f.name for f in files} == {"test_child1.txt"}

    # def test_japanese_temp_file_unpacked(self, inputfile_japanese_tempfile_zip_with_folder, temp_dir):
    #     # 日本語名を含むzipファイルを解凍できるかテスト
    #     xlsx_invoice = pd.DataFrame()
    #     parser = CompressedFolderParser(xlsx_invoice)
    #     files = parser._unpacked(inputfile_japanese_tempfile_zip_with_folder, temp_dir)
    #     assert len(files) == 10
    #     expect_files = {
    #         "テストファイル名１.txt": "これはテストファイル１です。",
    #         "漢字ファイル名.txt": "これは漢字ファイルです。",
    #         "かなファイル名.txt": "これはかなファイルです。",
    #         "カナファイル名.txt": "これはカナファイルです。",
    #         "全角スペースファイル名　.txt": "これは全角スペースファイルです。",
    #         "特殊記号！@＃$.txt": "これは特殊記号ファイルです。",
    #         "括弧（カッコ）.txt": "これは括弧ファイルです。",
    #         "波ダッシュ〜.txt": "これは波ダッシュファイルです。",
    #         "ファイル名_令和３年.txt": "これは令和３年ファイルです。",
    #         "テストデータ①.txt": "これはテストデータ１です。",
    #     }
    #     for file in files:
    #         with open(file, "r", encoding="utf-8") as f:
    #             assert f.read() == expect_files[file.name]

    def test_validation_uniq_fspath(self, temp_dir):
        compressed_filepath1 = pathlib.Path("tests", "temp", "test1.txt")
        compressed_filepath2 = pathlib.Path("tests", "temp", "test2.txt")
        compressed_filepath1.touch()
        compressed_filepath2.touch()

        xlsx_invoice = pd.DataFrame()
        parser = CompressedFolderParser(xlsx_invoice)
        verification_files = parser.validation_uniq_fspath(pathlib.Path("tests/temp"), exclude_names=["invoice_org.json"])

        assert len(verification_files) == 1
        assert "test1.txt" in [p.name for p in verification_files["tests/temp"]]
        assert "test2.txt" in [p.name for p in verification_files["tests/temp"]]

    def test_invalid_validation_uniq_fspath_folder(self, temp_dir):
        # import pdb;pdb.set_trace()
        xlsx_invoice = pd.DataFrame()

        if platform.system() == "Linux":
            pathlib.Path("tests", "temp", "sample").mkdir(parents=True, exist_ok=True)
            pathlib.Path("tests", "temp", "Sample").mkdir(parents=True, exist_ok=True)
            compressed_filepath1 = pathlib.Path("tests", "temp", "sample", "test1.txt")
            compressed_filepath2 = pathlib.Path("tests", "temp", "Sample", "test2.txt")
            compressed_filepath1.touch()
            compressed_filepath2.touch()
            parser = CompressedFolderParser(xlsx_invoice)
            with pytest.raises(StructuredError) as e:
                verification_files = parser.validation_uniq_fspath(pathlib.Path("tests/temp"), exclude_names=["invoice_org.json"])
            assert str(e.value) == "ERROR: folder paths and file paths stored in a zip file must always have unique names."
        else:
            pathlib.Path("tests", "temp", "sample").mkdir(parents=True, exist_ok=True)
            pathlib.Path("tests", "temp", "Sample").mkdir(parents=True, exist_ok=True)
            compressed_filepath1 = pathlib.Path("tests", "temp", "sample", "test1.txt")
            compressed_filepath2 = pathlib.Path("tests", "temp", "Sample", "Test1.txt")
            compressed_filepath1.touch()
            compressed_filepath2.touch()
            parser = CompressedFolderParser(xlsx_invoice)
            verification_files = parser.validation_uniq_fspath(pathlib.Path("tests/temp"), exclude_names=["invoice_org.json"])

            assert len(verification_files) == 1
            assert "test1.txt" in [p.name for p in verification_files["tests/temp/sample"]]

    def test_invalid_validation_uniq_fspath_file(self, temp_dir):
        # import pdb;pdb.set_trace()
        xlsx_invoice = pd.DataFrame()

        if platform.system() == "Linux":
            pathlib.Path("tests", "temp", "sample").mkdir(parents=True, exist_ok=True)
            pathlib.Path("tests", "temp", "Sample").mkdir(parents=True, exist_ok=True)
            compressed_filepath1 = pathlib.Path("tests", "temp", "sample", "test1.txt")
            compressed_filepath2 = pathlib.Path("tests", "temp", "sample", "Test1.txt")
            compressed_filepath1.touch()
            compressed_filepath2.touch()
            parser = CompressedFolderParser(xlsx_invoice)
            with pytest.raises(StructuredError) as e:
                verification_files = parser.validation_uniq_fspath(pathlib.Path("tests/temp"), exclude_names=["invoice_org.json"])
            assert str(e.value) == "ERROR: folder paths and file paths stored in a zip file must always have unique names."
        else:
            pathlib.Path("tests", "temp", "sample").mkdir(parents=True, exist_ok=True)
            pathlib.Path("tests", "temp", "Sample").mkdir(parents=True, exist_ok=True)
            compressed_filepath1 = pathlib.Path("tests", "temp", "sample", "test1.txt")
            compressed_filepath2 = pathlib.Path("tests", "temp", "Sample", "Test1.txt")
            compressed_filepath1.touch()
            compressed_filepath2.touch()
            parser = CompressedFolderParser(xlsx_invoice)
            verification_files = parser.validation_uniq_fspath(pathlib.Path("tests/temp"), exclude_names=["invoice_org.json"])

            assert len(verification_files) == 1
            assert "test1.txt" in [p.name for p in verification_files["tests/temp/sample"]]
