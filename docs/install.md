# インストール方法

## PyPIリポジトリからインストール

rdetoolkitのインストール方法は以下の通りです。

=== "Unix/macOS"

    ```shell
    python3 -m pip install rdetoolkit
    python3 -m pip install rdetoolkit==<指定バージョン>
    ```

=== "Windows"

    ```powershell
    py -m pip install rdetoolkit
    py -m pip install rdetoolkit==<指定バージョン>
    ```

### Githubリポジトリからインストール

Githubリポジトリから直接インストールしたい場合や、開発版のパッケージをインストールする場合、リポジトリから直接インストールしてください。

=== "Unix/macOS"

    ```shell
    python3 -m pip install rdetoolkit@git+https://github.com/nims-dpfc/rdetoolkit.git
    ```

=== "Windows"

    ```powershell
    py -m pip install "rdetoolkit@git+https://github.com/nims-dpfc/rdetoolkit.git"
    ```

### 依存関係

本パッケージは、以下のライブラリ群に依存しています。

```text
chardet>=5.2.0
charset-normalizer>=3.2.0
matplotlib>=3.7.2
openpyxl>=3.1.2
pandas>=2.0.3
build>=1.0.3
click>=8.1.7
toml>=0.10.2
pydantic>=2.6.3
jsonschema>=4.21.1
tomlkit>=0.12.4
PyYAML>=6.0.1
eval_type_backport>=0.2.0
```
