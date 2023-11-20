# RdeToolKit

[![Latest Release](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/badges/release.svg)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/releases)
[![pipeline status](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/badges/main/pipeline.svg)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/commits/main)
[![coverage report](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/badges/main/coverage.svg)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/commits/main)
[![python.org](https://img.shields.io/badge/Python-3.9%7C3.10%7C3.11-%233776AB?logo=python)](https://www.python.org/downloads/release/python-3917/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/blob/main/LICENSE)
[![Issue](https://img.shields.io/badge/issue_tracking-gitlab-orange)](https://gitlab.nims.go.jp/dpfc/data_registry/rde20/rdetoolkit/-/issues)


RdeToolKitは、RDE2.0構造化プログラムのワークフローを作成するための基本的なPythonパッケージです。
RdeToolKitの各種モジュールを使うことで、RDEへの研究・実験データの登録処理を簡単に構築できます。
また、ユーザーが研究や実験データに対して使用されているPythonモジュールと組み合わせることで、データの登録から加工、グラフ化などより多様な処理を実現できます。

RDE上で実行したい構造化処理関数を下記のように定義したとします。

```python
def dataset(srcpaths, resource_paths):
    read_file(srcpaths) # read input raw data
    plot(resource_paths) # plot raw data
```

この関数を、`run()`に渡すことで、簡単に構造化処理を実現できます。

```python
#importing a user-defined structured processing function
from modules import process
import rdetoolkit

#Pass your own defined structured processing functions as arguments
rdetoolkit.workflows.run(custom_dataset_function=process.dataset)
```

## Usage

[クイックスタート](usage.md)

## Contributing

本ライブラリの不具合や、開発へのご協力に関しては、以下のドキュメントを参照してください。

[Contributing](contributing.md)

