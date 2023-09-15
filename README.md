[![Latest Release](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/badges/release.svg)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/releases)
[![pipeline status](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/badges/main/pipeline.svg)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/commits/main)
[![coverage report](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/badges/main/coverage.svg)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/commits/main)
[![python.org](https://img.shields.io/badge/Python-3.9%7C3.10%7C3.11-%233776AB?logo=python)](https://www.python.org/downloads/release/python-3917/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/blob/main/LICENSE)
[![Issue](https://img.shields.io/badge/issue_tracking-gitlab-orange)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/issues)

# RdeToolKit

RdeToolKitは、RDE2.0構造化プログラムのワークフローを作成するための基本的なPythonパッケージです。
RdeToolKitの各種モジュールを使うことで、RDEへの研究・実験データの登録処理を簡単に構築できます。
また、ユーザーが研究や実験データに対して使用されているPythonモジュールと組み合わせることで、データの登録から加工、グラフ化などより多様な処理を実現できます。

## Install

インストールは、下記コマンドを実行してください。

```bash
pip install --index-url https://<access_token_name>:<access_token>@gitlab.nims.go.jp/api/v4/projects/648/packages/pypi/simple --no-deps rdetoolkit
```

> <access_token_name>と<access_token>は、個人のアクセストークンもしくは、Wikiの開発者ドキュメントにインストール用のトークンを掲載しています。そちらのドキュメントを参照してインストールしてください。

## Usage

RDE構造化プログラム構築の一例です。任意のディレクトリに、下記で示したファイル・ディレクトリを準備します。この例では、`container`というディレクトリを作成して、開発を進めます。

- **main.py**
  - 構造化プログラムの起動処理を定義
- **requirements.txt**
  - 構造化プログラム構築で使用したいPythonパッケージを追加してください。必要に応じて`pip install`を実行してください。
- **modules**
  - 構造化処理で使用したいプログラムを格納してください。別セクションで説明します。

```bash
container/
├── main.py
├── requirements.txt
└── modules/
```

### 起動処理について

起動処理で主に実行処理は、

- 入力ファイルのチェック
- 入力ファイルとRDE構造化で規定する各種ディレクトリパスを取得する
- ユーザーごとで定義した具体的な構造化処理を実行

```python
import sys
import traceback

from modules import datasets_process
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.invoiceFile import backup_invoice_json_files
from rdetoolkit.models.rde2types import RdeFormatFlags, RdeInputDirPaths
from rdetoolkit.modeproc import (excel_invoice_mode_process,
                                     invoice_mode_process,
                                     multifile_mode_process,
                                     rdeformat_mode_process)
from rdetoolkit.rde2util import StorageDir
from rdetoolkit.rdelogger import get_logger, write_job_errorlog_file
from rdetoolkit.workflows import (check_files,
                                      generate_folder_paths_iterator)


def main() -> None:
    try:
        # Enabling mode flag and validating input file
        format_flags = RdeFormatFlags()
        srcpaths = RdeInputDirPaths(
            inputdata=StorageDir.get_specific_outputdir(False, "inputdata"),
            invoice=StorageDir.get_specific_outputdir(False, "invoice"),
            tasksupport=StorageDir.get_specific_outputdir(False, "tasksupport"),
        )
        raw_files_group, excel_invoice_files = check_files(srcpaths, fmt_flags=format_flags)

        # Backup of invoice.json
        invoice_org_filepath = backup_invoice_json_files(excel_invoice_files, format_flags)
        invoice_schema_filepath = srcpaths.tasksupport.joinpath("invoice.schema.json")

        # Execution of data set structuring process based on various modes
        for idx, rdeoutput_resource in enumerate(generate_folder_paths_iterator(raw_files_group, invoice_org_filepath, invoice_schema_filepath)):
            if format_flags.is_rdeformat_enabled:
                rdeformat_mode_process(srcpaths, rdeoutput_resource, datasets_process.dataset)
            elif format_flags.is_multifile_enabled:
                multifile_mode_process(srcpaths, rdeoutput_resource, datasets_process.dataset)
            elif excel_invoice_files is not None:
                excel_invoice_mode_process(srcpaths, rdeoutput_resource, excel_invoice_files, idx, datasets_process.dataset)
            else:
                invoice_mode_process(srcpaths, rdeoutput_resource, datasets_process.dataset)

    except StructuredError as e:
        traceback.print_exc(file=sys.stderr)
        write_job_errorlog_file(e.eCode, e.eMsg)
        logger.exception(e.eMsg)
        sys.exit(1)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        write_job_errorlog_file(999, "ERROR: unknown error")
        logger.exception(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 構造化処理の実装

入力データに対してデータ加工・グラフ化・機械学習用のcsvファイルの作成など処理を実行し、RDEへデータを登録できます。下記の書式に従っていただければ、独自の処理をRDEの構造化処理のフローに組み込み込むことが可能です。

`dataset()`は、以下の2つの引数を渡してください。

- srcpaths (RdeInputDirPaths): 処理のための入力リソースへのパス
- resource_paths (RdeOutputResourcePath): 処理結果を保存するための出力リソースへのパス

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    ...
```

今回の例では、`modules`以下に、`def display_messsage()`というダミー処理を定義し、独自の構造化処理を定義したいと思います。`modules/process.py`というファイルを作成します。

```python
# modules/process.py
def display_messsage(path):
    print(f"Test Message!: {path}")

def dataset(srcpaths, resource_paths):
    display_messsage(srcpaths)
    display_messsage(resource_paths)
```

続いて、起動処理`main.py`に以下の処理を追加します。

```python
# main.py
import sys
import traceback

- from modules import datasets_process
+ from modules import process #変更

def main() -> None:
    try:
        ...#割愛
            if format_flags.is_rdeformat_enabled:
                rdeformat_mode_process(
                    srcpaths,
                    rdeoutput_resource,
                    process.dataset #変更
                )
            elif format_flags.is_multifile_enabled:
                multifile_mode_process(
                    srcpaths,
                    rdeoutput_resource,
                    process.dataset #変更
                )
            elif excel_invoice_files is not None:
                excel_invoice_mode_process(
                    srcpaths,
                    rdeoutput_resource,
                    excel_invoice_files,
                    idx,
                    process.dataset #変更
                )
            else:
                invoice_mode_process(
                    srcpaths,
                    rdeoutput_resource,
                    process.dataset #変更
                )
```

### ローカル環境で動作させる場合

`data`ディレクトリに必要な入力データを追加することで、ローカル環境でも実行可能です。

```bash
container/
├── main.py
├── requirements.txt
├── modules/
│   ├── process.py
└── data/
    ├── inputdata/
    │   └── <処理したい実験データ>
    ├── invoice/
    │   └── invoice.json
    └── tasksupport/
        ├── metadata-def.json
        ├── invoice.schema.json
        └── invoice.json
```

## Contributing

1. Fork it (https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit)
2. Create your feature branch (`git checkout -b feature/newFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/newFeature`)
5. Create a new Merge Request
