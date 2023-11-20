# クイックスタート

RDE構造化プログラム構築の一例です。

## プロジェクトを作成する

まず、RDE構造化プログラムに必要なファイルを準備します。以下のコマンドをターミナルやシェル上で実行してください。

```shell
python3 -m rdetoolkit init
```

コマンドが正しく動作すると、下記で示したファイル・ディレクトリが生成されます。

この例では、`container`というディレクトリを作成して、開発を進めます。

- **requirements.txt**
    - 構造化プログラム構築で使用したいPythonパッケージを追加してください。必要に応じて`pip install`を実行してください。
- **modules**
    - 構造化処理で使用したいプログラムを格納してください。別セクションで説明します。
- **main.py**
    - 構造化プログラムの起動処理を定義
- **data/inputdata**
    - 構造化処理対象データファイルを配置してください。
- **data/invoice**
    - ローカル実行させるためには空ファイルでも必要になります。
- **data/tasksupport**
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

入力データに対してデータ加工・グラフ化・機械学習用のcsvファイルの作成など処理を実行し、RDEへデータを登録できます。下記の書式に従っていただければ、独自の処理をRDEの構造化処理のフローに組み込み込むことが可能です。

`dataset()`は、以下の2つの引数を渡してください。

- srcpaths (RdeInputDirPaths): 処理のための入力リソースへのパス
- resource_paths (RdeOutputResourcePath): 処理結果を保存するための出力リソースへのパス

!!! Tip
    - [RdeInputDirPaths](rdetoolkit/models/rde2types.md/#RdeInputDirPaths)
    - [RdeOutputResourcePath](rdetoolkit/models/rde2types.md/#RdeOutputResourcePath)

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    ...#任意の処理
```

今回の例では、`modules`以下に、`def display_messsage()`というダミー処理を定義し、独自の構造化処理を定義したいと思います。`modules/process.py`というファイルを作成します。

```python
# modules/process.py
def display_messsage(path):
    print(f'Test Message: {path}')

def dataset(srcpaths, resource_paths):
    display_messsage(srcpaths)
    display_messsage(resource_paths)
```

## 起動処理について

続いて、`rdetoolkit.workflow.run()`を使って、起動処理を定義します。起動処理で主に実行処理は、

- 入力ファイルのチェック
- 入力ファイルとRDE構造化で規定する各種ディレクトリパスを取得する
- ユーザーごとで定義した具体的な構造化処理を実行

```python
from modules import process #独自で定義した構造化処理関数
import rdetoolkit

#独自で定義した構造化処理関数を引数として渡す
rdetoolkit.workflows.run(custom_dataset_function=process.dataset)
```

もし、独自の構造化処理を渡さない場合、以下のように定義してください。

```python
import rdetoolkit

rdetoolkit.workflows.run()
```

## 作成したプログラムをローカル環境で動作させる場合

各自のローカル環境で、デバッグやテスト的にRDEの構造化処理を実行したい場合、`data`ディレクトリに必要な入力データを追加することで、ローカル環境でも実行可能です。ディレクトリ構造は、以下のように、main.pyと同じ階層にdataディレクトリを配置していただければ動作します。

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

| ファイル名/フォルダ名 | 説明 |
| ------------------ | --- |
| main.py            | 起動スクリプト |
| modules            | 実行したい独自処理を格納したフォルダ |
| data/inputdata     | 構造化処理対象の入力データを格納するフォルダ |
| data/invoice       | invoice.jsonを格納するフォルダ |
| data/tasksupport   | その他プログラム実行時に必要なファイルを格納するフォルダ<br>現状以下のファイルを格納してください。<br>- metadata-def.json <br>- invoice.schema.json <br>- invoice.json|

## プログラムの実行

ターミナルや端末、コンソールを開いて、以下のコードを実行してください。

=== "Unix/macOS"

    ```shell
    python3 main.py
    ```

=== "Windows"

    ```shell
    python main.py
    ```

## 実行結果

プログラムを実行すると、自動的にフォルダ構成が作成されます。

!!! Warning

    今回の例題では下記のようなファイルが作成されません。

    自動的に作成される構成例ですので、あらかじめご注意ください。

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
    ├── meta/
    │   └── meta.json
    ├── main_image/
    │   └── sample_main_image.png
    ├── other_image/
    │   └── sample_other_image.png
    ├── structured/
    │   └── struct.csv
    ├── thumbnail/
    │   └── !_sample_main_image.png
    ├── (jobs.faild)
    └── tasksupport/
        ├── metadata-def.json
        ├── invoice.schema.json
        └── invoice.json
```

実行後に生成されるファイルは以下の通りです。

| ファイル名/フォルダ名 | 説明 |
| ------------------ | --- |
| meta               | メタデータに関するファイルを格納 |
| main_image         | 代表画像となる画像データファイルを格納するフォルダ |
| data/inputdata     | 上記以外のその他画像データを格納するフォルダ |
| data/structured    | 構造化処理後のファイルでブラウザで表示できる画像を除くファイルを格納するフォルダ |
| data/thumbnail     | 代表画像フォルダ。main_imageの画像が自動的に格納されます。 |
| jobs.faild         | プログラム実行エラーが発生すると生成されます。RDEに登録される際は、このファイルは格納されません。 |
