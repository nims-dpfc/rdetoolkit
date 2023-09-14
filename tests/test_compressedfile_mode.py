import os
import pathlib
import shutil
from unittest import mock

import pandas as pd
import pytest
from src.rdetoolkit.impl.compressed_controller import (
    CompressedFlatFileParser, CompressedFolderParser)


@pytest.fixture
def temp_dir():
    os.makedirs("tests/temp", exist_ok=True)
    yield "tests/temp"
    shutil.rmtree("tests/temp")


class TestCompressedFlatFileParser:
    @mock.patch("src.rdetoolkit.impl.compressed_controller.checkExistRawFiles")
    def test_read(self, mocker, inputfile_zip_with_file, temp_dir):
        xlsx_invoice = pd.DataFrame()
        expected_files = [
            (pathlib.Path(temp_dir, "test_child1.txt"),)
        ]

        mocker.return_value = [pathlib.Path(temp_dir, "test_child1.txt")]
        parser = CompressedFlatFileParser(xlsx_invoice)
        files =  parser.read(inputfile_zip_with_file, temp_dir)
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
        assert set([f.name for f in files]) == {"test_child2.txt", "test_child1.txt"}

    def test_validation_uniq_dirname(self, temp_dir):
        compressed_filepath1 = pathlib.Path("tests", "temp", "test1.txt")
        compressed_filepath2 = pathlib.Path("tests", "temp", "test2.txt")
        compressed_filepath1.touch()
        compressed_filepath2.touch()

        xlsx_invoice = pd.DataFrame()
        parser = CompressedFolderParser(xlsx_invoice)
        verification_files = parser.validation_uniq_dirname(pathlib.Path("tests/temp"), exclude_names=["invoice_org.json"])

        assert len(verification_files) == 1
        assert "test1.txt" in [p.name for p in verification_files["tests/temp"]]
        assert "test2.txt" in [p.name for p in verification_files["tests/temp"]]
