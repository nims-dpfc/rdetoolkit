# クイックスタート

RDE構造化プログラム構築の一例です。

## プロジェクトを作成する

まず、RDE構造化プログラムに必要なファイルを準備します。以下のコマンドをターミナルやシェル上で実行してください。

=== "Unix/macOS"

    ```shell
    python3 -m rdetoolkit init
    ```

=== "Windows"

    ```powershell
    py -m rdetoolkit init
    ```

コマンドが正しく動作すると、下記で示したファイル・ディレクトリが生成されます。

この例では、`container`というディレクトリを作成して、開発を進めます。

- requirements.txt
    - 構造化プログラム構築で使用したいPythonパッケージを追加してください。必要に応じて`pip install`を実行してください。
- modules
    - 構造化処理で使用したいプログラムを格納してください。別セクションで説明します。
- main.py
    - 構造化プログラムの起動処理を定義
- data/inputdata
    - 構造化処理対象データファイルを配置してください。
- data/invoice
    - ローカル実行させるためには空ファイルでも必要になります。
- data/tasksupport
    - 構造化処理の補助するファイル群を配置してください。

```shell
container
├── data
│   ├── inputdata
│   ├── invoice
│   │   └── invoice.json
│   └── tasksupport
│       ├── invoice.schema.json
│       └── metadata-def.json
├── main.py
├── modules
└── requirements.txt
```

## 構造化処理の実装

RDE構造化処理は、大きく分けて、以下の3つのフェーズに分けられます。

```mermaid
graph LR
    起動処理 --> カスタム構造化処理
    カスタム構造化処理 --> 終了処理
```

起動処理、終了処理は、rdetoolkitを使うことで簡単に実行できます。そのため、ユーザー自身は、ご自身のデータに対する処理を実行する **カスタム構造化処理** を定義するだけです。

!!! Tip "Documents"
    [カスタム用構造化処理関数の作成](structured.md/#_5)

### カスタム用構造化処理関数の作成

rdetoolkitでは、独自の処理をRDEの構造化処理のフローに組み込み込むことが可能です。独自の構造化処理は、入力データに対してデータ加工・グラフ化・機械学習用のcsvファイルの作成など、データセット固有の処理を定義することで、RDEへ柔軟にデータを登録可能です。

仮に、rdetoolkitへ渡す独自データセット関数を、`dataset()`とします。`dataset()`は、以下の2つの引数を渡してください。

- srcpaths (RdeInputDirPaths): 処理のための入力リソースへのパス
- resource_paths (RdeOutputResourcePath): 処理結果を保存するための出力リソースへのパス

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    ...
```

!!! Reference
    - API Documentation: [RdeInputDirPaths - rde2types](rdetoolkit/models/rde2types.md/#rdeinputdirpaths)
    - API Documentation: [RdeOutputResourcePath - rde2types](rdetoolkit/models/rde2types.md/#rdeoutputresourcepath)

今回の例では、`modules`以下に、`display_messsage()`, `custom_graph()`, `custom_extract_metadata()`というダミー処理を定義し、独自の構造化処理を定義します。これらの関数は、`modules/process.py`というファイルを作成し定義します。以下の2つの引数を渡す関数でなければ、rdetoolkitは正しく処理が実行できません。

```python
# modules/process.py
def display_messsage(path):
    print(f"Test Message!: {path}")

def custom_graph():
    print("graph")

def custom_extract_metadata():
    print("extract metadata")

def dataset(srcpaths, resource_paths):
    display_messsage(srcpaths)
    display_messsage(resource_paths)
    custom_graph()
    custom_extract_metadata()
```

上記の`dataset()`を次のセクションの起動処理で実行します。

### 起動処理について

続いて、`rdetoolkit.workflow.run()`を使って、構造化処理を実行します。起動処理で主に実行処理は、

- 入力ファイルのチェック
- 入力ファイルとRDE構造化で規定する各種ディレクトリパスを取得する
- ユーザーごとで定義した具体的な構造化処理を実行(上記セクションで定義した`dataset()`など)
- 各種入力ファイルのバリデーション

!!! Reference
    - API Documentation: [run - workflows](rdetoolkit/workflows.md/#run)

今回の例では、`main.py`を作成し、`modules/process.py`で定義した`dataset()`を実行します。

```python
import rdetoolkit
from modules.modules import dataset #独自で定義した構造化処理関数

#独自で定義した構造化処理関数を引数として渡す
rdetoolkit.workflows.run(custom_dataset_function=dataset)
```

もし、独自の構造化処理を渡さない場合、以下のように定義してください。

```python
import rdetoolkit

rdetoolkit.workflows.run()
```

## ローカル環境で構造化処理を動作させる

上記の手順で定義した`main.py`を、各自のローカル環境で、デバッグやテスト的にRDEの構造化処理を実行したい場合、`data`ディレクトリ、`tasksupport`ディレクトリに必要な入力データを追加することで、ローカル環境で実行可能です。ディレクトリ構造は、以下のように、main.pyと同じ階層にdataディレクトリを配置していただければ動作します。

```shell
container/
├── main.py
├── requirements.txt
├── modules/
│   └── modules.py
└── data/
    ├── inputdata/
    │   └── <処理したい実験データ>
    ├── invoice/
    │   └── invoice.json
    └── tasksupport/
        ├── metadata-def.json
        └── invoice.schema.json
```

> 上記のディレクトリ構造は、あくまで一例です。data/inputdataディレクトリ、tasksupportディレクトリは、必要なファイルを適宜追加/修正してください。

下記のように実行してください。

```shell
cd container
python3 main.py
```

## 次のステップ

- [カスタム構造化処理を実装する](structured_process/structured.md)
- [RDEToolKitの設定ファイルと制御できる機能を知る](config/config.md)
- [RDEのデータ登録モードを指定する](config/mode.md)
- [テンプレートファイルを知る](metadata_definition_file.md)
