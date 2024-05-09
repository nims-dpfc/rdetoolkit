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
