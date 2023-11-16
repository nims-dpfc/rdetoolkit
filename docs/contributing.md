# Contributing

> 変更を加える場合、以下のドキュメントも参考にしてください。
>
> - [RdeToolKitを変更する - RDE開発者ドキュメント](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/sample_project/-/wikis/base/RdeToolKit%E3%82%92%E5%A4%89%E6%9B%B4%E3%81%99%E3%82%8B)

このツールで、新機能・変更・不具合等が発生した場合、以下の手順で変更をしてください。

- 上記リポジトリのissueで、Issueを作成し新機能、問題や不具合を報告する
- 変更を実際に加える場合、ローカルで新規にブランチを作成し、変更を加える。
- CIテストを実行し、マージリクエストを出す
- CIテストが全てパス、レビューが完了したら、マージする
- Releaseページを作成する

この手順書を参考にして、RdeToolKitの開発・変更を行ってください。共同開発を円滑に進めるためのガイドラインとして利用してください。

## Issueを作成する

問題や不具合が発生した場合、以下のisuueへ起票お願いします。

> <https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/boards>

## 新機能・修正を加える

### 必要なツール

- `Python` (推奨バージョン: 3.9以上)
- [rye](https://rye-up.com/) or [Poetry](https://python-poetry.org/docs/)(プロジェクト管理ツール)
- `git` (バージョン管理)

> 以下の手順は、ryeを使った方法で説明をまとめます。

### リポジトリのクローン

リポジトリをローカルマシンにクローンします。

```bash
git clone [リポジトリのURL]
```

### ブランチの作成

新しい機能や修正を行う際は、新しいブランチを作成してください。

```bash
git checkout -b [ブランチ名]
```

### 依存ライブラリのインストール

```bash
rye sync
source .venv/bin/bash
```

### コードの変更・追加

必要に応じて、コードの修正をお願いします。

### テストの実行

変更を行った後は、テストを実行して正常に動作することを確認してください。

```bash
tox
```

### コミットとプッシュ

変更をコミットし、リモートリポジトリにプッシュします。

```bash
git add .
git commit -m "#[issue番号] [変更内容の簡単な説明]"
git push origin [ブランチ名]
```

### 変更リクエスト (Merge Request)

変更が完了したら、GitHub等のプラットフォームを使用して変更リクエスト (PR) を作成します。
この時、レビューを受け、必ずCIテストが全てパスすることを確認してください。

### マージ

レビューが完了し、問題がないと判断されたら、マスターブランチにマージします。また、デプロイが正しく実行できたら、tagの作成とReleaseページを作成してください。

> Releaseページ: <https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/releases>

## 関連ページ

- [トップページに戻る](home)
