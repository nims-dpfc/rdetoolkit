import json
import os
import pathlib
import shutil
import zipfile
from typing import Generator

import pandas as pd
import pytest


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
def inputfile_multi() -> Generator[list[str], None, None]:
    """Create multiple files temporarily for test input"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    # setup
    empty_child_file_1 = pathlib.Path(input_dir, "test_child1.txt")
    empty_child_file_1.touch()
    empty_child_file_2 = pathlib.Path(input_dir, "test_child2.txt")
    empty_child_file_2.touch()

    yield [str(empty_child_file_1), str(empty_child_file_2)]

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_zip_with_file() ->  Generator[str, None, None]:
    """ファイルのみを圧縮したzip"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_zip_root_foldername = pathlib.Path("test_input_multi.zip")
    test_zip_filepath = pathlib.Path(input_dir, test_zip_root_foldername)

    compressed_filepath1 = pathlib.Path("test_child1.txt")
    compressed_filepath1.touch()

    # setup
    with zipfile.ZipFile(str(test_zip_filepath), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(str(compressed_filepath1))

    yield str(test_zip_filepath)

    # teardown
    if os.path.exists(compressed_filepath1):
        os.remove(str(compressed_filepath1))
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_zip_with_folder() ->  Generator[str, None, None]:
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
def inputfile_zip_with_folder_multi() ->  Generator[str, None, None]:
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


# エクセルインボイス(file mode): zipに複数フォルダ+複数タイル登録
EXCELINVOICE_ENTRYDATA_SHEET1_MULTI = [
        ["data_file_names", "", "", "basic", "basic", "basic", "basic", "sample", "sample", "sample", "sample", "sample", "sample", "sample.general", "sample.general", "sample.general", "sample.general", "custom", "custom"],
        ["name", "dataset_title", "dataOwner", "dataOwnerId", "dataName", "experimentId", "referenceUrl", "description", "names", "sampleId", "ownerId", "composition", "description", "general-name", "chemical-composition", "sample-type", "cas-number", "key1", "key2"],
        ["ファイル名\n(拡張子も含め入力)\n(入力例:○○.txt)", "データセット名\n(必須)", "データ所有者\n(NIMS User ID)", "NIMS user UUID\n(必須)", "データ名\n(必須)", "実験ID", "参考URL", "説明", "試料名\n(ローカルID)", "試料UUID\n(必須)", "試料管理者UUID", "化学式・組成式・分子式など", "試料の説明", "一般名称\n(General name)", "化学組成\n(Chemical composition)", "試料分類\n(Sample type)", "CAS番号\n(CAS Number)", "key1", "key2"],
        ["test_child1.txt", "N_TEST_1","test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test1", "test_230606_1", "desc1", "sample1", "cbf194ea-813f-4e05-b288", "1111", "sample1", "test_ref", "desc3", "testname", "Fe", "magnet", "7439-89-6", "AAA", "CCC"],
        ["test_child2.txt", "N_TEST_2", "test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test2","test_230606_2", "desc2", "sample2", "cbf194ea-813f-4e05-b288", "1111", "sample2", "test_ref", "desc4", "testname", "Fe", "magnet", "7439-89-6", "BBB", "DDD"]
    ]

# エクセルインボイス(folder mode): zipに複数フォルダ+複数タイル登録
EXCELINVOICE_ENTRYDATA_SHEET1_MULTI_FOLDER = [
        ["data_folder_names", "", "", "basic", "basic", "basic", "basic", "sample", "sample", "sample", "sample", "sample", "sample", "sample.general", "sample.general", "sample.general", "sample.general", "custom", "custom"],
        ["name", "dataset_title", "dataOwner", "dataOwnerId", "dataName", "experimentId", "referenceUrl", "description", "names", "sampleId", "ownerId", "composition", "description", "general-name", "chemical-composition", "sample-type", "cas-number", "key1", "key2"],
        ["ファイル名\n(拡張子も含め入力)\n(入力例:○○.txt)", "データセット名\n(必須)", "データ所有者\n(NIMS User ID)", "NIMS user UUID\n(必須)", "データ名\n(必須)", "実験ID", "参考URL", "説明", "試料名\n(ローカルID)", "試料UUID\n(必須)", "試料管理者UUID", "化学式・組成式・分子式など", "試料の説明", "一般名称\n(General name)", "化学組成\n(Chemical composition)", "試料分類\n(Sample type)", "CAS番号\n(CAS Number)", "key1", "key2"],
        ["data2", "N_TEST_1","test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test1", "test_230606_1", "desc1", "sample1", "cbf194ea-813f-4e05-b288", "1111", "sample1", "test_ref", "desc3", "testname", "Fe", "magnet", "7439-89-6", "AAA", "CCC"],
        ["data1", "N_TEST_2", "test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test2","test_230606_2", "desc2", "sample2", "cbf194ea-813f-4e05-b288", "1111", "sample2", "test_ref", "desc4", "testname", "Fe", "magnet", "7439-89-6", "BBB", "DDD"]
    ]

# エクセルインボイス(file mode): zipに1ファイルのみ+1タイル登録
EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE = [
        ["data_file_names", "", "", "basic", "basic", "basic", "basic", "sample", "sample", "sample", "sample", "sample", "sample", "sample.general", "sample.general", "sample.general", "sample.general", "custom", "custom"],
        ["name", "dataset_title", "dataOwner", "dataOwnerId", "dataName", "experimentId", "referenceUrl", "description", "names", "sampleId", "ownerId", "composition", "description", "general-name", "chemical-composition", "sample-type", "cas-number", "key1", "key2"],
        ["ファイル名\n(拡張子も含め入力)\n(入力例:○○.txt)", "データセット名\n(必須)", "データ所有者\n(NIMS User ID)", "NIMS user UUID\n(必須)", "データ名\n(必須)", "実験ID", "参考URL", "説明", "試料名\n(ローカルID)", "試料UUID\n(必須)", "試料管理者UUID", "化学式・組成式・分子式など", "試料の説明", "一般名称\n(General name)", "化学組成\n(Chemical composition)", "試料分類\n(Sample type)", "CAS番号\n(CAS Number)", "key1", "key2"],
        ["test_child1.txt", "N_TEST_1","test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test1", "test_230606_1", "desc1", "sample1", "cbf194ea-813f-4e05-b288", "1111", "sample1", "test_ref", "desc3", "testname", "Fe", "magnet", "7439-89-6", "AAA", "CCC"],
    ]

# エクセルインボイス(file mode): zipに1ファイルのみ+複数タイル登録
EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE_MULTILINE = [
        ["data_file_names", "", "", "basic", "basic", "basic", "basic", "sample", "sample", "sample", "sample", "sample", "sample", "sample.general", "sample.general", "sample.general", "sample.general", "custom", "custom"],
        ["name", "dataset_title", "dataOwner", "dataOwnerId", "dataName", "experimentId", "referenceUrl", "description", "names", "sampleId", "ownerId", "composition", "description", "general-name", "chemical-composition", "sample-type", "cas-number", "key1", "key2"],
        ["ファイル名\n(拡張子も含め入力)\n(入力例:○○.txt)", "データセット名\n(必須)", "データ所有者\n(NIMS User ID)", "NIMS user UUID\n(必須)", "データ名\n(必須)", "実験ID", "参考URL", "説明", "試料名\n(ローカルID)", "試料UUID\n(必須)", "試料管理者UUID", "化学式・組成式・分子式など", "試料の説明", "一般名称\n(General name)", "化学組成\n(Chemical composition)", "試料分類\n(Sample type)", "CAS番号\n(CAS Number)", "key1", "key2"],
        ["test_child1.txt", "N_TEST_1","test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test1", "test_230606_1", "desc1", "sample1", "cbf194ea-813f-4e05-b288", "1111", "sample1", "test_ref", "desc3", "testname", "Fe", "magnet", "7439-89-6", "AAA", "CCC"],
        ["test_child1.txt", "N_TEST_1","test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test1", "test_230606_1", "desc1", "sample1", "cbf194ea-813f-4e05-b288", "1111", "sample1", "test_ref", "desc3", "testname", "Fe", "magnet", "7439-89-6", "DDD", "FFF"],
        ["test_child1.txt", "N_TEST_1","test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test1", "test_230606_1", "desc1", "sample1", "cbf194ea-813f-4e05-b288", "1111", "sample1", "test_ref", "desc3", "testname", "Fe", "magnet", "7439-89-6", "DDD", "FFF"],
    ]

# エクセルインボイス(file mode): 1ファイルのみ+1タイル登録+サンプル情報なし
EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE_NON_SAMPLE = [
        ["data_file_names", "", "", "basic", "basic", "basic", "basic", "basic", "custom", "custom"],
        ["name", "dataset_title", "dataOwner", "dataOwnerId", "dataName", "experimentId", "referenceUrl", "description", "key1", "key2"],
        ["ファイル名\n(拡張子も含め入力)\n(入力例:○○.txt)", "データセット名\n(必須)", "データ所有者\n(NIMS User ID)", "NIMS user UUID\n(必須)", "データ名\n(必須)", "実験ID", "参考URL", "説明", "key1", "key2"],
        ["test_child1.txt", "DATASETNAME_TEST_1", "test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "TEST DATA NAME", "exp_id", "test_ref_url", "desc1", "AAA", "CCC"],
    ]

# エクセルインボイス(file mode): 1ファイルのみ+1タイル登録+headerをマージした形式
EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE_MERGE = [
        ["data_file_names/name", "/dataset_title", "/dataOwner", "basic", "basic", "basic", "basic", "sample", "sample", "sample", "sample", "sample", "sample", "sample.general", "sample.general", "sample.general", "sample.general", "custom", "custom"],
        ["name", "dataset_title", "dataOwner", "dataOwnerId", "dataName", "experimentId", "referenceUrl", "description", "names", "sampleId", "ownerId", "composition", "description", "general-name", "chemical-composition", "sample-type", "cas-number", "key1", "key2"],
        ["ファイル名\n(拡張子も含め入力)\n(入力例:○○.txt)", "データセット名\n(必須)", "データ所有者\n(NIMS User ID)", "NIMS user UUID\n(必須)", "データ名\n(必須)", "実験ID", "参考URL", "説明", "試料名\n(ローカルID)", "試料UUID\n(必須)", "試料管理者UUID", "化学式・組成式・分子式など", "試料の説明", "一般名称\n(General name)", "化学組成\n(Chemical composition)", "試料分類\n(Sample type)", "CAS番号\n(CAS Number)", "key1", "key2"],
        ["test_child1.txt", "N_TEST_1","test_user", "f30812c3-14bc-4274-809f-afcfaa2e4047", "test1", "test_230606_1", "desc1", "sample1", "cbf194ea-813f-4e05-b288", "1111", "sample1", "test_ref", "desc3", "testname", "Fe", "magnet", "7439-89-6", "AAA", "CCC"],
    ]

# エクセルインボイス(file mode): ファイルなし+1タイル登録
EXCELINVOICE_ENTRYDATA_SHEET1_NONFILE = [
        ["data_file_names", "", "", "basic", "basic", "basic", "basic", "sample", "sample", "sample", "sample", "sample", "sample", "sample.general", "sample.general", "sample.general", "sample.general", "custom", "custom"],
        ["name", "dataset_title", "dataOwner", "dataOwnerId", "dataName", "experimentId", "referenceUrl", "description", "names", "sampleId", "ownerId", "composition", "description", "general-name", "chemical-composition", "sample-type", "cas-number", "key1", "key2"],
        ["ファイル名\n(拡張子も含め入力)\n(入力例:○○.txt)", "データセット名\n(必須)", "データ所有者\n(NIMS User ID)", "NIMS user UUID\n(必須)", "データ名\n(必須)", "実験ID", "参考URL", "説明", "試料名\n(ローカルID)", "試料UUID\n(必須)", "試料管理者UUID", "化学式・組成式・分子式など", "試料の説明", "一般名称\n(General name)", "化学組成\n(Chemical composition)", "試料分類\n(Sample type)", "CAS番号\n(CAS Number)", "key1", "key2"],
    ]

# エクセルインボイス: 2シート目の情報
EXCELINVOICE_ENTRYDATA_SHEET2 = [
        ['33c6e9dc-5787-0f96-7683-f39281c60419', 'sample.general.composiiton'],
        ['f2d5e89e-01f0-66a2-5d8e-623a4fc31698', 'sample.general.material-name'],
        ['a7a6fc7b-ed46-88b0-bba8-a1e34857a049', 'sample.general.sample-alias'],
        ['e2d20d02-2e38-2cd3-b1b3-66fdb8a11057', 'sample.general.cas-number'],
        ['1e70d11d-cbdd-bfd1-9301-9612c29b4060', 'sample.general.purchase-date'],
        ['1d3cab05-3eaa-cb9b-9a3f-20eb0ca26963', 'sample.general.crystalline-state'],
        ['efcf34e7-4308-c195-6691-6f4d28ffc9bb', 'sample.general.crystal-structure'],
        ['e9617207-7f74-ef45-9b05-74eef6e4ecbb', 'sample.general.pearson-symbol'],
        ['f63149a4-e57c-4273-4c1e-dffa41356d28', 'sample.general.space-group'],
        ['7cc57dfb-8b70-4b3a-5315-fbce4cbf73d0', 'sample.general.sample-shape'],
        ['efc6a0d5-313e-1871-190c-baaff7d1bf6c', 'sample.general.smiles-string'],
        ['9270879d-d94e-4d3f-2d5c-19568e040004', 'sample.general.inchi'],
        ['3edadcff-8a85-51d9-708f-8f76bf055377', 'sample.general.inchi-key'],
        ['dc27a956-263e-f920-e574-5beec912a247', 'sample.general.molecular-weight'],
        ['0444cf53-db47-b208-7b5f-54429291a140', 'sample.general.sample-type'],
        ['fc30c31d-12a3-591a-c837-4f06ab458de0', 'sample.general.taxonomy'],
        ['9a23002a-c398-e521-081a-24b6cd32dbbd', 'sample.general.cell-line'],
        ['b4ce4016-e2bf-e5a1-7cae-ed496c7a776f', 'sample.general.protein-name'],
        ['8c9b1a88-1530-24d3-4b2e-5441eee5c24f', 'sample.general.gene-name'],
        ['047e30f3-f294-e58d-cbe4-6bb588bf4cf8', 'sample.general.ncbi-accession-number'],
        ['3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e', 'sample.general.general-name'],
        ['0aadfff2-37de-411f-883a-38b62b2abbce', 'sample.general.chemical-composition'],
        ['5e166ac4-bfcd-457a-84bc-8626abe9188f', 'sample.general.supplier'],
        ['0d0417a3-3c3b-496a-b0fb-5a26f8a74166', 'sample.general.lot-number-or-product-number-etc'],
    ]

# エクセルインボイス: 3シート目の情報
EXCELINVOICE_ENTRYDATA_SHEET3 = [
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '3250c45d-0ed6-1438-43b5-eb679918604a', 'sample.specific.organic.chemical-formula'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '70c2c751-5404-19b7-4a5e-981e6cebbb15', 'sample.specific.organic.name'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', 'e2d20d02-2e38-2cd3-b1b3-66fdb8a11057', 'sample.specific.organic.cas-number'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '518e26a0-4262-86f5-3598-80e18e6ff2af', 'sample.specific.organic.pubchem'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '3a775d54-5c13-fe66-6405-29c05bc931ce', 'sample.specific.organic.viscosity'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '659da80e-c2ee-2986-41ce-68201b3bc4dd', 'sample.specific.organic.boiling-point'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '4efc4c3b-727c-c752-cf28-701b55dba1af', 'sample.specific.organic.melting-temperature'],
        ['932e4fe1-9724-305f-ffc5-1908c31c83e5', '70c2c751-5404-19b7-4a5e-981e6cebbb15', 'sample.specific.inorganic.name'],
        ['932e4fe1-9724-305f-ffc5-1908c31c83e5', '3250c45d-0ed6-1438-43b5-eb679918604a', 'sample.specific.inorganic.chemical-formula'],
        ['932e4fe1-9724-305f-ffc5-1908c31c83e5', 'f63149a4-e57c-4273-4c1e-dffa41356d28', 'sample.specific.inorganic.space-group'],
        ['a674a8ef-efa8-9497-4ed4-74de55fafddb', '3250c45d-0ed6-1438-43b5-eb679918604a', 'sample.specific.metals.chemical-formula'],
        ['a674a8ef-efa8-9497-4ed4-74de55fafddb', '70c2c751-5404-19b7-4a5e-981e6cebbb15', 'sample.specific.metals.name'],
        ['a674a8ef-efa8-9497-4ed4-74de55fafddb', 'e2d20d02-2e38-2cd3-b1b3-66fdb8a11057', 'sample.specific.metals.cas-number'],
        ['a674a8ef-efa8-9497-4ed4-74de55fafddb', 'f63149a4-e57c-4273-4c1e-dffa41356d28', 'sample.specific.metals.space-group'],
        ['a674a8ef-efa8-9497-4ed4-74de55fafddb', 'efcf34e7-4308-c195-6691-6f4d28ffc9bb', 'sample.specific.metals.crystal-structure'],
        ['a674a8ef-efa8-9497-4ed4-74de55fafddb', '659da80e-c2ee-2986-41ce-68201b3bc4dd', 'sample.specific.metals.boiling-point'],
        ['a674a8ef-efa8-9497-4ed4-74de55fafddb', '4efc4c3b-727c-c752-cf28-701b55dba1af', 'sample.specific.metals.melting-temperature'],
        ['342ba516-4d02-171c-9bc4-70a3134b47a8', '3250c45d-0ed6-1438-43b5-eb679918604a', 'sample.specific.polymers.chemical-formula'],
        ['342ba516-4d02-171c-9bc4-70a3134b47a8', '70c2c751-5404-19b7-4a5e-981e6cebbb15', 'sample.specific.polymers.name'],
        ['342ba516-4d02-171c-9bc4-70a3134b47a8', 'e2d20d02-2e38-2cd3-b1b3-66fdb8a11057', 'sample.specific.polymers.cas-number'],
        ['342ba516-4d02-171c-9bc4-70a3134b47a8', '518e26a0-4262-86f5-3598-80e18e6ff2af', 'sample.specific.polymers.pubchem'],
        ['342ba516-4d02-171c-9bc4-70a3134b47a8', '4efc4c3b-727c-c752-cf28-701b55dba1af', 'sample.specific.polymers.melting-temperature'],
        ['52148afb-6759-23e8-c8b8-33912ec5bfcf', '70c2c751-5404-19b7-4a5e-981e6cebbb15', 'sample.specific.semiconductors.name'],
        ['961c9637-9b83-0e9d-e60e-ffc1e2517afd', '70c2c751-5404-19b7-4a5e-981e6cebbb15', 'sample.specific.ceramics.name'],
        ['0dde5969-3039-739b-b33b-97df40450790', '70c2c751-5404-19b7-4a5e-981e6cebbb15', 'sample.specific.biological.name'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', 'dc27a956-263e-f920-e574-5beec912a247', 'sample.specific.organic-material.molecular-weight'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', 'efc6a0d5-313e-1871-190c-baaff7d1bf6c', 'sample.specific.organic-material.SMILES-String'],
        ['0dde5969-3039-739b-b33b-97df40450790', '0444cf53-db47-b208-7b5f-54429291a140', 'sample.specific.biological.sample-type'],
        ['0dde5969-3039-739b-b33b-97df40450790', 'fc30c31d-12a3-591a-c837-4f06ab458de0', 'sample.specific.biological.taxonomy'],
        ['0dde5969-3039-739b-b33b-97df40450790', '9a23002a-c398-e521-081a-24b6cd32dbbd', 'sample.specific.biological.cell-line'],
        ['0dde5969-3039-739b-b33b-97df40450790', 'b4ce4016-e2bf-e5a1-7cae-ed496c7a776f', 'sample.specific.biological.protein-name'],
        ['0dde5969-3039-739b-b33b-97df40450790', '8c9b1a88-1530-24d3-4b2e-5441eee5c24f', 'sample.specific.biological.gene-name'],
        ['0dde5969-3039-739b-b33b-97df40450790', '047e30f3-f294-e58d-cbe4-6bb588bf4cf8', 'sample.specific.biological.ncbi-accession-number'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '9270879d-d94e-4d3f-2d5c-19568e040004', 'sample.specific.organic-material.inchi'],
        ['01cb3c01-37a4-5a43-d8ca-f523ca99a75b', '3edadcff-8a85-51d9-708f-8f76bf055377', 'sample.specific.organic-material.inchi-key'],
    ]
@pytest.fixture
def inputfile_single_excelinvoice() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['term_id', 'key_name'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['sample_class_id', 'term_id', 'key_name'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")

@pytest.fixture
def inputfile_single_header_merge_excelinvoice() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE_MERGE, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['term_id', 'key_name'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['sample_class_id', 'term_id', 'key_name'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")

@pytest.fixture
def inputfile_multi_excelinvoice() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_MULTI, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['term_id', 'key_name'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['sample_class_id', 'term_id', 'key_name'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")

@pytest.fixture
def inputfile_multi_folder_excelinvoice() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_MULTI_FOLDER, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['term_id', 'key_name'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['sample_class_id', 'term_id', 'key_name'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")

@pytest.fixture
def inputfile_single_dummy_header_excelinvoice() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['dummy_id', 'dummy_term'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['dummy1', 'dummy2', 'dummy3'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def inputfile_empty_excelinvoice() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['dummy_id', 'dummy_term'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['dummy1', 'dummy2', 'dummy3'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def non_inputfile_excelinvoice() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_NONFILE, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['term_id', 'key_name'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['sample_class_id', 'term_id', 'key_name'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def excelinvoice_non_sampleinfo() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE_NON_SAMPLE, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['term_id', 'key_name'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['sample_class_id', 'term_id', 'key_name'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture
def excelinvoice_single_input_multiline() ->  Generator[str, None, None]:
    """ExcelInvoice"""
    input_dir = pathlib.Path("data", "inputdata")
    input_dir.mkdir(parents=True, exist_ok=True)
    test_excel_invoice = pathlib.Path(input_dir, "test_excel_invoice.xlsx")

    df1 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET1_SINGLE_MULTILINE, columns=["invoiceList_format_id", "Sample_RDE_DataSet", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    df2 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET2, columns=['term_id', 'key_name'])
    df3 = pd.DataFrame(EXCELINVOICE_ENTRYDATA_SHEET3, columns=['sample_class_id', 'term_id', 'key_name'])

    with pd.ExcelWriter(test_excel_invoice) as writer:
        df1.to_excel(writer, sheet_name="invoice_form", index=False)
        df2.to_excel(writer, sheet_name="generalTerm", index=False)
        df3.to_excel(writer, sheet_name="specificTerm", index=False)

    yield str(test_excel_invoice)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def ivnoice_json_with_sample_info() ->  Generator[str, None, None]:
    """試料情報ありのinvoice.json"""
    invoice_dir = pathlib.Path("data", "invoice")
    invoice_json_path = pathlib.Path(str(invoice_dir), "invoice.json")
    data = {
        'datasetId': 'e751fcc4-b926-4747-b236-cab40316fc49',
        'basic': {
            'dateSubmitted': '2023-03-14',
            'dataOwnerId': 'f30812c3-14bc-4274-809f-afcfaa2e4047',
            'dataName': 'test1',
            'experimentId': 'test_230606_1',
            'description': 'desc1'
            },
        'custom': {
            'key1': 'test1',
            'key2': 'test2'
        },
        'sample': {
            'sampleId': 'cbf194ea-813f-4e05-b288',
            'names': ['sample1'],
            'composition': 'sample1',
            'referenceUrl':'test_ref',
            'description': "desc3",
            'generalAttributes': [
                {'termId': '3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e', 'value': 'testname'},
                {'termId': 'e2d20d02-2e38-2cd3-b1b3-66fdb8a11057', 'value': '7439-89-6'},
                {'termId': '0aadfff2-37de-411f-883a-38b62b2abbce', 'value': 'sample1'},
                {'termId': '0444cf53-db47-b208-7b5f-54429291a140', 'value': 'magnet'},
                {'termId': '0444cf53-db47-b208-7b5f-54429291a140', 'value': 'magnet'},
                ],
            'ownerId': '1111'
        }
    }

    # setup
    invoice_dir.mkdir(parents=True, exist_ok=True)
    with open(invoice_json_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f)

    yield str(invoice_json_path)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def ivnoice_json_none_sample_info() ->  Generator[str, None, None]:
    """試料情報なしのinvoice.json"""
    invoice_dir = pathlib.Path("data", "invoice")
    invoice_json_path = pathlib.Path(str(invoice_dir), "invoice.json")
    data = {
        'datasetId': 'e751fcc4-b926-4747-b236-cab40316fc49',
        'basic': {
            'dateSubmitted': '2023-03-14',
            'dataOwnerId': 'f30812c3-14bc-4274-809f-afcfaa2e4047',
            'dataName': 'test1',
            'experimentId': 'test_230606_1',
            'description': 'desc1'
            },
        'custom': {
            'key1': 'test1',
            'key2': 'test2'
        }
    }

    # setup
    invoice_dir.mkdir(parents=True, exist_ok=True)
    with open(invoice_json_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f)

    yield str(invoice_json_path)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def tasksupport() ->  Generator[list[str], None, None]:
    tasksupport_dir = pathlib.Path("data", "tasksupport")
    tasksupport_dir.mkdir(parents=True, exist_ok=True)
    empty_defcsv = pathlib.Path(tasksupport_dir, "default_value.csv")
    empty_defcsv.touch()
    empty_schema = pathlib.Path(tasksupport_dir, "invoice.schema.json")
    empty_schema.touch()
    empty_defjson = pathlib.Path(tasksupport_dir, "metadata-def.json")
    empty_defjson.touch()

    yield [str(empty_defcsv), str(empty_schema), str(empty_defjson)]

    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def inputfile_rdeformat() ->  Generator[str, None, None]:
    """rdeformat用のフォルダ群を圧縮 (1ファイル入力/dividedなし)"""
    output_struct_dir_names = (
        "inputdata", "invoice", "raw", "main_image", "other_image",
        "thumbnail", "structured", "meta", "logs", "tasksupport"
    )
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
    output_struct_dir_names = ("inputdata", "invoice", "tasksupport")
    for name in output_struct_dir_names:
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
def inputfile_rdeformat_divived() ->  Generator[str, None, None]:
    """rdeformat用のフォルダ群を圧縮 (複数ファイル入力/divided)"""
    output_struct_dir_names = (
        "inputdata", "invoice", "raw", "main_image", "other_image",
        "thumbnail", "structured", "meta", "logs", "tasksupport"
    )
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
    for idx in range(1,3):
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
    output_struct_dir_names = ("inputdata", "invoice", "tasksupport")
    for name in output_struct_dir_names:
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
def inputfile_multimode() ->  Generator[str, None, None]:
    """multiモード"""
    os.makedirs(os.path.join("data", "tasksupport"), exist_ok=True)
    multi_flag_filepath = pathlib.Path("data", "tasksupport", "multifile.txt")
    multi_flag_filepath.touch()

    yield str(multi_flag_filepath)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")



@pytest.fixture()
def metadata_def_json_with_feature() ->  Generator[str, None, None]:
    """特徴量書き込み用のmetadata-def.json"""
    tasksupport_dir = pathlib.Path("data", "tasksupport")
    invoice_json_path = pathlib.Path(str(tasksupport_dir), "metadata-def.json")
    data = {
            "test_feature_meta1": {
                "name": {
                    "ja": "特徴量1",
                    "en": "feature1"
                },
                "schema": {
                    "type": "string"
                },
                "_feature": 1
            },
            "test_feature_meta2": {
                "name": {
                    "ja": "特徴量2",
                    "en": "feature2"
                },
                "schema": {
                    "type": "string"
                },
                "unit": "V",
                "_feature": 1
            },
            "test_feature_meta3": {
                "name": {
                    "ja": "特徴量3",
                    "en": "feature3"
                },
                "schema": {
                    "type": "string"
                },
                "unit": "V",
                "_feature": True,
                "variable": 1
            }
        }

    # setup
    tasksupport_dir.mkdir(parents=True, exist_ok=True)
    with open(invoice_json_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f)

    yield str(invoice_json_path)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def metadata_json() ->  Generator[str, None, None]:
    """test用のmetadata.json"""
    tasksupport_dir = pathlib.Path("data", "meta")
    invoice_json_path = pathlib.Path(str(tasksupport_dir), "metadata.json")
    data = {
            "constant":{
                "test_feature_meta1": {
                    "value": "test-value1"
                },
                "test_feature_meta2": {
                    "value": "test-value2",
                    "unit": "V"
                }
            },
            "variable": [
                {"test_feature_meta3":{
                    "value": "test-value3",
                    "unit": "V"
                }}
            ]
        }

    # setup
    tasksupport_dir.mkdir(parents=True, exist_ok=True)
    with open(invoice_json_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f)

    yield str(invoice_json_path)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")


@pytest.fixture()
def metadata_json_missing_value() ->  Generator[str, None, None]:
    """test用のmetadata.json
    variable test_feature_meta2を欠損させたもの
    """
    tasksupport_dir = pathlib.Path("data", "meta")
    invoice_json_path = pathlib.Path(str(tasksupport_dir), "metadata.json")
    data = {
            "constant":{
                "test_feature_meta1": {
                    "value": "test-value1"
                }
            },
            "variable": [
                {"test_feature_meta3":{
                    "value": "test-value3",
                    "unit": "V"
                }}
            ]
        }

    # setup
    tasksupport_dir.mkdir(parents=True, exist_ok=True)
    with open(invoice_json_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f)

    yield str(invoice_json_path)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")

@pytest.fixture()
def ivnoice_schema_json() ->  Generator[str, None, None]:
    """ダミー用invoice.schema.json"""
    tasksupport_dir = pathlib.Path("data", "tasksupport")
    invoice_json_path = pathlib.Path(str(tasksupport_dir), "invoice.schema.json")
    data = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://test_sample/test/dataset-templates/r000_Sample_Project/invoice.schema.json",

            "description": "固有情報と試料情報のスキーマ",
            "type": "object",
            "required": [
                "custom",
                "sample"
            ],
            "properties": {
                "custom": {
                    "type": "object",
                    "label": {
                        "ja": "固有情報",
                        "en": "Specific Information"
                    },
                    "required": [],
                    "properties": {
                        "key1": {
                            "label": {
                                "ja": "key1",
                                "en": "key1"
                            },
                            "type": "string",
                        },
                        "key2": {
                            "label": {
                                "ja": "key2",
                                "en": "key2"
                            },
                            "type": "string",
                        },
                        "common_data_type": {
                            "label": {
                                "ja": "登録データタイプ",
                                "en": "Data type"
                            },
                            "type": "string",
                            "default": "IV"
                        },
                        }
                    }
                }
            }


    # setup
    tasksupport_dir.mkdir(parents=True, exist_ok=True)
    with open(invoice_json_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f)

    yield str(invoice_json_path)

    # teardown
    if os.path.exists("data"):
        shutil.rmtree("data")
