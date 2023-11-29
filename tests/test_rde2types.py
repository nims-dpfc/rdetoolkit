"""テストスイート:
1. RdeOutputResourcePathに関するテスト
    1-1. 代入した属性が正しい値を保持しているかどうかテスト
    1-2. Noneが格納されている属性に参照すると例外キャッチできるかテスト
    1-3. 非NoneからNoneへ変更したのち、Noneへアクセスし例外を捕捉できるかテスト
2. RdeFormatFlagsに関するテスト
    2-1. RDEフォーマットとMultifileフラグの状態を保持できるかテスト
    2-2. 片方のフラグ(RDEフォーマット)のTrueにして正常に状態を保持できるかテスト
    2-3. 片方のフラグ(Multifile)のTrueにして正常に状態を保持できるかテスト
    2-4: 両方のフラグをTrue(フラグの起動となる空ファイルを同時に作成)にしたとき例外が出力されるかテスト
    2-5: 両方のフラグをTrueにしたとき例外が出力されるかテスト(状態を変更)
"""
import os
from pathlib import Path

import pytest
from rdetoolkit.models.rde2types import RdeFormatFlags, RdeOutputResourcePath


@pytest.fixture()
def create_rde_output_resource_path():
    yield RdeOutputResourcePath(
        raw=Path("data", "raw"),
        rawfiles=(Path("rawfile1"), Path("rawfile2")),
        struct=Path("data", "struct"),
        main_image=Path("data", "main_image"),
        other_image=Path("data", "other_image"),
        meta=Path("data", "meta"),
        thumbnail=Path("data", "thumbnail"),
        logs=Path("data", "logs"),
        invoice=Path("data", "invoice"),
        invoice_schema_json=Path("data", "invoice.schema.json"),
        invoice_org=Path("data", "invoice.json"),
    )


def test_rde_output_resource_path_initialization(create_rde_output_resource_path):
    """1-1. 正しい値を保持しているか"""
    obj = create_rde_output_resource_path
    assert obj.raw == Path("data/raw")
    assert obj.rawfiles == (Path("rawfile1"), Path("rawfile2"))
    assert obj.struct == Path("data/struct")
    assert obj.main_image == Path("data/main_image")
    assert obj.other_image == Path("data/other_image")
    assert obj.meta == Path("data/meta")
    assert obj.thumbnail == Path("data/thumbnail")
    assert obj.logs == Path("data/logs")
    assert obj.invoice == Path("data/invoice")
    assert obj.invoice_schema_json == Path("data/invoice.schema.json")
    assert obj.invoice_org == Path("data/invoice.json")


def test_rde_format_flags_no_flag():
    """2-1. RDEフォーマットとMultifileフラグの状態を保持できるかテスト"""
    flags = RdeFormatFlags()
    assert flags.is_rdeformat_enabled == False
    assert flags.is_multifile_enabled == False


def test_rde_format_flags_rdeformat_flag(inputfile_rdeformat):
    """2-2. 片方のフラグ(RDEフォーマット)のTrueにして正常に状態を保持できるかテスト"""
    flags = RdeFormatFlags()
    assert flags.is_rdeformat_enabled == True
    assert flags.is_multifile_enabled == False


def test_rde_format_flags_multifile_flag(inputfile_multimode):
    """2-3. 片方のフラグ(Multifile)のTrueにして正常に状態を保持できるかテスト"""
    flags = RdeFormatFlags()
    assert flags.is_rdeformat_enabled == False
    assert flags.is_multifile_enabled == True


def test_defualt_check_both_flags(inputfile_multimode):
    """2-4: 両方のフラグをTrue(フラグの起動となる空ファイルを同時に作成)にしたとき例外が出力されるかテスト"""
    rdeformat_text = Path("data", "tasksupport", "rdeformat.txt")
    rdeformat_text.touch()

    with pytest.raises(ValueError) as e:
        _ = RdeFormatFlags()
    assert str(e.value) == "both flags cannot be True"

    os.remove(rdeformat_text)


def test_both_flags_after_create_instance():
    """2-5: 両方のフラグをTrueにしたとき例外が出力されるかテスト(状態を変更)"""
    flags = RdeFormatFlags()
    flags.is_rdeformat_enabled = True
    with pytest.raises(ValueError) as e:
        flags.is_multifile_enabled = True
    assert str(e.value) == "both flags cannot be True"

    flags = RdeFormatFlags()
    flags.is_multifile_enabled = True
    with pytest.raises(ValueError) as e:
        flags.is_rdeformat_enabled = True
    assert str(e.value) == "both flags cannot be True"
