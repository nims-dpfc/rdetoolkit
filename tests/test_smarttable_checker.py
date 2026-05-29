"""Test SmartTableChecker functionality.

Equivalence Partitioning:
| API | Input/State Partition | Rationale | Expected Outcome | Test ID |
| --- | --- | --- | --- | --- |
| ``SmartTableChecker.parse`` + ``generate_folder_paths_iterator`` | SmartTable mode with saved table file | valid domain | table file is in data/ root and row CSVs populate divided folders | TC-EP-SMARTTABLE-ITER-001 |
| ``SmartTableChecker.parse`` + ``generate_folder_paths_iterator`` | SmartTable mode without saved table file | valid domain | last row is in data/ root and earlier row CSVs populate divided folders | TC-EP-SMARTTABLE-ITER-002 |

Boundary Value:
| API | Boundary | Rationale | Expected Outcome | Test ID |
| --- | --- | --- | --- | --- |
| ``SmartTableChecker.parse`` + ``generate_folder_paths_iterator`` | two generated data rows | minimum row count that exercises root/divided reordering | rowfile mapping follows RDE registration order | TC-BV-SMARTTABLE-ITER-001 |

Validation commands:
Direct: ``uv run pytest tests/test_smarttable_checker.py tests/test_generate_folder_paths_iterator.py -q``
Tox: ``tox -e py312-module -- tests/test_smarttable_checker.py tests/test_generate_folder_paths_iterator.py``
"""

from pathlib import Path
import pytest
import zipfile
from unittest.mock import Mock, patch

from rdetoolkit.impl.input_controller import SmartTableChecker
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.workflows import generate_folder_paths_iterator


class TestSmartTableChecker:
    """Test suite for SmartTableChecker functionality."""

    def test_checker_type(self):
        """Test that checker_type returns correct value."""
        checker = SmartTableChecker(Path("data/temp"))
        assert checker.checker_type == "smarttable"

    def test_parse_with_excel_file(self, tmp_path):
        """Test parsing with SmartTable Excel file."""
        # Create test files
        smarttable_file = tmp_path / "smarttable_test.xlsx"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), (Path("file1.txt"),)),
                (Path("data/temp/row_1.csv"), (Path("file2.txt"),)),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=True)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            assert len(rawfiles) == 3
            # idx=0 -> data/ root: SmartTable file (registered last by RDE)
            assert rawfiles[0] == (smarttable_file,)
            # idx>=1 -> data/divided/000N: data rows in table order
            assert rawfiles[1] == (Path("data/temp/row_0.csv"), Path("file1.txt"))
            assert rawfiles[2] == (Path("data/temp/row_1.csv"), Path("file2.txt"))
            assert smarttable_path == smarttable_file

    def test_parse_with_csv_file(self, tmp_path):
        """Test parsing with SmartTable CSV file."""
        smarttable_file = tmp_path / "smarttable_data.csv"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), ()),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=True)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            assert len(rawfiles) == 2
            # idx=0 -> data/ root: SmartTable file (registered last by RDE)
            assert rawfiles[0] == (smarttable_file,)
            # idx=1 -> data/divided/0001: data row
            assert rawfiles[1] == (Path("data/temp/row_0.csv"),)
            assert smarttable_path == smarttable_file

    def test_parse_with_tsv_file(self, tmp_path):
        """Test parsing with SmartTable TSV file."""
        smarttable_file = tmp_path / "smarttable_experiment.tsv"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), (Path("data1.txt"), Path("data2.txt"))),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=True)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            assert len(rawfiles) == 2
            # idx=0 -> data/ root: SmartTable file (registered last by RDE)
            assert rawfiles[0] == (smarttable_file,)
            # idx=1 -> data/divided/0001: data row with related files
            assert rawfiles[1] == (Path("data/temp/row_0.csv"), Path("data1.txt"), Path("data2.txt"))
            assert smarttable_path == smarttable_file

    def test_parse_with_zip_file(self, tmp_path):
        """Test parsing with SmartTable file and zip file."""
        # Create SmartTable file
        smarttable_file = tmp_path / "smarttable_with_zip.xlsx"
        smarttable_file.touch()

        # Create zip file with test content
        zip_file = tmp_path / "test_data.zip"
        test_content = tmp_path / "test_content.txt"
        test_content.write_text("test data")

        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.write(test_content, "test_content.txt")

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), (Path("data/temp/test_content.txt"),)),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=True)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            assert len(rawfiles) == 2
            # idx=0 -> data/ root: SmartTable file (registered last by RDE)
            assert rawfiles[0] == (smarttable_file,)
            # idx=1 -> data/divided/0001: data row with extracted file
            assert rawfiles[1] == (Path("data/temp/row_0.csv"), Path("data/temp/test_content.txt"))
            assert smarttable_path == smarttable_file

    def test_parse_no_smarttable_files(self, tmp_path):
        """Test parsing when no SmartTable files are found."""
        # Create non-SmartTable files
        (tmp_path / "regular_file.txt").touch()
        (tmp_path / "data.xlsx").touch()  # Excel file but doesn't start with smarttable_

        checker = SmartTableChecker(Path("data/temp"))

        with pytest.raises(StructuredError) as exc_info:
            checker.parse(tmp_path)

        assert "No SmartTable files found" in str(exc_info.value)

    def test_parse_multiple_smarttable_files(self, tmp_path):
        """Test parsing when multiple SmartTable files are found."""
        # Create multiple SmartTable files
        (tmp_path / "smarttable_1.xlsx").touch()
        (tmp_path / "smarttable_2.csv").touch()

        checker = SmartTableChecker(Path("data/temp"))

        with pytest.raises(StructuredError) as exc_info:
            checker.parse(tmp_path)

        assert "Multiple SmartTable files found" in str(exc_info.value)

    def test_parse_invalid_extension(self, tmp_path):
        """Test parsing with invalid file extension."""
        # Create file with smarttable_ prefix but invalid extension
        (tmp_path / "smarttable_data.txt").touch()

        checker = SmartTableChecker(Path("data/temp"))

        with pytest.raises(StructuredError) as exc_info:
            checker.parse(tmp_path)

        assert "No SmartTable files found" in str(exc_info.value)

    def test_unpacked_smarttable_functionality(self, tmp_path):
        """Test the _unpacked_smarttable method."""
        # Create test zip file
        zip_file = tmp_path / "test.zip"
        test_file = tmp_path / "source.txt"
        test_file.write_text("test content")

        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.write(test_file, "extracted.txt")

        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()

        checker = SmartTableChecker(temp_dir)
        extracted_files = checker._unpacked_smarttable(zip_file)

        assert len(extracted_files) == 1
        assert extracted_files[0].name == "extracted.txt"
        assert extracted_files[0].is_file()

    def test_edge_case_empty_directory(self, tmp_path):
        """Test parsing with empty directory."""
        checker = SmartTableChecker(Path("data/temp"))

        with pytest.raises(StructuredError) as exc_info:
            checker.parse(tmp_path)

        assert "No SmartTable files found" in str(exc_info.value)

    def test_case_insensitive_extensions(self, tmp_path):
        """Test that file extensions are handled case-insensitively."""
        smarttable_file = tmp_path / "smarttable_test.XLSX"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), ()),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=True)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            assert len(rawfiles) == 2
            # idx=0 -> data/ root: SmartTable file (registered last by RDE)
            assert rawfiles[0] == (smarttable_file,)
            # idx=1 -> data/divided/0001: data row
            assert rawfiles[1] == (Path("data/temp/row_0.csv"),)
            assert smarttable_path == smarttable_file

    def test_multiple_zip_files_handling(self, tmp_path):
        """Test handling multiple zip files."""
        # Create SmartTable file
        smarttable_file = tmp_path / "smarttable_test.xlsx"
        smarttable_file.touch()

        # Create multiple zip files
        for i in range(2):
            zip_file = tmp_path / f"data_{i}.zip"
            test_file = tmp_path / f"source_{i}.txt"
            test_file.write_text(f"test content {i}")

            with zipfile.ZipFile(zip_file, 'w') as zf:
                zf.write(test_file, f"extracted_{i}.txt")

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            # Mock should be called with extracted files from both zips
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), (Path("data/temp/extracted_0.txt"), Path("data/temp/extracted_1.txt"))),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=True)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            assert len(rawfiles) == 2
            # idx=0 -> data/ root: SmartTable file (registered last by RDE)
            assert rawfiles[0] == (smarttable_file,)
            # idx=1 -> data/divided/0001: data row (CSV file + 2 extracted files)
            assert len(rawfiles[1]) == 3  # CSV file + 2 extracted files
            assert rawfiles[1][0] == Path("data/temp/row_0.csv")  # CSV file first within the tuple
            assert smarttable_path == smarttable_file

    def test_save_table_file_false(self, tmp_path):
        """Test that when save_table_file=False, SmartTable file is not included in rawfiles."""
        # Create test files
        smarttable_file = tmp_path / "smarttable_test.xlsx"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), (Path("file1.txt"),)),
                (Path("data/temp/row_1.csv"), (Path("file2.txt"),)),
            ]

            # Default behavior: save_table_file=False
            checker = SmartTableChecker(Path("data/temp"))
            rawfiles, smarttable_path = checker.parse(tmp_path)

            # SmartTable file is excluded; the LAST row occupies data/ root (registered
            # last by RDE) so registration order stays row_0 -> row_1.
            assert len(rawfiles) == 2
            assert rawfiles[0] == (Path("data/temp/row_1.csv"), Path("file2.txt"))  # idx=0 -> data/ root (last row)
            assert rawfiles[1] == (Path("data/temp/row_0.csv"), Path("file1.txt"))  # idx=1 -> data/divided/0001 (first row)
            assert smarttable_path == smarttable_file

    def test_save_table_file_explicit_false(self, tmp_path):
        """Test explicit save_table_file=False behavior."""
        smarttable_file = tmp_path / "smarttable_data.csv"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), ()),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=False)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            # Only CSV files should be in rawfiles
            assert len(rawfiles) == 1
            assert rawfiles[0] == (Path("data/temp/row_0.csv"),)
            assert smarttable_path == smarttable_file

    def test_parse_save_table_file_true_table_at_data_root(self, tmp_path):
        """Test SmartTable file goes to data/ root when save_table_file=True.

        The RDE system registers data/divided/0001..N first and data/ root LAST,
        so placing the SmartTable file at idx=0 (data/ root) makes data rows
        register in table order (row1, row2, ...) followed by the table file:
        - idx=0 → data/ root (SmartTable file, registered last)
        - idx=1 → data/divided/0001/ (first data row)
        - idx=2 → data/divided/0002/ (second data row)
        """
        smarttable_file = tmp_path / "smarttable_test.xlsx"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), (Path("file1.txt"),)),
                (Path("data/temp/row_1.csv"), (Path("file2.txt"),)),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=True)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            # SmartTable file occupies data/ root; data rows fill divided in table order
            assert len(rawfiles) == 3
            assert rawfiles[0] == (smarttable_file,)  # idx=0 -> data/ root (registered last)
            assert rawfiles[1] == (Path("data/temp/row_0.csv"), Path("file1.txt"))  # idx=1 -> 1st data row
            assert rawfiles[2] == (Path("data/temp/row_1.csv"), Path("file2.txt"))  # idx=2 -> 2nd data row
            assert smarttable_path == smarttable_file

    def test_parse_save_table_file_false_last_row_first(self, tmp_path):
        """Test the LAST data row goes to data/ root when save_table_file=False.

        The RDE system registers data/divided/0001..N first and data/ root LAST, and
        data/ root must always be registered. With no SmartTable file to occupy it,
        the final data row is placed at idx=0 so registration order stays row_0..row_2:
        - idx=0 → data/ root (row_2, the last row, registered last)
        - idx=1 → data/divided/0001/ (row_0, the first row)
        - idx=2 → data/divided/0002/ (row_1, the second row)
        """
        smarttable_file = tmp_path / "smarttable_test.xlsx"
        smarttable_file.touch()

        with patch('rdetoolkit.impl.input_controller.SmartTableFile') as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (Path("data/temp/row_0.csv"), (Path("file0.txt"),)),
                (Path("data/temp/row_1.csv"), (Path("file1.txt"),)),
                (Path("data/temp/row_2.csv"), (Path("file2.txt"),)),
            ]

            checker = SmartTableChecker(Path("data/temp"), save_table_file=False)
            rawfiles, smarttable_path = checker.parse(tmp_path)

            assert len(rawfiles) == 3
            assert rawfiles[0] == (Path("data/temp/row_2.csv"), Path("file2.txt"))  # idx=0 -> data/ root (last row)
            assert rawfiles[1] == (Path("data/temp/row_0.csv"), Path("file0.txt"))  # idx=1 -> data/divided/0001 (first row)
            assert rawfiles[2] == (Path("data/temp/row_1.csv"), Path("file1.txt"))  # idx=2 -> data/divided/0002 (second row)
            assert smarttable_path == smarttable_file

    @pytest.mark.parametrize(
        ("save_table_file", "expected_rawfiles", "expected_rowfiles"),
        [
            (
                True,
                [
                    ["smarttable_test.xlsx"],
                    ["fsmarttable_test_0000.csv", "file0.txt"],
                    ["fsmarttable_test_0001.csv", "file1.txt"],
                ],
                [None, "fsmarttable_test_0000.csv", "fsmarttable_test_0001.csv"],
            ),
            (
                False,
                [
                    ["fsmarttable_test_0001.csv", "file1.txt"],
                    ["fsmarttable_test_0000.csv", "file0.txt"],
                ],
                ["fsmarttable_test_0001.csv", "fsmarttable_test_0000.csv"],
            ),
        ],
    )
    def test_parse_to_generate_folder_paths_iterator_keeps_smarttable_order__tc_ep_smarttable_iter_001_002(
        self,
        tmp_path,
        save_table_file,
        expected_rawfiles,
        expected_rowfiles,
    ):
        """Test SmartTable parse output as generate_folder_paths_iterator input."""
        # Given: a SmartTable file whose generated row CSVs follow table order.
        smarttable_file = tmp_path / "smarttable_test.xlsx"
        smarttable_file.touch()
        row0 = tmp_path / "fsmarttable_test_0000.csv"
        row1 = tmp_path / "fsmarttable_test_0001.csv"
        related0 = tmp_path / "file0.txt"
        related1 = tmp_path / "file1.txt"
        invoice_org_json = tmp_path / "invoice_org.json"
        invoice_schema_json = tmp_path / "invoice.schema.json"

        with patch("rdetoolkit.impl.input_controller.SmartTableFile") as mock_st:
            mock_instance = Mock()
            mock_st.return_value = mock_instance
            mock_instance.generate_row_csvs_with_file_mapping.return_value = [
                (row0, (related0,)),
                (row1, (related1,)),
            ]

            checker = SmartTableChecker(tmp_path / "temp", save_table_file=save_table_file)

            # When: parse output is consumed by the RDE folder path iterator.
            rawfiles, _ = checker.parse(tmp_path)
            resources = list(
                generate_folder_paths_iterator(
                    rawfiles,
                    invoice_org_json,
                    invoice_schema_json,
                    smarttable_mode=True,
                ),
            )

        # Then: raw file ordering and SmartTable rowfile detection preserve registration order.
        assert [[path.name for path in resource.rawfiles] for resource in resources] == expected_rawfiles
        assert [
            resource.smarttable_rowfile.name if resource.smarttable_rowfile is not None else None
            for resource in resources
        ] == expected_rowfiles
