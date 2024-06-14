# バリデーション機能

## バリデーションについて

RDEToolKitには、特定のファイルをバリデーションする機能を実装しています。ローカル環境で開発する場合、invoice.jsonやinvocie.schema.jsonなどのテンプレートファイルを、事前に作成する必要があります。そのため、ローカル環境で開発したファイルが正しくRDEに登録されるために、事前にローカル環境でチェックすることが可能です。

## バリデーションの対象ファイル

RDEToolKitでバリデーションの対象となるファイルは、以下の4つのファイルになります。これらのファイルをチェックする理由は、構造化処理内で下記ファイルの内容を変更できてしまうためです。構造化処理構築の際、バリデーションエラーが発生した場合、下記の情報を参考にファイルを修正してください。

- invoice.schema.json
- invoice.json
- metadata-def.json
- metadata.json

!!! Tip
    - [テンプレートファイルについて](metadata_definition_file.md)

## invoice.schema.jsonのバリデーション

`invoice.schema.json`をバリデーションする方法です。invoie.schema.jsonは、RDEの画面を構成するスキーマファイルですが、構造化処理中で変更、ローカルで定義ファイルを作成する点から、必要なフィールドが定義されているか確認するためのチェック機能を実行します。以下のバリデーション機能は、`rdetoolkit.workflows.run()`に組み込まれています。

`invoice.schema.json`の各フィールドのチェックは、[`rdetoolkit.validation.InvoiceValidator`](../../rdetoolkit/validation/#invoicevalidator)で実行します。

```python
import json
from pydantic import ValidationError

from rdetoolkit.validation import InvoiceValidator
from rdetoolkit.exceptions import InvoiceSchemaValidationError

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://rde.nims.go.jp/rde/dataset-templates/dataset_template_custom_sample/invoice.schema.json",
    "description": "RDEデータセットテンプレートサンプル固有情報invoice",
    "type": "object",
    "required": ["custom", "sample"],
    "properties": {
        "custom": {
            "type": "object",
            "label": {"ja": "固有情報", "en": "Custom Information"},
            "required": ["sample1"],
            "properties": {
                "sample1": {"label": {"ja": "サンプル１", "en": "sample1"}, "type": "string", "format": "date", "options": {"unit": "A"}},
                "sample2": {"label": {"ja": "サンプル２", "en": "sample2"}, "type": "number", "options": {"unit": "b"}},
            },
        },
        "sample": {
            "type": "object",
            "label": {"ja": "試料情報", "en": "Sample Information"},
            "properties": {
                "generalAttributes": {
                    "type": "array",
                    "items": [
                        {"type": "object", "required": ["termId"], "properties": {"termId": {"const": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e"}}}
                    ],
                },
                "specificAttributes": {"type": "array", "items": []},
            },
        },
    },
}

data = {
    "datasetId": "1s1199df4-0d1v-41b0-1dea-23bf4dh09g12",
    "basic": {
        "dateSubmitted": "",
        "dataOwnerId": "0c233ef274f28e611de4074638b4dc43e737ab993132343532343430",
        "dataName": "test-dataset",
        "instrumentId": None,
        "experimentId": None,
        "description": None,
    },
    "custom": {"sample1": "2023-01-01", "sample2": 1.0},
    "sample": {
        "sampleId": "",
        "names": ["test"],
        "composition": None,
        "referenceUrl": None,
        "description": None,
        "generalAttributes": [{"termId": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e", "value": None}],
        "specificAttributes": [],
        "ownerId": "de17c7b3f0ff5126831c2d519f481055ba466ddb6238666132316439",
    },
}

with open("temp/invoice.schema.json", "w") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

validator = InvoiceValidator("temp/invoice.schema.json")
try:
    validator.validate(obj=data)
except ValidationError as validation_error:
    raise InvoiceSchemaValidationError from validation_error
```

### invoice.schema.jsonのバリデーションエラー

`invoice.schema.json`のバリデーションエラーが発生した場合、`pydantic_core._pydantic_core.ValidationError`が発生します。

!!! Reference
    - [pydantic_core._pydantic_core.ValidationError - Pydantic](https://docs.pydantic.dev/latest/errors/validation_errors/)

invoice.schema.jsonのバリデーションエラーは、`invoice.schema.json`の属性が不正、欠損が生じた場合に発生します。そのため、再度定義を確認してください。`invoice.schema.json`の定義については、[invoice.schema.jsonについて - テンプレートファイル](metadata_definition_file.md)を参照ください。

```shell
pydantic_core._pydantic_core.ValidationError: 1 validation error for InvoiceSchemaJson
  Value error, sample is required but is None [type=value_error, input_value={'$schema': 'https://json...array', 'items': []}}}}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.7/v/value_error
```

この例では、`Value error, sample is required but is None`と書かれている通り、`required`に、`sample`が含まれていないことを指しています。

```python
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://rde.nims.go.jp/rde/dataset-templates/dataset_template_custom_sample/invoice.schema.json",
    "description": "RDEデータセットテンプレートサンプル固有情報invoice",
    "type": "object",
    "required": ["custom"], # sampleが定義されているにもかかわらず"required"に含まれていない
    "properties": {
        "custom": {
            ...
            },
        "sample": {
            ...
        }
    },
}
```

!!! Tip
    詳しい修正方法は、[invoice.schema.json - テンプレートファイルについて](metadata_definition_file.md/#invoiceschemajson_2) を参照ください。

## invoice.jsonのバリデーション

invoice.schema.jsonのバリデーションは、必要なフィールドが定義されているかチェックします。invoice.jsonのバリデーションには、`invoice.schema.json`が必要になります。

```python
import json
from pydantic import ValidationError

from rdetoolkit.validation import InvoiceValidator
from rdetoolkit.exceptions import InvoiceSchemaValidationError

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://rde.nims.go.jp/rde/dataset-templates/dataset_template_custom_sample/invoice.schema.json",
    "description": "RDEデータセットテンプレートサンプル固有情報invoice",
    "type": "object",
    "required": ["custom", "sample"],
    "properties": {
        "custom": {
            "type": "object",
            "label": {"ja": "固有情報", "en": "Custom Information"},
            "required": ["sample1"],
            "properties": {
                "sample1": {"label": {"ja": "サンプル１", "en": "sample1"}, "type": "string", "format": "date", "options": {"unit": "A"}},
                "sample2": {"label": {"ja": "サンプル２", "en": "sample2"}, "type": "number", "options": {"unit": "b"}},
            },
        },
        "sample": {
            "type": "object",
            "label": {"ja": "試料情報", "en": "Sample Information"},
            "properties": {
                "generalAttributes": {
                    "type": "array",
                    "items": [
                        {"type": "object", "required": ["termId"], "properties": {"termId": {"const": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e"}}}
                    ],
                },
                "specificAttributes": {"type": "array", "items": []},
            },
        },
    },
}

data = {
    "datasetId": "1s1199df4-0d1v-41b0-1dea-23bf4dh09g12",
    "basic": {
        "dateSubmitted": "",
        "dataOwnerId": "0c233ef274f28e611de4074638b4dc43e737ab993132343532343430",
        "dataName": "test-dataset",
        "instrumentId": None,
        "experimentId": None,
        "description": None,
    },
    "custom": {"sample1": "2023-01-01", "sample2": 1.0},
    "sample": {
        "sampleId": "",
        "names": ["test"],
        "composition": None,
        "referenceUrl": None,
        "description": None,
        "generalAttributes": [{"termId": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e", "value": None}],
        "specificAttributes": [],
        "ownerId": "de17c7b3f0ff5126831c2d519f481055ba466ddb6238666132316439",
    },
}

with open("temp/invoice.schema.json", "w") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

validator = InvoiceValidator("temp/invoice.schema.json")
try:
    validator.validate(obj=data)
except ValidationError as validation_error:
    print(validation_error)
```

### 試料情報の定義とバリデーションについて

ローカル環境で構造化処理を開発する場合、invoice.json(送り状)を事前に用意しなければなりません。送り状に試料情報を定義する場合、以下の2つの定義が想定されます。

1. 試料情報を新規に追加する場合
1. 既存の試料情報を参照する場合

上記の2つのケースでは必須項目が異なるため、ローカル環境で作成したファイルを使ってデバッグする際は注意が必要です。上記のどちらかの必須項目を満たせていない場合、バリデーションエラーが発生します。

#### 試料情報を新規に追加する場合

この場合、`sample`フィールドの`sampleId`、`names`、`ownerId`が必須になります。

```json
"sample": {
        "sampleId": "de1132316439",
        "names": ["test"],
        "composition": null,
        "referenceUrl": null,
        "description": null,
        "generalAttributes": [{"termId": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e", "value": null}],
        "specificAttributes": [],
        "ownerId": "de17c7b3f0ff5126831c2d519f481055ba466ddb6238666132316439",
    },
```

### 既存の試料情報を参照する場合

この場合、`sample`フィールドの`sampleId`が必須になります。

```json
"sample": {
        "sampleId": "de1132316439",
        "names": [],
        "composition": null,
        "referenceUrl": null,
        "description": null,
        "generalAttributes": [{"termId": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e", "value": null}],
        "specificAttributes": [],
        "ownerId": "de17c7b3f0ff5126831c2d519f481055ba466ddb6238666132316439",
    },
```

### 試料情報に関するバリデーションエラー

上記の2つのケースどちらかを満たしていなければ、バリデーションエラーが発生します。

```shell
jsonschema.exceptions.ValidationError: {'names': [], 'generalAttributes': [{'termId': '3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e'}], 'specificAttributes': [], 'ownerId': 'de17c7b3f0ff5126831c2d519f481055ba466ddb6238666132316439'} is not valid under any of the given schemas

Failed validating 'anyOf' in schema['properties']['sample']:
    {'anyOf': [{'$ref': '#/definitions/sample/sampleWhenAdding'},
               {'$ref': '#/definitions/sample/sampleWhenRef'}]}

On instance['sample']:
    {'generalAttributes': [{'termId': '3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e'}],
     'names': [],
     'ownerId': 'de17c7b3f0ff5126831c2d519f481055ba466ddb6238666132316439',
     'specificAttributes': []}

During handling of the above exception, another exception occurred:
```

### その他invoice.jsonのバリデーションエラー

`invoice.json`の`basic`項目に過不足や値が不正な場合、`jsonschema`のバリデーションエラーが発生します。

```python
data = {
    "datasetId": "1s1199df4-0d1v-41b0-1dea-23bf4dh09g12",
    "basic": {
        "dateSubmitted": "",
        "dataOwnerId": "0c233ef274f28e611de4074638b4dc43e737ab9931323435323434",
        "dataName": "test-dataset",
        "instrumentId": None,
        "experimentId": None,
        "description": None,
    },
    "custom": {"sample1": "2023-01-01", "sample2": 1.0},
}
```

以下のようなエラーメッセージが出力されます。

```shell
jsonschema.exceptions.ValidationError: '0c233ef274f28e611de4074638b4dc43e737ab9931323435323434' does not match '^([0-9a-zA-Z]{56})$'

Failed validating 'pattern' in schema['properties']['basic']['properties']['dataOwnerId']:
    {'pattern': '^([0-9a-zA-Z]{56})$', 'type': 'string'}

On instance['basic']['dataOwnerId']:
    '0c233ef274f28e611de4074638b4dc43e737ab9931323435323434
```

!!! Tip
    詳しい修正方法は、[invoice.json - テンプレートファイルについて](metadata_definition_file.md/#invoice.json_2) を参照ください。

## metadata.jsonのバリデーション

データ構造化が出力するメタデータの名前やデータ型を宣言するファイル。送り状等に入力されるメタデータは、`metadata-def.json`に定義する必要はありません。

```python
import json

from rdetoolkit.exceptions import MetadataValidationError
from rdetoolkit.validation import metadata_validate

metadata = {
    "constant": {"meta1": {"value": "sample_meta"}, "meta2": {"value": 1000, "unit": "mV"}},
    "variable": [
        {"meta3": {"value": 100, "unit": "V"}, "meta4": {"value": 200, "unit": "V"}},
        {"meta3": {"value": 300, "unit": "V"}, "meta4": {"value": 400, "unit": "V"}},
    ],
}

with open("temp/metadata.json", "w") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

try:
    metadata_validate("temp/metadata.json")
except ValidationError as validation_error:
    raise MetadataValidationError from validation_error
```

### metadata.jsonのバリデーションエラー

`metadata.json`に、`constant`, `variable`が正しく定義されていない場合、エラーが発生します。

```python
metadata = {
    "constant": {"value": "sample_meta"},
    "variable": [
        {"meta3": {"value": 100, "unit": "V"}, "meta4": {"value": 200, "unit": "V"}},
        {"meta3": {"value": 300, "unit": "V"}, "meta4": {"value": 400, "unit": "V"}},
    ],
}
```

以下のようなエラーメッセージが出力されます。

```shell
rdetoolkit.exceptions.MetadataValidationError: Error in validating metadata.json: 1 validation error for MetadataItem
constant.value
  Input should be a valid dictionary or instance of MetaValue [type=model_type, input_value='sample_meta', input_type=str]
    For further information visit https://errors.pydantic.dev/2.7/v/model_type
```

!!! Tip
    詳しい修正方法は、[metadata.json - テンプレートファイルについて](metadata_definition_file.md/#metadatajson_1) を参照ください。
