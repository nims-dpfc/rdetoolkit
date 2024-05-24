RDEの構造化処理でサポートしているモードは、以下4つのモードをサポートしています。

| モード名 | 起動条件 |
| --- | --- |
| invoiceモード | デフォルトで起動 |
| Excelinvoiceモード | 入力ファイルに`*._excel_invoice.xlsx`を格納 |
| マルチデータタイル | 設定ファイルに`extended_mode: 'MultiDataTile'`を追加 |
| RDEフォーマットモード | 設定ファイルに`extended_mode: 'rdeformat'`を追加 |

ここでは、各種モードの説明と実行例をまとめました。

## invoiceモード

- 起動条件: デフォルトで起動
- 備考: モード切り替えはRdeToolKitで定義

このモードは、通常のRDE登録画面でデータを登録するモードを指します。一番、基本的かつデフォルトのモードになります。

以下のように、Entry画面から、データを投入するモードです。

![invoice_mode](../img/invoice_mode.svg)

### invoiceモード実行例

#### 投入データ

- 登録ファイル
  - test23_1.csv
- tasksupport
  - 追加なし

#### 実行前ファイル構成

```shell
$ tree data
data
├── inputdata
│   └── test23_1.csv
├── invoice
│   └── invoice.json
└── tasksupport
    ├── invoice.schema.json
    └── metadata-def.json

4 directories, 4 files
```

#### 実行後ファイル構成

```shell
$ tree data
data
├── inputdata
│   └── test23_1.csv
├── invoice
│   └── invoice.json
├── logs
│   └── rdesys.log
├── main_image
├── meta
├── other_image
├── raw
│   └── test23_1.csv
├── structured
├── tasksupport
│   ├── invoice.schema.json
│   └── metadata-def.json
├── temp
└── thumbnail

12 directories, 6 files
```

`inputdata`が`raw`にコピーされている。invoice.jsonの書き換えはしない。

## ExcelInvoiceモード

- 起動条件: 入力ファイルに`*._excel_invoice.xlsx`を格納
- 備考: モード切り替えはRdeToolKitで定義

このモードは、一度に複数件のデータセットを登録するものモードです。通常のinvoiceモードでは、一件ずつしかデータセットの登録実行できませんが、Excelinvoiceモードを使うと、一度に複数データセットを登録することができます。

このモードの起動条件として、入力ファイルに、`*._excel_invoice.xlsx`という命名規則を持つExcelファイルを投入するとExcelinvoiceとして登録されます。

このExcelinvoiceのテンプレートファイルはRDEへ問い合わせください。

![excelinvoice](../img/excelinvoice.svg)

!!! Note
    ExcelInvoiceには、ファイルモードとフォルダモードという概念があります。[File Mode / Folder Mode](file_folder_mode.md)を参照ください。

### ExcelInvoiceモード実行例

#### 投入データ

- 登録ファイル(data/inputdata)
  - data.zip (投入ファイルをzip圧縮したもの)
  - sample_excel_invoice.xlsx (この事例では3行3データタイル分を記載)
- tasksupport
  - 追加なし

#### 実行前ディレクトリ構成

> `data/invoice/invoice.json`は、空のjsonファイルでも構いません。

```shell
container/
├── main.py
├── requirements.txt
├── modules/
│   ├── <任意の構造化処理モジュール>
└── data
    ├── inputdata
    │   ├── data.zip
    │   └── sample_excel_invoice.xlsx
    ├── invoice
    │   └── invoice.json
    └── tasksupport
        ├── invoice.schema.json
        └── metadata-def.json
```

#### data.zipの内容

エクセルインボイスに3行追加するため3ファイルzip化する。

```shell
$ unzip -t data.zip
Archive:  data.zip
    testing: data0000.dat             OK
    testing: data0001.dat             OK
    testing: data0002.dat             OK
```

![excelinvoice_demo](../img/excelinvoice_demo.svg)

#### 実行後

- data.zipの内容は展開される
- sample_excel_invoice.xlsxの記入内容に従ってdividedを含むフォルダに展開
- 各invoice.jsonは、excel_invoiceの各行から読み出した情報が入力される

```console
data
├── divided
│   ├── 0001
│   │   ├── invoice
│   │   │   └── invoice.json
│   │   ├── logs
│   │   ├── main_image
│   │   ├── meta
│   │   ├── other_image
│   │   ├── raw
│   │   │   └── data0001.dat
│   │   ├── structured
│   │   ├── temp
│   │   └── thumbnail
│   └── 0002
│       ├── invoice
│       │   └── invoice.json
│       ├── logs
│       ├── main_image
│       ├── meta
│       ├── other_image
│       ├── raw
│       │   └── data0002.dat
│       ├── structured
│       ├── temp
│       └── thumbnail
├── inputdata
│   ├── data.zip
│   └── sample_excel_invoice.xlsx
├── invoice
│   └── invoice.json
├── logs
│   └── rdesys.log
├── main_image
├── meta
├── other_image
├── raw
│   └── data0000.dat
├── structured
├── tasksupport
│   ├── invoice.schema.json
│   └── metadata-def.json
├── temp
│   ├── data0000.dat
│   ├── data0001.dat
│   ├── data0002.dat
│   └── invoice_org.json
└── thumbnail
```

#### dividedフォルダ以下の内容について

`divided/0001/invoice/invoice.json`の内容は、事前に配置されたinvoice.jsonがコピーされ`basic/dataName`,
`basic/dataOwnerId` がエクセルインボイスの内容で書き換えが行われている。

書き換え後の、`data/invoice/invoice.json`

```json
{
    "datasetId": "ab9536f2-5fe4-49c4-bb82-dd8212453d85",
    "basic": {
        "dateSubmitted": "2023-03-14",
        "dataOwnerId": "153cbe4798cb8c1c3c0fc66062c7e55a9b4255fe3364613035643239",
        "dataName": "dumm.dat",
        "instrumentId": null,
        "experimentId": null,
        "description": null
    },
    "custom": null
}
```

書き換え後の、`data/divided/0001/invoice/invoice.json`

```json
{
    "datasetId": "e751fcc4-b926-4747-b236-cab40316fc49",
    "basic": {
        "dateSubmitted": "2023-03-14",
        "dataOwnerId": "97e05f8b9ed6b4b5dd6fd50411a9c163a2d4e38d6264623666383663",
        "dataName": "data0001.dat",
        "instrumentId": null,
        "experimentId": null,
        "description": null
    }
}
```

!!! Warning
    - `smple.zip`に不要なファイルが含まれていないか確認する。Mac特有の`.DS_Store`ファイルが格納されている場合、実行エラーが発生します。
    - エクセルインボイスファイルを開いたまま実行している場合、Microsoft特有のファイル(`~$`から始まるファイル)が残ってしまい、実行エラーが発生します。
    - ローカルで実行する場合、tempフォルダに前回の実行結果が残っているとエラーが発生します。

### フォルダを含むzipのExcelInvoiceモード実行例

フォルダを含むzipファイルを登録する方法は、zipファイルは以下の通りです。

!!! Note
    ExcelInvoiceには、ファイルモードとフォルダモードという概念があります。[File Mode / Folder Mode](file_folder_mode.md)を参照ください。

```shell
# フォルダありでzip
$ zip data_folder.zip -r ./inputdata -x \*/.DS_Store *\.xlsx
  adding: inputdata/ (stored 0%)
  adding: inputdata/data0001.dat (stored 0%)
  adding: inputdata/data0000.dat (stored 0%)
  adding: inputdata/data0002.dat (stored 0%)
```

## RDEformatモード

RDEフォーマットモードは、データセットのモックを作成するモードです。データ登録時に、具体的な構造化処理は行わず、指定された入力データをRDEデータセットの形式に登録をします。

入力データとして、以下のフォーマットを持つzip形式のファイルを投入する必要があります。zipファイルの中に、`invoice`, `main_image`, `other_image`, `structured`というディレクトリがあり、その中に、それぞれのデータを格納してください。zipファイルは、すでに構造化処理が実行され出力された想定のファイルを格納し、そのデータを指定フォルダに格納するイメージです。

```text
|- sample.zip
    |- invoice/
    |   |- invoice.json
    |- main_image/
    |   |- xxxx.png
    |- other_image/
    |   |- xxxx.png
    |- structured/
        |- sample.csv
```

![rdeformat](../img/rdeformat.svg)

### RDEformatモード実行例

#### 投入データ

- 登録ファイル
    - structured.zip (RDEformat形式で展開されたファイル一式をzipでまとめたもの)
- tasksupport
    - .rdeconfig.yml

!!! Note
    設定ファイル`.rdeconfig.yml`は、[設定ファイル - config](config.md)を参照ください。

structured.zipの内容は下記の通りです。

```shell
# unzip -t structured.zip
Archive: structured.zip
    testing: divided/                 OK
    testing: divided/0002/            OK
    testing: divided/0002/meta/       OK
    testing: divided/0002/meta/metadata.json   OK
    testing: divided/0002/structured/   OK
    testing: divided/0002/structured/test23_2-output.html   OK
    testing: divided/0002/structured/test23_2-output.csv   OK
    testing: divided/0002/main_image/   OK
    testing: divided/0002/main_image/test23_2-output.png   OK
    testing: divided/0002/raw/        OK
    testing: divided/0002/raw/test23_2.csv   OK
    testing: divided/0001/            OK
    testing: divided/0001/meta/       OK
    testing: divided/0001/meta/metadata.json   OK
    testing: divided/0001/structured/   OK
    testing: divided/0001/structured/test23_1-output.html   OK
    testing: divided/0001/structured/test23_1-output.csv   OK
    testing: divided/0001/main_image/   OK
    testing: divided/0001/main_image/test23_1-output.png   OK
    testing: divided/0001/raw/        OK
    testing: divided/0001/raw/test23_1.csv   OK
    testing: meta/                    OK
    testing: meta/metadata.json       OK
    testing: structured/              OK
    testing: structured/test23_0-output.html   OK
    testing: structured/test23_0-output.csv   OK
    testing: main_image/              OK
    testing: main_image/test23_0-output.png   OK
    testing: raw/                     OK
    testing: raw/test23_0.csv         OK
No errors detected in compressed data of data/inputdata/structured.zip.
```

上記の出力はinvoice.jsonファイルを含んでいたときのものではないが、invoice.jsonも含めたものもテストをしている。

#### 実行後ファイル構成

```shell
data
├── divided
│   ├── 0001
│   │   ├── invoice
│   │   │   └── invoice.json
│   │   ├── logs
│   │   ├── main_image
│   │   │   └── test23_1-output.png
│   │   ├── meta
│   │   │   └── metadata.json
│   │   ├── other_image
│   │   ├── raw
│   │   │   └── test23_1.csv
│   │   ├── structured
│   │   │   ├── test23_1-output.csv
│   │   │   └── test23_1-output.html
│   │   ├── temp
│   │   └── thumbnail
│   │       └── test23_1-output.png
│   └── 0002
│       ├── invoice
│       │   └── invoice.json
│       ├── logs
│       ├── main_image
│       │   └── test23_2-output.png
│       ├── meta
│       │   └── metadata.json
│       ├── other_image
│       ├── raw
│       │   └── test23_2.csv
│       ├── structured
│       │   ├── test23_2-output.csv
│       │   └── test23_2-output.html
│       ├── temp
│       └── thumbnail
│           └── test23_2-output.png
├── inputdata
│   └── structured.zip
├── invoice
│   └── invoice.json
├── logs
│   └── rdesys.log
├── main_image
│   └── test23_0-output.png
├── meta
│   └── metadata.json
├── other_image
├── raw
│   └── test23_0.csv
├── structured
│   ├── test23_0-output.csv
│   └── test23_0-output.html
├── tasksupport
│   ├── invoice.schema.json
│   └── metadata-def.json
├── temp
│   ├── divided
│   │   ├── 0001
│   │   │   ├── invoice
│   │   │   │   └── invoice.json
│   │   │   ├── main_image
│   │   │   │   └── test23_1-output.png
│   │   │   ├── meta
│   │   │   │   └── metadata.json
│   │   │   ├── raw
│   │   │   │   └── test23_1.csv
│   │   │   └── structured
│   │   │       ├── test23_1-output.csv
│   │   │       └── test23_1-output.html
│   │   └── 0002
│   │       ├── invoice
│   │       │   └── invoice.json
│   │       ├── main_image
│   │       │   └── test23_2-output.png
│   │       ├── meta
│   │       │   └── metadata.json
│   │       ├── raw
│   │       │   └── test23_2.csv
│   │       └── structured
│   │           ├── test23_2-output.csv
│   │           └── test23_2-output.html
│   ├── invoice
│   │   └── invoice.json
│   ├── invoice_org.json
│   ├── main_image
│   │   └── test23_0-output.png
│   ├── meta
│   │   └── metadata.json
│   ├── raw
│   │   └── test23_0.csv
│   └── structured
│       ├── test23_0-output.csv
│       └── test23_0-output.html
└── thumbnail
    └── test23_0-output.png

51 directories, 45 files
```

structured.zipがtempフォルダに展開されたのちに規程のフォルダに展開される。

#### invoice.jsonをzipに含めた場合

RDEformatモードでは、投入した`invoice.json`は利用されず`invoice/invoice.json`がコピーされる

!!! Warning
    - RDEformatモードでは、`invoice/invoice.json`が利用される(dividedにもコピー)
    - tempフォルダに展開されるが終了後削除されない


## マルチデータタイル(MultiDataTile)

マルチデータタイルは、一度に複数のデータセットを追加するモードです。このモードは、ブラウザのRDEデータ受け入れ画面より登録します。下記の例の場合、`.rdeconfig.yml`をデータセットテンプレートに格納し、`extended_mode: 'MultiDataTile'`を追加すると、登録したデータ数ごとに、データセットタイルが作成されます。`.rdeconfig.yml`がない場合、もしくは、`extended_mode`の指定がない場合、一つのデータセットタイルに登録したファイルがすべて登録されます。

![multifile_mode](../img/multifile_mode.svg)

### マルチデータタイル(MultiDataTile) 実行例

#### 投入データ

- 登録ファイル
  - tdata0000.dat
  - data0001.dat
- tasksupport
  - .rdeconfig.yml

!!! Note
    設定ファイル`.rdeconfig.yml`は、[設定ファイル - config](config.md)を参照ください。

#### 実行前ファイル構成

```shell
$ tree data
data
├── inputdata
│   ├── data0000.dat
│   └── data0001.dat
├── invoice
│   └── invoice.json
└── tasksupport
    ├── .rdeconfig.yml
    ├── invoice.schema.json
    └── metadata-def.json
```

#### 実行後ファイル構成

```shell
$ tree data
data
├── divided
│   └── 0001
│       ├── invoice
│       │   └── invoice.json
│       ├── logs
│       ├── main_image
│       ├── meta
│       ├── other_image
│       ├── raw
│       │   └── data0000.dat
│       ├── structured
│       ├── temp
│       └── thumbnail
├── inputdata
│   ├── data0000.dat
│   └── data0001.dat
├── invoice
│   └── invoice.json
├── logs
│   └── rdesys.log
├── main_image
├── meta
├── other_image
├── raw
│   └── data0001.dat
├── structured
├── tasksupport
│   ├── .rdeconfig.yml
│   ├── metadata-def.json
│   └── invoice.schema.json
├── temp
│   └── invoice_org.json
└── thumbnail
```
