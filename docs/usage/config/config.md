# RDEToolKit設定ファイル

rdetoolkitでは、起動時の挙動を設定ファイルで制御することは可能です。

!!! Reference
    API Documents: [rdetoolkit.config.parse_config_file](/rdetoolkit/config/#parse_config_file)

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

!!! Tip "Documents"
    参考: [データ登録モードについて](mode.md)

このうち、マルチデータタイルとRDEフォーマットモードは拡張モード(`extended_mode`)であるため、上記2つのモードを利用する場合、`mode_type`の指定が必要です。`mode_type`を指定しない場合、デフォルトでinvoiceモードとなります。

=== "マルチデータタイル"

    ```yaml
    system:
        extended_mode: 'MultiDataTile'
    ```

=== "RDEフォーマットモード"

    ```yaml
    system:
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

入力ファイルの自動保存を有効化すると、自動的に`raw`ディレクトリもしくは、`nonshared_raw`ディレクトリに入力ファイルを保存します。保存先は、RDEデータセット公開と共にデータが共有される`raw`, RDEデータセットが公開されても入力ファイルが共有されない`nonshared_raw`があり、利用状況に応じて設定ファイルより設定してください。

| 設定値             | 値               | 説明                                                      |
| ------------------ | ---------------- | --------------------------------------------------------- |
| save_raw           | `true` / `false` | `raw`ディレクトリに保存する。デフォルトは`false`          |
| save_nonshared_raw | `true` / `false` | `nonshared_raw`ディレクトリに保存する。デフォルトは`true` |

=== "入力データの自動保存の有効化(raw)"

    ```yaml
    system:
        save_raw: true
    ```

=== "入力データの自動保存の無効化(raw)"

    ```yaml
    system:
        save_raw: false
    ```

=== "入力データの自動保存の有効化(nonshared_raw)"

    ```yaml
    system:
        save_nonshared_raw: true
    ```

=== "入力データの自動保存の無効化(nonshared_raw)"

    ```yaml
    system:
        save_nonshared_raw: false
    ```

### magic variable

このモードは、デフォルトの入力モード`invoiceモード`のみで実行される処理になります。下記のように、データ登録時に`${filename}`という名称でデータ名を登録すると、自動的にファイル名をデータ名に転記するモードです。
以下の例では、データ名に、「`${filename}`」を入力し、ファイルxrd_CI0034.rasxを登録すると、データ名が、xrd_CI0034.rasxに置換されます。

![magic_filename](../../img/magic_filename.svg)

=== "magic variableの有効化"

    ```yaml
    system:
        magic_variable: true
    ```

=== "magic variableの無効化"

    ```yaml
    system:
        magic_variable: false
    ```

### サムネイル画像の自動保存

サムネイルに使用する画像を自動的保存する機能です。このモードを有効化すると、Main画像(main_image)フォルダの画像を、データセットタイルのサムネイルフォルダへ設定できます。

=== "サムネイル画像の自動保存の有効化"

    ```yaml
    system:
        save_thumbnail_image: ture
    ```

=== "サムネイル画像の自動保存の無効化"

    ```yaml
    system:
        save_thumbnail_image: false
    ```

### 独自の設定値を設定する

`rdeconfig.yaml`等の設定ファイルは、ユーザー独自の設定値を記述することができます。例えば、サムネイルの画像にどのファイルにするか指定する場合、`thumbnail_image_name`という設定値を以下のように記述します。

=== "yml・yaml"

    ```yaml
    custom:
        thumbnail_image_name: "inputdata/sample_image.png"
    ```

=== "pyproject.toml"

    ```toml
    [tool.rdetoolkit.custom]
     thumbnail_image_name: "inputdata/sample_image.png"
    ```

> 設定値の書き方については、YAMLフォーマットに従って記述してください。: [YAML Ain’t Markup Language (YAML™) version 1.2](https://yaml.org/spec/1.2.2/)

### MultiDataTileモードでエラーによるプログラム終了をスキップする

`MultiDataTile`は、一度に複数のデータを登録できますが、途中でエラーが発生すると、処理が停止し、最後まで構造化処理が実行されません。このとき、入力したファイルに対して処理を最後まで実行したい場合、`multidata_tile`というセクションの`ignore_errors`を有効化してください。デフォルトは、`false`となっており、エラーが発生すると処理が終了します。

=== "エラー処理スキップ機能を有効化"

    ```yaml
    multidata_tile:
        ignore_errors: true
    ```

=== "エラー処理スキップ機能を無効化"

    ```yaml
    multidata_tile:
        ignore_errors: false
    ```

> 設定値の書き方については、YAMLフォーマットに従って記述してください。: [YAML Ain’t Markup Language (YAML™) version 1.2](https://yaml.org/spec/1.2.2/)

## 設定ファイルの設定例

=== "rdeconfig.yml"

    ```yaml
    system:
        extended_mode: 'MultiDataTile'
        save_raw: false
        save_nonshared_raw: true
        magic_variable: false
        save_thumbnail_image: true
    ```

=== "pyproject.toml"

    ```toml
    [tool.rdetoolkit.system]
    extended_mode = 'MultiDataTile'
    save_raw = true
    save_nonshared_raw=true
    magic_variable = false
    save_thumbnail_image = true
    ```

### 構造化処理から設定値を参照する

構造化処理内で、`tasksupport`に格納した設定値を参照する方法は、`rdetoolkit.models.rde2types.RdeInputDirPaths.config`で設定値を参照できます。

    ```python
    def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
        # この関数内でユーザ自身が定義したクラスや関数を記述する
        ... #任意の処理

        # Extendeds Modeの設定値を取得する
        print(srcpaths.config.system.extended_mode)

        # 入力ファイルの自動保存の設定値を取得する
        print(srcpaths.config.system.save_raw)

        # サムネイル画像の自動保存の設定値を参照する
        print(srcpaths.config.system.save_thumbnail_image)

        # magic variableの設定値を参照する
        print(srcpaths.config.system.magic_variable)

        # 独自の設定値を参照する
        print(srcpaths.config.custom.thumbnail_image_name)
    ```
