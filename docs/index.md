# RDEToolKit

![GitHub Release](https://img.shields.io/github/v/release/nims-dpfc/rdetoolkit)
[![python.org](https://img.shields.io/badge/Python-3.9%7C3.10%7C3.11-%233776AB?logo=python)](https://www.python.org/downloads/release/python-3917/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/nims-dpfc/rdetoolkit/blob/main/LICENSE)
[![Issue](https://img.shields.io/badge/issue_tracking-github-orange)](https://github.com/nims-dpfc/rdetoolkit/issues)
![workflow](https://github.com/nims-dpfc/rdetoolkit/actions/workflows/main.yml/badge.svg)
![coverage](img/coverage.svg)

RDEToolKitは、RDE構造化プログラムのワークフローを作成するための基本的なPythonパッケージです。
RDEToolKitの各種モジュールを使うことで、RDEへの研究・実験データの登録処理を簡単に構築できます。
また、ユーザーが研究や実験データに対して使用されているPythonモジュールと組み合わせることで、データの登録から加工、グラフ化などより多様な処理を実現できます。

RDEToolKitは、ユーザーが定義した構造化処理の前処理・後処理をサポートします。

```mermaid
graph LR
    前処理 --|rdetoolkit|--> カスタム構造化処理
    カスタム構造化処理 --|rdetoolkit|--> 後処理
```

## 主な機能

- **データ登録**: 研究・実験データをRDEに簡単に登録できます。
- **データ加工**: データの前処理や変換を行うためのツールを提供します。
- **グラフ化**: データの可視化をサポートし、グラフやチャートを作成できます。
- **ワークフロー管理**: データ処理のワークフローを簡単に管理できます。

## インストール

RDEToolKitはPythonパッケージとして提供されており、以下のコマンドでインストールできます。

```bash
pip install rdetoolkit
```

## Usage

[クイックスタート](usage/quickstart.md) を参照してください。

## API Documentation

[API Documentation](rdetoolkit/impl/compressed_controller) を参照してください。

## Contributing

RDEToolKitへのコントリビュートをしていただくには、以下のドキュメントを参照してください。

[Contributing](contribute/home.md)

## ライセンス

RDEToolKitはMITライセンスの下で提供されています。詳細については、[LICENSE](https://github.com/nims-dpfc/rdetoolkit/blob/main/LICENSE)ファイルを参照してください。
