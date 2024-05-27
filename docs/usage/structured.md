### 構造化処理を定義する

RDE構造化処理は、大きく分けて、以下の3つのフェーズに分けられます。

```mermaid
graph LR
    起動処理 --> カスタム構造化処理
    カスタム構造化処理 --> 終了処理
```

起動処理、終了処理は、rdetoolkitを使うことで簡単に実行できます。そのため、ユーザー自身は、ご自身のデータに対する処理を実行する`カスタム構造化処理`を定義するだけです。

### 起動処理

起動処理では、カスタム構造化処理を実行する前の処理を実行します。

!!! Reference
    API Documents: [rdetoolkit.workflows.run](rdetoolkit/workflows.md/#run)

#### 実装例

実装は、プログラムのエントリーポイントとなるファイルに実装することを推奨します。例えば、`main.py`や`run.py`というファイルを作成し、以下のように実装します。

```python
from modules import process #独自で定義した構造化処理関数
import rdetoolkit

# run()がRDE構造化の起動処理と後処理を実行
rdetoolkit.workflows.run(custom_dataset_function=process.dataset)
```

#### 具体的な処理について

起動処理は、次の処理を実行します。

- RDE構造化処理で必要なディレクトリの自動作成
- 入力ファイルを`raw`ディレクトリへ自動保存
- 入力ファイル・設定ファイルの内容から、各種モードに応じた読み込み処理
- 読み込んだファイルを、独自で定義したカスタム構造化処理に渡し実行

> 各種モードごとのファイル読み込みでは、ファイルの内容を読み込んでいません。そのため、ファイルに対する具体的な処理は、カスタム構造化処理等で定義してください。

```mermaid
graph TD
    init1[起動処理] --> init2[ディレクトリ作成]
    init2 --> init3{設定:save_raw}
    init3 -->|False|init5{モード選択}
    init3-->|True|init4[rawフォルダへ自動保存] --> init5
    init5-->|default|init6[invoiceモード]
    init5-->init7[Excelinvoiceモード]
    init5-->init8[マルチファイルモード]
    init5-->init9[RDEフォーマットモード]
    init6-->init10[カスタム構造化処理]
    init7-->init10
    init8-->init10
    init9-->init10
```

### カスタム用構造化処理関数の作成

rdetoolkitでは、独自の処理をRDEの構造化処理のフローに組み込み込むことが可能です。独自の構造化処理は、入力データに対してデータ加工・グラフ化・機械学習用のcsvファイルの作成など、データセット固有の処理を定義することで、RDEへ柔軟にデータを登録可能です。

#### 実装例

仮に、rdetoolkitへ渡す独自データセット関数を、`dataset()`とします。`dataset()`は、以下の2つの引数を渡してください。

!!! Tip

    独自のクラス・関数群を定義する場合、必ず`RdeInputDirPaths`, `RdeOutputResourcePath`を引数で受け取り可能な関数でwrapしてください。

```python
# wrap用関数
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    # この関数内でユーザ自身が定義したクラスや関数を呼び出す
    ...
```

これの引数には、構造化するために必要な各種ディレクトリ情報やファイル情報が格納されています。特に、`RdeOutputResourcePath`には、ファイル保存先情報が格納されています。

- srcpaths (RdeInputDirPaths): 入力されたリソースファイルのパス情報
- resource_paths (RdeOutputResourcePath): 処理結果を保存するための出力リソースパス情報

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

#### 起動処理へ組み込む

この`dataset()`を起動するためには、先ほどの起動処理で作成したエントリーポイントとなるファイル(`main.py`など)に以下のように定義します。

```python
from modules import process #独自で定義した構造化処理関数
import rdetoolkit

# run()にカスタム構造化処理をを渡す
rdetoolkit.workflows.run(custom_dataset_function=process.dataset)
```

### 終了処理について

続いて、`rdetoolkit.workflow.run()`が実行する終了処理について説明します。

- 生成ファイル、入力ファイルのバリデーション
- Main画像から代表画像の自動保存
- データタイル説明欄へ指定メタデータの自動記述

```mermaid
graph TD
    end1[カスタム構造化処理] --> end2[バリデーション]
    end2 --> end3{設定:save_thumbnail_image}
    end3 -->|False|end6[説明欄の自動記述]
    end3-->|True|end5[Main画像からサムネイル画像保存]
    end5 --> end6
```

#### 各種ファイルのバリデーション

バリデーションは、次のファイルが対象となります。これらのファイルは、データセット開設時、データ登録時に重要なファイルとなります。

- `tasksupport/metadata-def.json`
- `tasksupport/invoice.shcema.json`
- `data/invoice/invoice.json`

#### 説明欄への自動転記

以下のドキュメントを参照してください。

- [データタイル説明欄への自動転記](feature_description.md)