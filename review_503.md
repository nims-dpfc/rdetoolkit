## Verdict

Request changes. 実装の方向性は概ね一貫していますが、公開 API 互換性・バージョン整合性・型スタブ不一致・フルテスト失敗があり、このままのマージは避けるべきです。

## Strongest case against merging

- `smarttable_rowfile` の非推奨 alias は属性アクセスだけで、`RdeOutputResourcePath(..., smarttable_rowfile=...)` の既存コンストラクタ呼び出しが壊れます。
- Breaking change として文書化されている一方、package metadata は `1.6.5` のままで、リリース方針と整合していません。
- `SmartTableChecker.__init__` の runtime default と `.pyi` stub が不一致です。
- フル `uv run pytest` が失敗しています。

## Critical issues

### 1. Deprecated constructor keyword is broken

- **Severity:** High
- **Category:** Correctness / Type / Maintainability
- **Problem:** `src/rdetoolkit/models/rde2types.py:1015` で dataclass field が `smarttable_rawfile` に変更され、`smarttable_rowfile` property alias はあるものの、既存の `RdeOutputResourcePath(..., smarttable_rowfile=...)` は `TypeError` になります。
- **Why it matters:** 公開 API の互換性が破壊されます。
- **Suggested fix:** custom `__init__` / `InitVar` で旧 keyword を受ける、または field は旧名のまま新名を alias にする。回帰テストも追加してください。

### 2. Breaking change と version metadata が不整合

- **Severity:** High
- **Category:** Design / Maintainability
- **Problem:** `CHANGELOG.md` と `docs/releases/index.en.md` は breaking changes / v1.7.0 を示していますが、`pyproject.toml` と `src/rdetoolkit/__init__.py` は `1.6.5` のままです。
- **Why it matters:** patch release として公開されると、利用者は互換性が維持されると期待します。SmartTable callback/API の破壊的変更が patch version に紛れ込むと、既存 workflow を予期せず壊します。
- **Suggested fix:** `1.6.x` として出すなら後方互換にする。破壊的変更なら version/docs/release plan を揃えてください。

### 3. Runtime と stub の default が不一致

- **Severity:** Medium
- **Category:** Type
- **Problem:** `src/rdetoolkit/impl/input_controller.py:406` は `save_table_file=False`、`src/rdetoolkit/impl/input_controller.pyi:39` は `True`。
- **Why it matters:** 型付き package として IDE・type checker・利用者向け補完が誤った default を提示します。
- **Suggested fix:** `.pyi` を `False` に合わせる。

### 4. Full test suite is red

- **Severity:** Medium
- **Category:** Correctness / Testability
- **Problem:** `uv run pytest -q -x --tb=short` が `tests/property/test_smarttable_invoice_initializer_issue_429.py:228` で失敗しています。
- **Why it matters:** CI が red の状態では、今回の変更が既存仕様を壊していないと判断できません。
- **Suggested fix:** CR-only SmartTable numeric input を missing と扱うのか invalid と扱うのか仕様を決め、実装または property strategy を修正してください。

## Hidden assumptions and edge cases

- `generate_folder_paths_iterator(..., smarttable_mode=True)` が常に新しい `(row_csv, user_files)` 形状を受ける前提になっています。
- `smarttable_rowfile` alias は属性アクセスのみで、constructor kwargs や serialized dict 互換はありません。
- SmartTable pipeline の順序に依存しており、順序変更時に `smarttable_rawfile=None` が壊れやすいです。
- legacy SmartTable rawfile tuple を受けた場合、明示的に失敗せず `rawfiles` が壊れた形で伝播する可能性があります。

## Testability review

追加すべきテスト:

- `RdeOutputResourcePath(..., smarttable_rowfile=Path(...))` の後方互換テスト
- `SmartTableChecker` の runtime/stub default 整合確認
- `generate_folder_paths_iterator(..., smarttable_mode=True)` に malformed / legacy-shaped input が来た場合の明示的なエラー挙動
- CR-only SmartTable numeric input の仕様に対応した property test または regression test

## Type and interface review

`SmartTableRawFiles` が tuple shape と bool flag + `cast()` に依存しており、誤用しやすいです。`NamedTuple` または dataclass で `row_csv` / `user_files` を明示した方が安全です。

例:

```python
@dataclass(frozen=True)
class SmartTableRawFile:
    row_csv: Path
    user_files: tuple[Path, ...]
```

この形にすると、tuple index の意味を呼び出し側が暗黙に知る必要がなくなり、型 checker も意図を検出しやすくなります。

## Security review

変更差分内で具体的な新規 security issue は見つかりませんでした。脅威モデルとしては、file copying が user-provided path を扱うため path traversal や意図しないコピー先が懸念になり得ますが、今回の差分では controlled input checker flow から得た path を扱っており、明確な新規リスクとしては確認できません。

## Performance review

明確な performance regression は見つかりません。生成 row CSV を raw/nonshared copy から除外する方向は I/O 削減として妥当です。

ただし、SmartTable rawfile の形状判定が曖昧なままだと、将来的に defensive validation や再処理が増えて複雑化する可能性があります。現時点では premature optimization より interface 明確化を優先すべきです。

## Maintainability review

SmartTable の path model、workflow classification、file copy、parsing、docs、tests にまたがる変更で影響範囲が広いです。公開 API 互換性と release boundary を機械的に保証しないと将来の保守コストが高くなります。

特に、deprecated alias を入れるなら「どの public surface で互換性を維持するか」を明確にする必要があります。属性アクセスだけを alias にする実装は、利用者にとっては互換性があるように見えて constructor で壊れるため、保守上の罠になります。

## Suggested improvements

1. `smarttable_rowfile` constructor 互換を維持する、または明示的な breaking release に揃える。
2. version metadata / changelog / release docs を整合させる。
3. `input_controller.pyi` の default を修正する。
4. フル `uv run pytest` を通す。
5. SmartTable rawfile tuple を named structure に置き換える。
6. malformed SmartTable rawfile input を明示的な exception にする。

## Final recommendation

最低限、公開 API 互換性または versioning 方針、stub mismatch、フルテスト失敗を解消するまでマージ不可です。
