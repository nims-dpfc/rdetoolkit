# Configration

rdetoolkitでは、起動時の挙動を設定ファイルで制御することは可能です。

!!! Reference
    API Documents

    [rdetoolkit.config.parse_config_file](rdetoolkit/config.md/#parse_config_file)

## 設定ファイル

設定ファイルは、`tasksupport`もしくは、プロジェクト直下に格納された、以下のファイル名を読み込みます。

### サポートする設定ファイル名

- rdeconfig.yaml
- rdeconfig.yaml
- rdeconfig.yml
- rdeconfig.yaml
- pyproject.toml

## 設定可能なオプション

### Extendeds Mode

rdetoolkitでは、4つの起動モードをサポートしています。

- invoiceモード
- ExcelInvoiceモード
- マルチデータタイル
- RDEフォーマットモード

!!! Reference
    参考: [Run Mode](mode.md)

このうち、マルチデータタイルとRDEフォーマットモードは拡張モード(`extended_mode`)であるため、上記2つのモードを利用する場合、`mode_type`の指定が必要です。`mode_type`を指定しない場合、デフォルトでinvoiceモードとなります。

=== "マルチデータタイル"

    ```yaml
    extended_mode: 'MultiDataTile'
    ```

=== "RDEフォーマットモード"

    ```yaml
    extended_mode: 'rdeformat'
    ```

#### 起動条件

| モード名              | 起動条件                                             |
| --------------------- | ---------------------------------------------------- |
| invoiceモード         | デフォルトで起動                                     |
| Excelinvoiceモード    | 入力ファイルに`*._excel_invoice.xlsx`を格納          |
| マルチデータタイル    | 設定ファイルに`extended_mode: 'MultiDataTile'`を追加 |
| RDEフォーマットモード | 設定ファイルに`extended_mode: 'rdeformat'`を追加     |

### 入力ファイルの自動保存

入力ファイルの自動保存は、`true`にすると、登録したファイルを自動的に、`raw`フォルダへ格納します。`false`にすると、登録したデータの操作はされないため、ユーザー自身でファイル操作する必要があります。

=== "入力データの自動保存の有効化"

    ```yaml
    save_raw: true
    ```

=== "入力データの自動保存の無効化"

    ```yaml
    save_raw: false
    ```

### magic variable

このモードは、デフォルトの入力モード`invoiceモード`のみで実行される処理になります。下記のように、データ登録時に`${filename}`という名称でデータ名を登録すると、自動的にファイル名をデータ名に転記するモードです。
以下の例では、データ名に、「`${filename}`」を入力し、ファイルxrd_CI0034.rasxを登録すると、データ名が、xrd_CI0034.rasxに置換されます。

![magic_filename](../img/magic_filename.svg)

=== "magic variableの有効化"

    ```yaml
    magic_variable: true
    ```

=== "magic variableの無効化"

    ```yaml
    magic_variable: false
    ```

### サムネイル画像の自動保存

サムネイルに使用する画像を自動的保存する機能です。このモードを有効化すると、Main画像(main_image)フォルダの画像を、データセットタイルのサムネイルフォルダへ設定できます。

=== "サムネイル画像の自動保存の有効化"

    ```yaml
    save_thumbnail_image: ture
    ```

=== "サムネイル画像の自動保存の無効化"

    ```yaml
    save_thumbnail_image: false
    ```

## 設定ファイルの設定例

=== "rdeconfig.yml"

    ```yaml
    extended_mode: 'MultiDataTile'
    save_raw: true
    magic_variable: false
    save_thumbnail_image: true
    ```

=== "pyproject.toml"

    ```toml
    [tool.rdetoolkit]
    extended_mode = 'MultiDataTile'
    save_raw = true
    magic_variable = false
    save_thumbnail_image = true
    ```
