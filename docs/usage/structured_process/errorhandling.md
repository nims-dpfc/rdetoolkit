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

![error](../../img/error.svg)

## RDEToolKitを使ってエラーハンドリングを実装する

RDEToolKitでは、[`rdetoolkit.workflows.run()`](/rdetoolkit/workflows/#run)を利用することで、内部で発生した例外[`rdetoolkit.exceptions.StructuredError`](/rdetoolkit/exceptions/#StructuredError)をキャッチすることが可能です。例えば、下記の例では、存在しないファイル読み込んだときのエラーを、job.failedに記述する例です。

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

`job.failed`の出力結果は以下のようになります。

```plaintext
ErrorCode=3
ErrorMessage=Config file not found
```

### スタックトレース整形する

`rdetoolkit.exceptions.catch_exception_with_message`を使用すると、構造化処理のスタックトレースを整形することが可能です。例えば、上記の`dataset`に、`catch_exception_with_message`でデコレーターとして付与します。

デコレータを使用すると、スタックトレースの整形、エラーメッセージ、エラーコードの上書き、デフォルトのスタックトレースの表示・非表示を設定できます。

- `error_message`： 上書きするエラーメッセージ
- `error_code`: 上書きするエラーコード
- `verbose`: デフォルトのスタックトレースの表示・非表示

```python
@catch_exception_with_message(error_message="Overwrite message!", error_code=100, verbose=False)
def dataset(srcpaths, resource_paths):
    try:
        config = read_experiment_data("not_found_file_path.txt")
    except FileNotFoundError as e:
        # Add the error message and the error code
        raise StructuredError("Config file not found", ecode=3, eobj=e) from e

    # Do something with the dataset
    passs
```

この時のスタックトレースは、以下の通りです。

```shell
Traceback (simplified message):
Call Path:
   File: /Users/myproject/container/modules/custom_modules.py, Line: 109 in wrapper()
    └─ File: /Users/myproject/container/main.py, Line: 27 in dataset()
        └─> L27: raise StructuredError("Config file not found", ecode=3, eobj=e) from e 🔥

Exception Type: StructuredError
Error: Config file not found
```

また、デコレーターを使用する場合の`job.failed`は、デコレータを付与する前と同様の出力となります。**これは、内部で明示的に定義した`raise <例外クラス>`の内容を捕捉し、詳細情報を`job.faild`に書き込みます。**

デコレーターを付与した関数内部で明示的に定義した例外クラスでエラーを捕捉した場合、その例外情報が優先されるため、デコレータ引数で与えたメッセージやエラーコードでは上書きされません。

このデコレータを使用すると、事前に例外処理を定義していないかつ、予期しないエラーが発生し捕捉したとき、デコレータの引数で事前に定義したエラーメッセージとエラーコードを`job.faild`に書き込むことができます。

```text
ErrorCode=3
ErrorMessage=Error: Config file not found
```

もし、デコレータを使わなず、予期しないエラーが発生した場合、`job.faild`には以下のデフォルトメッセージが書き込まれます。そのため、Web UIで確認したとき、エラーの特定が難しいです。

```text
ErrorCode=999
ErrorMessage=Error: Please check the logs and code, then try again.
```
