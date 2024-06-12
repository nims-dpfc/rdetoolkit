# 構造化処理のエラーハンドリング

## RDEのエラーコードとメッセージ

RDEのエラーコードとメッセージは、`job.failed`というテキストファイルへ出力することで終了コード0以外をリターンすることで、構造化処理の異常終了をRDEアプリケーションから確認可能です。

フォーマット

```plaintext
ErrorCode=<エラーコード・番号>
ErrorMessage=<エラーメッセージ>
```

`jobs.faild`の記述例

```plaintext
ErrorCode=1
ErrorMessage=ERROR: failed in data processing
```

![error](../img/error.svg)

## RDEToolKitを使ってエラーハンドリングを実装する

RDEToolKitでは、[`rdetoolkit.workflows.run()`](rdetoolkit/workflows.md/#run)を利用することで、内部で発生した例外[`rdetoolkit.exceptions.StructuredError`](rdetoolkit/exceptions.md/#StructuredError)をキャッチすることが可能です。例えば、下記の例では、存在しないファイル読み込んだときのエラーを、job.failedに記述する例です。

```python
# main.py
import json

import rdetoolkit
from rdetoolkit.exceptions import StructuredError


def read_experiment_data(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return json.load(f)


def dataset(srcpaths, resource_paths):
    try:
        config = read_experiment_data("not_found_file_path.txt")
    except FileNotFoundError as e:
        # Add the error message and the error code
        raise StructuredError("Config file not found", ecode=3, eobj=e) from e

    # Do something with the dataset
    pass


if __name__ == "__main__":
    rdetoolkit.workflows.run(custom_dataset_function=dataset)
```

出力結果

```plaintext
ErrorCode=3
ErrorMessage=Config file not found
```
