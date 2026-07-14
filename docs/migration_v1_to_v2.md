# v1 から v2 への移行

v2 の正準入口は eager に実行される `@flow` と ProcessingTemplate です。
実行結果は `RunReport` で受け取り、`status`、タイルごとの結果、警告、エラーを
同じスキーマから確認します。このガイドでは既存のハンドラークラスを一度に
捨てず、機械変換と小さな手作業を組み合わせて移行します。

## 1. 既存コードを検査する

例として、次の v1 形式のファイルを `legacy.py` とします。

<!-- test: legacy-source -->
```python
import rdetoolkit.workflows as legacy_workflows


class TextHandler:
    def process(self, srcpaths, resource_paths):
        source = next(srcpaths.inputdata.glob("*.txt"))
        destination = resource_paths.struct / "structured.txt"
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def custom_dataset_function(srcpaths, resource_paths):
    TextHandler().process(srcpaths, resource_paths)


if __name__ == "__main__":
    legacy_workflows.run(custom_dataset_function=custom_dataset_function)
```

`migrate check` は移行点を報告する読み取り専用コマンドです。`migrate apply` は
既定で dry-run になり、変換後の `@flow` を表示します。内容を確認した後だけ
`--no-dry-run --out <別ディレクトリ>` を指定してください。入力ファイルを
直接書き換えることはありません。

<!-- test: migration-commands -->
```bash
$ python -m rdetoolkit migrate check legacy.py
$ python -m rdetoolkit migrate apply legacy.py
```

変換不能な動的ディスパッチなどは `TODO(rdetoolkit-migrate)` として残ります。
TODO がない場合でも、生成物のテストと出力ディレクトリを確認してから採用します。

## 2. ハンドラーを `as_node` でつなぐ中間形

付録 M の Protocol に適合する既存ハンドラーは、移行期間中だけ `as_node` で
メソッドを通常の node にできます。Protocol はこの移行判断の補助であり、DI や
新規設計の入口ではありません。

<!-- test: as-node-bridge -->
```python
from rdetoolkit import as_node


class LegacyReader:
    def read(self, name: str) -> str:
        return name.upper()


read_legacy = as_node(LegacyReader(), method="read", id="docs.migration.legacy_reader")
result = read_legacy("sample.txt")
assert result == "SAMPLE.TXT"
```

この段階ではクラスを残せますが、node 間の値は明示引数で渡し、`self.df` のような
隠れ状態を増やさないでください。

## 3. 最終形を選ぶ

対応するドメインテンプレートがある場合は、`templates describe <name>` で slot を
確認し、`init --processing-template <name>` が生成したクラスの TODO slot だけを
実装します。骨格、保存順序、出力規約はテンプレートが所有します。

テンプレートがない非定型処理では `@flow` を 1 関数書きます。`if`、ループ、
f-string、リテラル引数、デフォルト引数は通常の Python と同じです。処理を再利用
したくなった時点でだけ `@node` に分割します。保存処理には `rdetoolkit.nodes` の
組込ノードを使います。

## 実行時の変更点

- v2 の正準戻り値は `RunReport` です。`report.status` と
  `report.iterations` を起点に結果を処理してください。
- **`on_iteration_error` の既定値は v1 の `fail-fast` から v2 の `continue` に変わります。**
  従来と同じ即時停止が必要なら設定で `fail_fast` を明示してください。
- グラフは実行前 DAG ではなく、実行後の call sequence です。通常の Python
  制御構文をそのまま使えます。

## v1 ユーザー向け互換範囲とスケジュール

> **暫定** — v2.0 GA までのランタイム統合（`merge_v1/Plan.md`）後に確定。

確定版では、互換入口、ディレクトリと成果物の契約、設定キーの変換表、旧結果を
必要とする利用側の明示変換、移行期限をまとめます。現時点では新規コードを
`@flow` または ProcessingTemplate で作り、戻り値を `RunReport` として扱って
ください。
