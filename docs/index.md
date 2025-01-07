# RDEToolKit

![GitHub Release](https://img.shields.io/github/v/release/nims-dpfc/rdetoolkit)
[![python.org](https://img.shields.io/badge/Python-3.9%7C3.10%7C3.11-%233776AB?logo=python)](https://www.python.org/downloads/release/python-3917/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/nims-dpfc/rdetoolkit/blob/main/LICENSE)
[![Issue](https://img.shields.io/badge/issue_tracking-github-orange)](https://github.com/nims-dpfc/rdetoolkit/issues)
![workflow](https://github.com/nims-dpfc/rdetoolkit/actions/workflows/main.yml/badge.svg)
![coverage](img/coverage.svg)

RDEToolKitは、RDE構造化プログラムのワークフローを作成するための基本的なPythonパッケージです。RDEToolKitの各種モジュールを使うことで、RDEへの研究・実験データの登録処理を簡単に構築できます。主に、RDEToolKitは、ユーザーが定義した構造化処理の前処理・後処理をサポートします。また、ユーザーが研究や実験データに対して使用されているPythonモジュールと組み合わせることで、データの登録から加工、グラフ化などより多様な処理を実現可能です。これにより、データのクレンジング、変換、集計、可視化など、データサイエンスのワークフロー全体を効率的に管理できます。

<br>

![overview_workflow](img/overview_workflow.svg)

## 主な特徴

- **モジュール化**
    - RDEデータ登録に必要な前処理や後処理がモジュールとして提供されており、カスタマイズしたい処理を実装するだけで、柔軟に構造処理を実装できます。
- **柔軟なデータ処理**
    - データの前処理、変換、可視化など、さまざまなデータ処理をサポートします。
- **簡単なインストール**
    - `pip install rdetoolkit` コマンドで簡単にインストールできます。
- **拡張性**
    - ユーザーが定義したカスタムデータセット処理関数を使用して、特定のデータ処理ニーズに対応できます。これにより、特定の研究や実験の要件に合わせたデータ処理が可能です。
- **統合**
    - 他のPythonモジュールと組み合わせることで、データの登録から加工、グラフ化など、より多様な処理を実現可能です。これにより、構造化処理全体を一元管理できます。

## インストール

RDEToolKitはPythonパッケージとして提供されており、以下のコマンドでインストールできます。

```bash
pip install rdetoolkit
```

## Code Sample

|       Sample1: ユーザー定義構造化処理あり       |            Sample2: ユーザー定義構造化処理なし            |
| :---------------------------------------------: | :-------------------------------------------------------: |
| ![quick-sample-code](img/quick-sample-code.svg) | ![quick-sample-code-none](img/quick-sample-code-none.svg) |

## Next Step

<div class="grid cards" markdown>

- [:material-arrow-down-bold-circle:{ .lg .middle } __rdetoolkitをインストール__](install)
- [:material-clock-fast:{ .lg .middle } __クイックスタート__](usage/quickstart)
- [:material-code-braces:{ .lg .middle } __RDE構造化処理を開発する__](usage/structured_process/structured)
- [:material-book:{ .lg .middle } __rdetoolkit API Documents__](rdetoolkit/index.md)
- [:material-account-group:{ .lg .middle } __Contributing__](contribute/home.md)
- [:material-license:{ .lg .middle } __License__](https://github.com/nims-dpfc/rdetoolkit/blob/main/LICENSE)

</div>

## Contact

RDEToolKitの不具合やお問い合わせは、以下のIssueにご投稿ください。

[Contributing](https://github.com/nims-dpfc/rdetoolkit/issues)
