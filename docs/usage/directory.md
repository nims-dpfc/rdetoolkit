## RDE構造化処理で扱うディレクトリとパスの取得

### サポートするディレクトリ構造

RDE構造化処理では以下のディレクトリをサポートしています。

#### 入力

以下の3つのディレクトリは、構造化処理実行時、システム側で自動で生成されるディレクトリになります。そのため、ローカルで構造化処理を実行する場合、以下のディレクトリは、事前に作成してください。作成する場所は、プログラムを実行するディレクトリと同じ階層に、`data`ディレクトリを作成し、その`data`ディレクトリ配下に、下記ディレクトリを作成してください。

| ディレクトリ名 | 種別 | 用途 |
| ------------ | --- | ---- |
| inputdata | 入力データ | 入力データファイルを格納 |
| invoice | 送り状データ | 送り状(invoice.json)が格納されます。 |
| tasksupport | 画像ファイル | 事前にテンプレート作成時に登録した構造化処理補助ファイル群を格納 |

#### 構造化処理を実行前のディレクトリ例

ローカルで構造化処理を実行する場合、以下のように事前にディレクトリを作成する。

```shell
.
├── modules
│   └── custom_modules.py
├── data
│   ├── inputdata
│   │   └── sample_data.ras
│   ├── invoice
│   │   └── invoice.json
│   └── tasksupport
│       ├── invoice.schema.json
│       └── metadata-def.json
├── main.py # 起動処理を定義(entry point)
└── requirements.txt
```

#### 出力

出力ディレクトリは、構造化処理を実行した結果を格納するディレクトリ群です。rdetoolkitでは、構造化処理実行すると、下記ディレクトリが自動で作成されます。

| ディレクトリ名 | 種別 | 用途 |
| ------------ | --- | ---- |
| meta | 主要パラメータ情報ファイル | 主要パラメータ情報ファイル(`metadata.json`)を格納 |
| main_image | 画像ファイル | RDEデータセット詳細画像として表示されるサムネイルファイル |
| other_image | 画像ファイル | RDEデータセットファイル一覧にのみ表示される |
| thumbnail | 画像ファイル | RDEデータセット一覧に表示される画像ファイル |
| attachment | - | 添付ファイル(※) |
| nonshared_raw | - | 共有不可能なファイル群を配置 |
| raw | rawデータファイル | 共有可能なrawファイル群を配置。入力データを配置する。 |
| structured | 構造化ファイル | 構造化処理により生成されたファイルを配置。入力データを配置する。 |
| logs | - | データセットに登録・反映されませんが、ログを蓄積するためのディレクトリが作成されます。|
| temp | - | データセットに登録・反映されませんが、一時的ディレクトリとして、tempディレクトリが作成されるケースがあります。 |

!!! Warning
    * attachmentは、rdetoolkitでは自動で生成されません。

#### ローカルで構造化処理実行後のディレクトリ例

```shell
├── modules
│   └── custom_modules.py
├── data
│   ├── inputdata
│   │   └── excelinvoice.zip
│   ├── invoice
│   │   └── invoice.json
│   ├── logs
│   │   └── rdesys.log
│   ├── main_image
│   │   └── iamge0.png
│   ├── meta
│   │   └── metadata.json
│   ├── nonshared_raw
│   ├── other_image
│   │   ├── sub_image1.png
│   │   └── sub_image2.png
│   ├── raw
│   │   ├── DMF-pos-1.xyz
│   │   ├── li-mole.inp
│   │   └── opt.xyz
│   ├── structured
│   │   └── sample.csv
│   ├── tasksupport
│   │   ├── invoice.schema.json
│   │   └── metadata-def.json
│   ├── temp
│   │   └── invoice_org.json
│   └── thumbnail
│       └── image.png
├── main.py
└── requirements.txt
```

### ディレクトリとカスタム構造化処理の制約

ユーザー自身が、カスタム構造化処理を定義する際が、`RdeInputDirPaths`, `RdeOutputResourcePath`を引数で受け取れり可能な関数を定義しなければなりません。

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    # この関数内でユーザ自身が定義したクラスや関数を呼び出す
    ...
```

!!! Reference
    - API Documentation: [RdeInputDirPaths - rde2types](rdetoolkit/models/rde2types.md/#rdeinputdirpaths)
    - API Documentation: [RdeOutputResourcePath - rde2types](rdetoolkit/models/rde2types.md/#rdeoutputresourcepath)

`RdeInputDirPaths`は、入力で扱われるディレクトリパスやファイルパス群を格納してます。ディレクトリパスは、`pathlib.Path`オブジェクトで格納されています。

```python
@dataclass
class RdeInputDirPaths:
    inputdata: Path
    invoice: Path
    tasksupport: Path
```

関数内ディレクトリパスにアクセスする場合、以下の定義でディレクトリパスを取得できます。

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    inputdata_dir = srcpaths.inputdata
    invoice_dir = srcpaths.invoice
    tasksupport = srcpaths.tasksupport
```

`RdeOutputResourcePath`では、出力で扱われるディレクトリパス群を格納しています。

```python
@dataclass
class RdeOutputResourcePath:
    raw: Path
    rawfiles: tuple[Path, ...]
    struct: Path
    main_image: Path
    other_image: Path
    meta: Path
    thumbnail: Path
    logs: Path
    invoice: Path
    invoice_schema_json: Path
    invoice_org: Path
    temp: Path | None = None
    invoice_patch: Path | None = None
    attachment: Path | None = None
    nonshared_raw: Path | None = None
```

関数内ディレクトリパスにアクセスする場合、以下の定義でディレクトリパスを取得できます。

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    rawfiles = resource_paths.rawfiles
    raw_dir = resource_paths.raw
    struct_dir = resource_paths.struct
    main_image_dir = resource_paths.main_image
```
