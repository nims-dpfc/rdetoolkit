# RDEToolKit

![GitHub Release](https://img.shields.io/github/v/release/nims-dpfc/rdetoolkit)
[![python.org](https://img.shields.io/badge/Python-3.9%7C3.10%7C3.11-%233776AB?logo=python)](https://www.python.org/downloads/release/python-3917/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/nims-dpfc/rdetoolkit/blob/main/LICENSE)
[![Issue](https://img.shields.io/badge/issue_tracking-github-orange)](https://github.com/nims-dpfc/rdetoolkit/issues)
![workflow](https://github.com/nims-dpfc/rdetoolkit/actions/workflows/main.yml/badge.svg)
![coverage](img/coverage.svg)

RDEToolKitは、RDE構造化プログラムのワークフローを作成するための基本的なPythonパッケージです。RDEToolKitの各種モジュールを使うことで、RDEへの研究・実験データの登録処理を簡単に構築できます。主に、RDEToolKitは、ユーザーが定義した構造化処理の前処理・後処理をサポートします。また、ユーザーが研究や実験データに対して使用されているPythonモジュールと組み合わせることで、データの登録から加工、グラフ化などより多様な処理を実現可能です。これにより、データのクレンジング、変換、集計、可視化など、データサイエンスのワークフロー全体を効率的に管理できます。

<br>

![overview_workflow](img/overview_workflow.svg)

## 主な特徴

- **モジュール化**: RDEデータ登録に必要な前処理や後処理がモジュールとして提供されており、カスタマイズしたい処理を実装するだけで、柔軟に構造処理を実装できます。
- **柔軟なデータ処理**: データの前処理、変換、可視化など、さまざまなデータ処理をサポートします。
- **簡単なインストール**: `pip install rdetoolkit` コマンドで簡単にインストールできます。
- **拡張性**: ユーザーが定義したカスタムデータセット処理関数を使用して、特定のデータ処理ニーズに対応できます。これにより、特定の研究や実験の要件に合わせたデータ処理が可能です。
- **統合**: 他のPythonモジュールと組み合わせることで、データの登録から加工、グラフ化など、より多様な処理を実現可能です。これにより、構造化処理全体を一元管理できます。

## インストール

RDEToolKitはPythonパッケージとして提供されており、以下のコマンドでインストールできます。

```bash
pip install rdetoolkit
```

## Usage

[クイックスタート](usage/quickstart.md) を参照してください。

|       Sample1: ユーザー定義構造化処理あり       |            Sample2: ユーザー定義構造化処理なし            |
| :---------------------------------------------: | :-------------------------------------------------------: |
| ![quick-sample-code](img/quick-sample-code.svg) | ![quick-sample-code-none](img/quick-sample-code-none.svg) |

インストール後、以下のコマンドを実行してください。

```shell
python -m rdetoolkit init
```

実行するスクリプトと、事前に以下のディレクトリを作成してください。`invoice.json`と`invoice.schema.json`は、[こちら](usage/metadata_definition_file)のページを参照してください。

```shell
.
├── data
│   ├── inputdata
│   ├── invoice
│   │   └── invoice.json
│   └── tasksupport
│       └── invoice.schema.json
├── main.py
├── modules
└── requirements.txt
```

```python
import rdetoolkit


# User-defined Processing
def display_messsage(path):
    print(f'Test Message!: {path}')

def custom_graph():
    print('graph')

def custom_extract_metadata():
    print('extract metadata')

def dataset(srcpaths, resource_paths):
    display_messsage(srcpaths)
    display_messsage(resource_paths)
    custom_graph()
    custom_extract_metadata()

# RDEToolKit
rdetoolkit.workflows.run(custom_dataset_function=dataset)
```

## API Documentation

[API Documentation](rdetoolkit/impl/compressed_controller) を参照してください。

### modules

- [workflows](rdetoolkit/workflows): ワークフローの定義と管理を行うモジュール。
- [config](rdetoolkit/config): 設定ファイルの読み込みと管理を行うモジュール。
- [fileops](rdetoolkit/fileops): RDE関連のファイル操作を提供するモジュール。
- [rde2util](rdetoolkit/rde2util): RDE関連のユーティリティ関数を提供するモジュール。
- [invoicefile](rdetoolkit/invoicefile): 請求書ファイルの処理を行うモジュール。
- [validation](rdetoolkit/validation): データの検証を行うモジュール。
- [modeproc](rdetoolkit/modeproc): モード処理を行うモジュール。
- [img2thumb](rdetoolkit/img2thumb): 画像をサムネイルに変換するモジュール。
- [rdelogger](rdetoolkit/rdelogger): ロギング機能を提供するモジュール。
- [errors](rdetoolkit/errors): エラーハンドリングを行うモジュール。
- [exceptions](rdetoolkit/exceptions): 例外処理を行うモジュール。

### models

- [config](rdetoolkit/models/config): 設定ファイルの読み込みと管理を行うモジュール。
- [invoice_schema](rdetoolkit/models/invoice_schema): 送り状のスキーマを定義するモジュール。
- [metadata](rdetoolkit/models/metadata): メタデータの管理を行うモジュール。
- [rde2types](rdetoolkit/models/rde2types): RDE関連の型定義を提供するモジュール。
- [result](rdetoolkit/models/result): 処理結果を管理するモジュール。

### impl

- [compressed_controller](rdetoolkit/impl/compressed_controller): 圧縮ファイルの管理を行うモジュール。
- [input_controller](rdetoolkit/impl/input_controller): 入力モードの管理を行うモジュール。

### interface

- [filechecker](rdetoolkit/interface/filechecker)

### cmd

- [command](rdetoolkit/cmd/command)

## Contributing

RDEToolKitへのコントリビュートをしていただくには、以下のドキュメントを参照してください。

[Contributing](contribute/home.md)

## ライセンス

RDEToolKitはMITライセンスの下で提供されています。詳細については、[LICENSE](https://github.com/nims-dpfc/rdetoolkit/blob/main/LICENSE)ファイルを参照してください。
