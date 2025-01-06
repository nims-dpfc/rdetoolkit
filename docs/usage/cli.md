# コマンドライン機能について

## init: スタートアッププロジェクトの作成

以下のコマンドで、RDE構造化処理のスタートアッププロジェクトを作成することができます。

=== "Unix/macOS"

    ```shell
    python3 -m rdetoolkit init
    ```

=== "Windows"

    ```powershell
    py -m rdetoolkit init
    ```

以下のディレクトリとファイル群が生成されます。

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

各ファイルの説明は以下の通りです。

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

!!! Tip
    すでに存在するファイルは上書きや生成がスキップされます。

## ExcelInvoiceの生成機能について

`make_excelinvoice`で、`invoic.schema.json`からExcelinvoiceを生成可能です。利用可能なオプションは以下の通りです。

| オプション   | 説明                                                                                     | 必須 |
| ------------ | ---------------------------------------------------------------------------------------- | ---- |
| -o(--output) | 出力ファイルパス。ファイルパスの末尾は`_excel_invoice.xlsx`を付与すること。              | o    |
| -m           | モードの選択。登録モードの選択。ファイルモード`file`かフォルダモード`folder`を選択可能。 | -    |

=== "Unix/macOS"

    ```shell
    python3 -m rdetoolkit make_excelinvoice <invoice.schema.json path> -o <save file path> -m <file or folder>
    ```

=== "Windows"

    ```powershell
    py -m rdetoolkit make_excelinvoice <invoice.schema.json path> -o <save file path> -m <file or folder>
    ```

## version: バージョン確認

以下のコマンドで、rdetoolkitのバージョンを確認することができます。

=== "Unix/macOS"

    ```shell
    python3 -m rdetoolkit version
    ```

=== "Windows"

    ```powershell
    py -m rdetoolkit version
    ```
