"""Unit tests for the shared zip filename encoding helper (issue #515).

``rdetoolkit.impl._zip_encoding.resolve_filename`` decides what filename a zip
entry should be extracted under. ``zipfile`` has already decoded the name by the
time it is called -- as UTF-8 when the language encoding flag (general purpose
bit 11, ``0x800``) is set, otherwise as cp437 -- so this function's job is to
decide whether that decoding can be trusted and repair it when it cannot.

These tests target ``resolve_filename`` directly, rather than through an
extraction call, so that the fallback branches can be exercised in isolation.
End-to-end coverage through the checkers lives in
``tests/test_smarttable_checker_zip_encoding.py``.

Equivalence Partitioning:
| Input/State Partition | Rationale | Expected Outcome | Test ID |
| --- | --- | --- | --- |
| UTF-8 flag set | spec guarantees UTF-8; zipfile already correct | name returned verbatim, no detection | TC-EP-RESOLVE-001 |
| cp932 bytes, flag unset | legacy Japanese Windows zip (the issue #515 bug) | name recovered as cp932 | TC-EP-RESOLVE-002 |
| ASCII bytes, flag unset | common case | name unchanged | TC-EP-RESOLVE-003 |
| bytes cp932 cannot decode, flag unset | non-Japanese legacy zip | falls back to detection, never raises | TC-EP-RESOLVE-004 |
| detection returns an unusable codec | heuristic failure | warns and keeps zipfile's name; never raises | TC-EP-RESOLVE-005 |
| detection returns None | heuristic yields nothing | falls back to cp437 (zipfile's own default) | TC-EP-RESOLVE-006 |

Validation commands:
Direct: ``uv run pytest tests/test_zip_encoding.py -v``
Tox: ``tox -e py312-module -- tests/test_zip_encoding.py``
"""

from __future__ import annotations

import zipfile

import pytest

from rdetoolkit.impl import _zip_encoding
from rdetoolkit.impl._zip_encoding import LANG_ENC_FLAG, resolve_filename


def _zip_info_for(raw_name: bytes, *, utf8_flag: bool) -> zipfile.ZipInfo:
    """Build a ZipInfo as ``zipfile`` would present it after parsing an archive.

    Args:
        raw_name: The filename bytes as stored in the archive.
        utf8_flag: Whether the entry advertises UTF-8 (general purpose bit 11).

    Returns:
        zipfile.ZipInfo: Entry whose ``filename`` is decoded the way ``zipfile``
            itself would decode it, and whose ``flag_bits`` match ``utf8_flag``.
    """
    info = zipfile.ZipInfo()
    info.filename = raw_name.decode("utf-8" if utf8_flag else "cp437")
    info.flag_bits = LANG_ENC_FLAG if utf8_flag else 0
    return info


class TestResolveFilename:
    """Issue #515: recovering true filenames from non-UTF-8 zip entries."""

    def test_utf8_flagged_name_is_returned_verbatim(self) -> None:
        """TC-EP-RESOLVE-001: a flagged name is trusted without detection."""
        # Given: an entry that advertises UTF-8, as modern zip tools produce.
        name = "日本語ファイル.txt"
        info = _zip_info_for(name.encode("utf-8"), utf8_flag=True)

        # When: resolving the filename.
        result = resolve_filename(info)

        # Then: zipfile's decoding is trusted as-is.
        assert result == name

    def test_utf8_flagged_name_skips_detection_entirely(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-EP-RESOLVE-001: detection must not run for flagged entries.

        Detection is heuristic and mis-reads short names, so a name the spec
        already guarantees to be correct must never be passed through it.
        """
        # Given: detection that fails loudly if it is ever consulted.
        def _boom(_: bytes) -> dict[str, str]:
            pytest.fail("charset_normalizer.detect() must not run for UTF-8-flagged entries")

        monkeypatch.setattr(_zip_encoding.charset_normalizer, "detect", _boom)
        info = _zip_info_for("データ.txt".encode(), utf8_flag=True)

        # When: resolving the filename.
        result = resolve_filename(info)

        # Then: the name survives and detection was never called.
        assert result == "データ.txt"

    @pytest.mark.parametrize(
        "name",
        [
            "NB1_800_20220214_2θ_θ.TXT",
            "20211014T5高圧_2θ_θ.TXT",
            "日本語ファイル.txt",
            "データ.txt",
            "測定結果_2023.csv",
        ],
    )
    def test_cp932_name_without_flag_is_recovered(self, name: str) -> None:
        """TC-EP-RESOLVE-002: cp932 names are recovered (the issue #515 bug).

        ``charset_normalizer`` alone reads several of these as cp949 or
        utf_16_le and corrupts them, which is why cp932 is tried first.
        """
        # Given: an unflagged entry whose stored bytes are cp932.
        info = _zip_info_for(name.encode("cp932"), utf8_flag=False)

        # When: resolving the filename.
        result = resolve_filename(info)

        # Then: the original Japanese text is recovered.
        assert result == name

    def test_ascii_name_without_flag_is_unchanged(self) -> None:
        """TC-EP-RESOLVE-003: ASCII names pass through untouched."""
        # Given: an unflagged entry with a pure-ASCII name.
        info = _zip_info_for(b"data.txt", utf8_flag=False)

        # When: resolving the filename.
        result = resolve_filename(info)

        # Then: the name is unchanged.
        assert result == "data.txt"

    def test_undecodable_cp932_falls_back_to_detection(self) -> None:
        """TC-EP-RESOLVE-004: non-cp932 legacy names reach the fallback.

        ``0x81 0x20`` is an illegal cp932 multibyte sequence, so cp932 decoding
        raises and detection takes over. The result may be imperfect, but the
        call must return a name rather than propagate the error.
        """
        # Given: an unflagged entry whose bytes cp932 cannot decode.
        raw = bytes([0x81, 0x20]) + b"_bad.TXT"
        with pytest.raises(UnicodeDecodeError):
            raw.decode("cp932")  # guard: the fixture really does defeat cp932
        info = _zip_info_for(raw, utf8_flag=False)

        # When: resolving the filename.
        result = resolve_filename(info)

        # Then: some name comes back and nothing is raised.
        assert isinstance(result, str)
        assert result

    def test_unusable_detected_codec_keeps_zipfile_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-EP-RESOLVE-005: a bogus detection result must not abort the zip.

        Detection is heuristic and can name a codec that does not exist or
        cannot decode these bytes. One unreadable filename must not take the
        whole archive down with it.
        """
        # Given: detection that names a codec Python does not have.
        monkeypatch.setattr(
            _zip_encoding.charset_normalizer,
            "detect",
            lambda _: {"encoding": "not-a-real-codec"},
        )
        raw = bytes([0x81, 0x20]) + b"_bad.TXT"
        info = _zip_info_for(raw, utf8_flag=False)
        fallback_name = info.filename

        # When: resolving the filename.
        result = resolve_filename(info)

        # Then: zipfile's own name is kept instead of raising.
        assert result == fallback_name

    def test_detection_returning_none_falls_back_to_cp437(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-EP-RESOLVE-006: no detection result means cp437, zipfile's default."""
        # Given: detection that yields no encoding at all.
        monkeypatch.setattr(
            _zip_encoding.charset_normalizer,
            "detect",
            lambda _: {"encoding": None},
        )
        raw = bytes([0x81, 0x20]) + b"_bad.TXT"
        info = _zip_info_for(raw, utf8_flag=False)

        # When: resolving the filename.
        result = resolve_filename(info)

        # Then: the cp437 reading (what zipfile produced) is used.
        assert result == raw.decode("cp437")
