# 構造化ディレクトリパスの取得

## ディレクトリとカスタム構造化処理の制約

ユーザー自身が、カスタム構造化処理を定義する際が、`RdeInputDirPaths`, `RdeOutputResourcePath`を引数で受け取れり可能な関数を定義しなければなりません。

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    # この関数内でユーザ自身が定義したクラスや関数を呼び出す
    ...
```

!!! Reference
    - API Documentation: [RdeInputDirPaths - rde2types](../../../rdetoolkit/models/rde2types/#rdeinputdirpaths)
    - API Documentation: [RdeOutputResourcePath - rde2types](../../../rdetoolkit/models/rde2types/#rdeoutputresourcepath)

`RdeInputDirPaths`は、入力で扱われるディレクトリパスやファイルパス群を格納してます。ディレクトリパスは、`pathlib.Path`オブジェクトで格納されています。

```python
@dataclass
class RdeInputDirPaths:
    inputdata: Path
    invoice: Path
    tasksupport: Path
```

関数内ディレクトリパスにアクセスする場合、以下の定義でディレクトリパスを取得できます。

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    inputdata_dir = srcpaths.inputdata
    invoice_dir = srcpaths.invoice
    tasksupport = srcpaths.tasksupport
```

`RdeOutputResourcePath`では、出力で扱われるディレクトリパス群を格納しています。

```python
@dataclass
class RdeOutputResourcePath:
    raw: Path
    rawfiles: tuple[Path, ...]
    struct: Path
    main_image: Path
    other_image: Path
    meta: Path
    thumbnail: Path
    logs: Path
    invoice: Path
    invoice_schema_json: Path
    invoice_org: Path
    temp: Path | None = None
    invoice_patch: Path | None = None
    attachment: Path | None = None
    nonshared_raw: Path | None = None
```

関数内ディレクトリパスにアクセスする場合、以下の定義でディレクトリパスを取得できます。

```python
def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath):
    rawfiles = resource_paths.rawfiles
    raw_dir = resource_paths.raw
    struct_dir = resource_paths.struct
    main_image_dir = resource_paths.main_image
```
