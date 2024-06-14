# テンプレートファイル

## テンプレートファイルについて

RDEではテンプレートファイルとして以下のファイルを扱います。RDE構造化処理を実行するとき、以下のファイルが必要になる時があります。

- invoice.schema.json
- invoice.json
- metadata-def.json
- metadata.json

## invoice.schema.jsonについて

送り状のスキーマを定義する。スキーマの形式はJSON Schemaの標準仕様に準拠します。この JSONスキーマは送り状の画面を生成するために使用されますが、RDEToolKitを使うことで送り状のバリデーションとして使われます。

!!! Tip
    [Creating your first schema - json-schema.org](https://json-schema.org/learn/getting-started-step-by-step)

### invoice.schema.jsonの構築例

<details>
<summary>invoice.shcema.jsonの構築例</summary>

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://rde.nims.go.jp/rde/dataset-templates/dataset_template_custom_sample/invoice.schema.json",
  "description": "RDEデータセットテンプレートサンプル固有情報invoice",
  "type": "object",
  "required": [
    "custom",
    "sample"
  ],
  "properties": {
    "custom": {
      "type": "object",
      "label": {
        "ja": "固有情報",
        "en": "Custom Information"
      },
      "required": [
        "sample1",
        "sample2"
      ],
      "properties": {
        "sample1": {
          "label": {
            "ja": "サンプル１",
            "en": "sample1"
          },
          "type": "string",
          "format": "date",
          "options": {
            "unit": "A"
          }
        },
        "sample2": {
          "label": {
            "ja": "サンプル２",
            "en": "sample2"
          },
          "type": "number",
          "options": {
            "unit": "b"
          }
        },
        "sample3": {
          "label": {
            "ja": "サンプル３",
            "en": "sample3"
          },
          "type": "integer",
          "options": {
            "unit": "c",
            "placeholder": {
              "ja": "Please Enter text",
              "en": "Please Enter text"
            }
          }
        },
      }
    },
    "sample": {
      "type": "object",
      "label": {
        "ja": "試料情報",
        "en": "Sample Information"
      },
      "properties": {
        "generalAttributes": {
          "type": "array",
          "items": [
            {
              "type": "object",
              "required": [
                "termId"
              ],
              "properties": {
                "termId": {
                  "const": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "termId"
              ],
              "properties": {
                "termId": {
                  "const": "e2d20d02-2e38-2cd3-b1b3-66fdb8a11057"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "termId"
              ],
              "properties": {
                "termId": {
                  "const": "efcf34e7-4308-c195-6691-6f4d28ffc9bb"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "termId"
              ],
              "properties": {
                "termId": {
                  "const": "1e70d11d-cbdd-bfd1-9301-9612c29b4060"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "termId"
              ],
              "properties": {
                "termId": {
                  "const": "5e166ac4-bfcd-457a-84bc-8626abe9188f"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "termId"
              ],
              "properties": {
                "termId": {
                  "const": "0d0417a3-3c3b-496a-b0fb-5a26f8a74166"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "termId"
              ],
              "properties": {
                "termId": {
                  "const": "efc6a0d5-313e-1871-190c-baaff7d1bf6c"
                }
              }
            }
          ]
        },
        "specificAttributes": {
          "type": "array",
          "items": [
            {
              "type": "object",
              "required": [
                "classId",
                "termId"
              ],
              "properties": {
                "classId": {
                  "const": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b"
                },
                "termId": {
                  "const": "3250c45d-0ed6-1438-43b5-eb679918604a"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "classId",
                "termId"
              ],
              "properties": {
                "classId": {
                  "const": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b"
                },
                "termId": {
                  "const": "70c2c751-5404-19b7-4a5e-981e6cebbb15"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "classId",
                "termId"
              ],
              "properties": {
                "classId": {
                  "const": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b"
                },
                "termId": {
                  "const": "e2d20d02-2e38-2cd3-b1b3-66fdb8a11057"
                }
              }
            },
            {
              "type": "object",
              "required": [
                "classId",
                "termId"
              ],
              "properties": {
                "classId": {
                  "const": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b"
                },
                "termId": {
                  "const": "518e26a0-4262-86f5-3598-80e18e6ff2af"
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

</details>

### invoice.schema.jsonの定義

| 項目名   (JSONポインタ)                                                                                      | 型               | フォーマット | 必須 | 固定値                                         | 説明                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------ | ---------------- | ------------ | ---- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| (ドキュメントルート)                                                                                         | object           | -            | ○    | -                                              | JSONドキュメントのルート。                                                                                                                                         |
| /$schema                                                                                                     | string           | uri          | ○    | `https://json-schema.org/draft/2020-12/schema` | メタスキーマ(スキーマのスキーマ)のID。                                                                                                                             |
| /$id                                                                                                         | string           | uri          | ○    | -                                              | このスキーマのID。ユニークであること                                                                                                                               |
| /description                                                                                                 | string           | -            | -    | -                                              | スキーマの説明                                                                                                                                                     |
| /type                                                                                                        | string           | -            | ○    | "object"                                       | 値は固定。                                                                                                                                                         |
| /required                                                                                                    | array            | -            | ○    | -                                              | 固有情報を入力させる場合は"custom"を含める。試料情報を入力させる場合は"sample"を含める。                                                                           |
| /properties                                                                                                  | object           | -            | ○    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;/custom                                                                                          | object           | -            | -    | -                                              | 送り状の固有情報を格納するオブジェクト。固有情報を入力させない場合は省く。                                                                                         |
| &ensp;&ensp;&ensp;&ensp;/type                                                                                | string           | -            | ○    | "object"                                       | 値は固定。                                                                                                                                                         |
| &ensp;&ensp;&ensp;&ensp;/label                                                                               | object           | -            | ○    | -                                              | 固有情報の見出しとして使用する文字列。言語別に指定する。                                                                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/ja                                                                      | string           | -            | ○    | -                                              | 見出しの日本語表記。                                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/en                                                                      | string           | -            | ○    | -                                              | 見出しの英語表記。                                                                                                                                                 |
| &ensp;&ensp;&ensp;&ensp;/required                                                                            | object           | -            | ○    | -                                              | 必須のキー名を指定する。複数指定可。                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;/properties                                                                          | object           | -            | ○    | -                                              | 固有情報項目のマップ。表示や入力する際の項目の順序は、このスキーマでの記述順に従う。                                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;/{最初のキーの名前}                                                            | object           | -            | -    | -                                              | 最初の項目のキー名。キーの名前はファイル全体でユニークであること。                                                                                                 |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/type                                                                    | string           | -            | ○    | -                                              | 項目の値のデータ型。"boolean", "integer", "number", "string"のいずれか1つを指定する。"boolean","integer", "number", "string"のいずれの場合もnullを許容しない。※注1 |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/description                                                             | string           | -            | -    | -                                              | 項目の説明。画面には表示しない。                                                                                                                                   |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/examples                                                                | array            | -            | -    | -                                              | 値の例。画面には表示しない。                                                                                                                                       |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/default                                                                 | 任意             | -            | -    | -                                              | 初期値を指定する。                                                                                                                                                 |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/{最初のスキーマキーワード}                                              | キーワードに依存 | -            | -    | -                                              | 項目の値に関する制約を指定するキーワード。                                                                                                                         |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/{2番目のスキーマキーワード}                                             | キーワードに依存 | -            | -    | -                                              | 同上                                                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/...                                                                     | -                | -            | -    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/label                                                                   | object           | -            | ○    | -                                              | 画面に表示する項目のラベル。言語別に指定する。                                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/ja                                                          | string           | -            | ○    | -                                              | 日本語表示時のラベル。                                                                                                                                             |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/en                                                          | string           | -            | ○    | -                                              | 英語表示時のラベル。                                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/options                                                                 | object           | -            | -    | -                                              | 項目に関するオプションの指定。                                                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/widget                                                      | string           | -            | -    | -                                              | 画面部品を明示的に指定する場合に使う。"textarea"のみ指定可。通常はtypeの値に応じた画面部品が生成される。                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/rows                                                        | integer          | -            | -    | -                                              | 画面部品がtextareaの場合の行数を指定する。                                                                                                                         |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/unit                                                        | string           | -            | -    | -                                              | 画面に表示する単位。                                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/placeholder                                                 | object           | -            | -    | -                                              | 画面部品に設定するプレイスホルダ。言語別に指定する。省略可能。                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/ja                                              | string           | -            | -    | -                                              | 日本語表示時のプレイスホルダ。                                                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/en                                              | string           | -            | -    | -                                              | 英語表示時のプレイスホルダ。                                                                                                                                       |
| &ensp;&ensp;&ensp;&ensp;&ensp;/{2番目のキーの名前}                                                           | object           | -            | -    | -                                              | 2番目の項目のキー名。                                                                                                                                              |
| &ensp;&ensp;&ensp;&ensp;&ensp;(以下繰り返し)                                                                 | -                | -            | -    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;/sample                                                                                          | object           | -            | -    | -                                              | 送り状の試料情報を格納するオブジェクト。試料情報を入力させない場合は省く。                                                                                         |
| &ensp;&ensp;&ensp;&ensp;/type                                                                                | string           | -            | ○    | "object"                                       | 値は固定。                                                                                                                                                         |
| &ensp;&ensp;&ensp;&ensp;/label                                                                               | object           | -            | ○    | -                                              | 試料情報の見出しとして使用する文字列。言語別に指定する。                                                                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/ja                                                                      | string           | -            | ○    | -                                              | 見出しの日本語表記。                                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/en                                                                      | string           | -            | ○    | -                                              | 見出しの英語表記。                                                                                                                                                 |
| &ensp;&ensp;&ensp;&ensp;/properties                                                                          | object           | -            | ○    | -                                              | 試料のプロパティ                                                                                                                                                   |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/generalAttributes                                                       | object           | -            | -    | -                                              | 一般項目。一般項目を入力しない場合は省略可。                                                                                                                       |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/type                                                  | string           | -            | ○    | "array"                                        |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/items                                                 | array            | -            | ○    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/0                                         | object           | -            | -    | -                                              | 最初の一般項目。                                                                                                                                                   |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/type                          | string           | -            | ○    | "object"                                       |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/required                      | array            | -            | ○    | ["termId"]                                     | 一般項目が持つ必須プロパティ。固定。                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/properties                    | object           | -            | ○    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/termId            | object           | -            | ○    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/const | string           | -            | ○    | -                                              | この一般項目の用語ID。                                                                                                                                             |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/1                                         | object           | -            | -    | -                                              | 2番目の一般項目。                                                                                                                                                  |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;(以下繰り返し)                             | -                | -            | -    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/specificAttributes                                                      | object           | -            | -    | -                                              | 分類別項目。分類別項目を入力しない場合は省略可。                                                                                                                   |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/type                                                  | string           | -            | ○    | "array"                                        |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/items                                                 | array            | -            | ○    | "string"                                       |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/0                                         | object           | -            | -    | -                                              | 最初の分類別項目。                                                                                                                                                 |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/type                          | string           | -            | ○    | "object"                                       |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/required                      | array            | -            | ○    | ["classId","termId"]                           | 分類別項目が持つ必須プロパティ。固定。                                                                                                                             |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/properties                    | object           | -            | ○    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/classId           | object           | -            | ○    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/const | string           | uuid         | ○    | -                                              | この分類別項目の試料分類ID。                                                                                                                                       |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/termId            | object           | -            | ○    | -                                              |                                                                                                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/const | string           | -            | ○    | -                                              | この分類別項目の用語ID。                                                                                                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/1                                         | object           | -            | -    | -                                              | 2番目の分類別項目。                                                                                                                                                |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;(以下繰り返し)                             | -                | -            | -    | -                                              |                                                                                                                                                                    |

### invoice.schema.jsonで利用可能なスキーマキーワード一覧

項目の値に関する制約として指定可能なスキーマキーワードを下表に示す。

| type                 | キーワード       | 値の型     | 説明                                                                               | 値の制約                           |
| -------------------- | ---------------- | ---------- | ---------------------------------------------------------------------------------- | ---------------------------------- |
| すべて               | type             | string     | 値の型を指定する。取り得る値は"boolean", "integer", "number", "string"のいずれか。 | 指定できる型は1つのみ              |
|                      | const            | typeに依存 | 定数を指定する。このキーワードが存在する場合は入力・編集不可。                     |                                    |
|                      | enum             | array      | 取り得る値を指定する。                                                             |                                    |
| numberまたは integer | maximum          | number     | 数値が指定された値以下であることを宣言する。                                       |                                    |
|                      | exclusiveMaximum | number     | 数値が指定された値未満であることを宣言する。                                       |                                    |
|                      | minimum          | number     | 数値が指定された値以上であることを宣言する。                                       |                                    |
|                      | exclusiveMinimum | number     | 数値が指定された値より大きいことを宣言する。                                       |                                    |
| string               | maxLength        | integer    | 文字列の長さの最大値を指定する。                                                   | 値は2,147,483,647以下であること。  |
|                      | minLength        | integer    | 文字列の長さの最小値を指定する。0以上。                                            |                                    |
|                      | pattern          | string     | 正規表現で指定したパターンを持つことを宣言する。                                   | 開発言語に依存しないパターンに限定 |
|                      | format           | string     | 文字列のフォーマットを指定。指定可能な値は`フォーマット一覧`を参照のこと。         |                                    |

### invoice.schema.jsonで利用可能なフォーマット一覧

スキーマキーワードformatが取り得る値を下表に示す。

| type     | キーワード                                                                     |
| -------- | ------------------------------------------------------------------------------ |
| date     | 日付。RFC 3339のfull-date。                                                    |
| time     | 時刻。RFC 3339のfull-time。                                                    |
| uri      | URI                                                                            |
| uuid     | UUID。URN形式ではなく素のUUID                                                  |
| markdown | Markdown形式の文字列。このフォーマットはJSONスキーマの標準仕様には存在しない。 |

### invoice.schema.jsonのオプションについて

項目に関する各種のオプションはoptionsキーワードによって指定できる。オプションとして指定可能なキーワードを下表に示す。

| キーワード  | 値の型  | 説明                                                                         |
| ----------- | ------- | ---------------------------------------------------------------------------- |
| format      | string  | 生成する画面部品の種類を明示的に指定する。取り得る値は”textarea”のみとする。 |
| widget      | string  | 生成する画面部品の種類を明示的に指定する。取り得る値は”textarea”のみとする。 |
| rows        | integer | widgetの値が”textarea”の場合のrows属性の値を指定する。                       |
| unit        | string  | 単位の表示内容を指定する。                                                   |
| placeholder | object  | 画面部品に設定するプレイスホルダ。日本語と英語を指定できる。                 |

## invoice.jsonについて

invoice.schema.jsonのバリデーションは、必要なフィールドが定義されているかチェックします。

### invoice.jsonの構築例

<details>
<summary>invoice.jsonの構築例</summary>

```json
{
  "datasetId": "1s1199df4-0d1v-41b0-1dea-23bf4dh09g12",
  "basic": {
    "dateSubmitted": "",
    "dataOwnerId": "0c233ef274f28e611de4074638b4dc43e737ab993132343532343430",
    "dataName": "test-dataset",
    "instrumentId": null,
    "experimentId": null,
    "description": null
  },
  "custom": {
    "sample1": "2023-01-01",
    "sample2": 1.0,
    "sample3": 1
  },
  "sample": {
    "sampleId": "",
    "names": ["test"],
    "composition": null,
    "referenceUrl": null,
    "description": null,
    "generalAttributes": [
      {
        "termId": "3adf9874-7bcb-e5f8-99cb-3d6fd9d7b55e",
        "value": null
      },
      {
        "termId": "e2d20d02-2e38-2cd3-b1b3-66fdb8a11057",
        "value": null
      },
      {
        "termId": "efcf34e7-4308-c195-6691-6f4d28ffc9bb",
        "value": null
      },
      {
        "termId": "1e70d11d-cbdd-bfd1-9301-9612c29b4060",
        "value": null
      },
      {
        "termId": "5e166ac4-bfcd-457a-84bc-8626abe9188f",
        "value": null
      },
      {
        "termId": "0d0417a3-3c3b-496a-b0fb-5a26f8a74166",
        "value": null
      },
      {
        "termId": "efc6a0d5-313e-1871-190c-baaff7d1bf6c",
        "value": null
      }
    ],
    "specificAttributes": [
      {
        "classId": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b",
        "termId": "3250c45d-0ed6-1438-43b5-eb679918604a",
        "value": null
      },
      {
        "classId": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b",
        "termId": "70c2c751-5404-19b7-4a5e-981e6cebbb15",
        "value": null
      },
      {
        "classId": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b",
        "termId": "e2d20d02-2e38-2cd3-b1b3-66fdb8a11057",
        "value": null
      },
      {
        "classId": "01cb3c01-37a4-5a43-d8ca-f523ca99a75b",
        "termId": "518e26a0-4262-86f5-3598-80e18e6ff2af",
        "value": null
      }
    ],
    "ownerId": "de17c7b3f0ff5126831c2d519f481055ba466ddb6238666132316439"
  }
}
```

</details>

### invoice.jsonの定義

| 項目 (JSONポインタ)                          | バリュー型 | フォーマット | 必須 | 説明                                                                                                                                                                           |
| -------------------------------------------- | ---------- | ------------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| (ドキュメントルート)                         | object     | -            | ○    |                                                                                                                                                                                |
| /datasetId                                   | string     | uuid         | ○    | データの登録先となるデータセットのID。                                                                                                                                         |
| /basic                                       | object     | -            | ○    | 送り状の基本情報を格納するオブジェクト。                                                                                                                                       |
| &ensp;&ensp;/dateSubmitted                   | string     | date         | ○    | 送り状が提出された日。読み取り専用。                                                                                                                                           |
| &ensp;&ensp;/dataOwnerId                     | string     | -            | -    | データを所有するユーザのID。                                                                                                                                                   |
| &ensp;&ensp;/dataName                        | string     | -            | ○    | データの名前。                                                                                                                                                                 |
| &ensp;&ensp;/instrumentId                    | string     | uuid         | -    | 装置ID。                                                                                                                                                                       |
| &ensp;&ensp;/experimentId                    | string     | -            | -    | 実験ID。ユーザが自由に採番する。                                                                                                                                               |
| &ensp;&ensp;/description                     | string     | -            | -    | データセットの説明。                                                                                                                                                           |
| /custom                                      | object     | -            | -    | 送り状の固有情報を格納するオブジェクト。オブジェクトに含まれるプロパティは送り状スキーマによって異なる。                                                                       |
| &ensp;&ensp;…                                | -          | -            | -    |                                                                                                                                                                                |
| /sample                                      | object     | -            | -    | 送り状の試料情報を格納するオブジェクト。プロパティはsampleId, ownerIdを除いて試料APIの試料属性と一致。試料への閲覧権限が無い場合は、子のプロパティを含めて出力項目に含めない。 |
| &ensp;&ensp;/sampleId                        | string     | uuid         | -    | 試料のID。送り状の初回提出時に指定した場合、以下のプロパティは不要。                                                                                                           |
| &ensp;&ensp;/names                           | array      | -            | ○    | 試料名のリスト。                                                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;/0                   | string     | -            | ○    | 試料の主たる名前。                                                                                                                                                             |
| &ensp;&ensp;&ensp;&ensp;…                    | -          | -            | -    | 2番目以降の名前。                                                                                                                                                              |
| &ensp;&ensp;/composition                     | string     | -            | -    | 試料の組成。                                                                                                                                                                   |
| &ensp;&ensp;/referenceUrl                    | string     | uri          | -    | 試料の参考URL。                                                                                                                                                                |
| &ensp;&ensp;/description                     | string     | -            | -    | 試料の説明。                                                                                                                                                                   |
| &ensp;&ensp;/generalAttributes               | array      | -            | -    | 一般試料属性のリスト。画面の一般項目に該当する。                                                                                                                               |
| &ensp;&ensp;&ensp;&ensp;/0                   | object     | -            | -    | 最初の属性。※注1 "boolean","integer", "number", "string"は、値の設定がない場合は出力しない。以下。同様。                                                                       |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/termId  | string     | uuid         | ○    | 属性の名前としての用語ID。                                                                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/value   | string     | -            | -    | 属性の値。                                                                                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;…                    | -          | -            | ○    | 2番目以降の属性。                                                                                                                                                              |
| &ensp;&ensp;/specificAttributes              | array      | -            | -    | 特定試料属性のリスト。画面の分類別項目に該当する。                                                                                                                             |
| &ensp;&ensp;&ensp;&ensp;/0                   | object     | -            | -    | 最初の属性。                                                                                                                                                                   |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/classId | string     | uuid         | ○    | 試料分類のID。                                                                                                                                                                 |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/termId  | string     | uuid         | ○    | 属性の名前としての用語ID。                                                                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/value   | string     | -            | -    | 属性の値。                                                                                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;…                    | -          | -            | -    | 2番目以降の属性。                                                                                                                                                              |
| &ensp;&ensp;/ownerId                         | string     | -            | -    | 試料管理者のID。                                                                                                                                                               |

## metadata-def.json

データ構造化が出力するメタデータの名前やデータ型を宣言するファイル。送り状等に入力されるメタデータは、`metadata-def.json`に定義する必要はありません。

### metadata-def.jsonの構築例

<details>
<summary>metadata-def.jsonの構築例</summary>

```json
{
    "operator_identifier": {
        "name": {
            "ja": "測定者",
            "en": "Operator identifier"
        },
        "schema": {
            "type": "string"
        },
        "order": 1,
        "originalName": "Operator"
    },
    "comment": {
        "name": {
            "ja": "コメント",
            "en": "Comment"
        },
        "schema": {
            "type": "string"
        },
        "order": 2,
        "originalName": "Comment"
    },
    "memo": {
        "name": {
            "ja": "メモ",
            "en": "Memo"
        },
        "schema": {
            "type": "string"
        },
        "order": 3,
        "originalName": "Memo",
        "variable": 1
    },
    "measurement_operator": {
        "name": {
            "ja": "測定実施者",
            "en": "Measurement Operator"
        },
        "schema": {
            "type": "string"
        },
        "order": 4,
        "originalName": "Operator",
        "variable": 1
    },
    "specimen": {
        "name": {
            "ja": "試料",
            "en": "Specimen"
        },
        "schema": {
            "type": "string"
        },
        "order": 5,
        "originalName": "SampleName",
        "variable": 1
    },
    "peak": {
        "name": {
            "ja": "ピーク値",
            "en": "peak value"
        },
        "schema": {
            "type": "number"
        },
        "unit": "V"
        "order": 6,
        "variable": 1
    }
}
```

</details>

### metadata-def.jsonの定義

| 項目 (JSONポインタ)             | バリュー型 | フォーマット | 必須 | 説明                                                                                                                        |
| ------------------------------- | ---------- | ------------ | ---- | --------------------------------------------------------------------------------------------------------------------------- |
| (ルート)                        | object     | -            | ○    | JSONドキュメントのルート。                                                                                                  |
| /{最初のキーの名前}             | object     | -            | ○    | 最初のメタデータ項目のキー名。全てのキー名はファイル内でユニークであること。                                                |
| &ensp;&ensp;/name               | object     | -            | ○    | -                                                                                                                           |
| &ensp;&ensp;&ensp;&ensp;/ja     | string     | -            | ○    | メタデータ項目名の日本語表記。                                                                                              |
| &ensp;&ensp;&ensp;&ensp;/en     | string     | -            | ○    | メタデータ項目名の英語表記。                                                                                                |
| &ensp;&ensp;/schema             | object     | -            | ○    | JSON Schema (2020-12)のキーワードであるtypeとformatを使用する。これらのキーワードの定義はJSON Schemaに従う。                |
| &ensp;&ensp;&ensp;&ensp;/type   | string     | -            | ○    | "s メタデータの値の型。取り得る値は"array", "boolean"、"integer"、"number"、"string"。"array"の場合、要素の型は規定しない。 |
| &ensp;&ensp;&ensp;&ensp;/format | string     | -            | -    | "d メタデータの値のフォーマット。取り得る値は"date-time"、"duration"。                                                      |
| &ensp;&ensp;/unit               | string     | -            | -    | メタデータ項目の値に付加する単位。単位が無い場合は省略する。                                                                |
| &ensp;&ensp;/description        | string     | -            | -    | メタデータ項目の説明。                                                                                                      |
| &ensp;&ensp;/uri                | string     | uri          | -    | メタデータ項目のキーに紐づくURI/URL。                                                                                       |
| &ensp;&ensp;/mode               | string     | -            | -    | "S このメタデータ項目が有効である計測モード。計測モードの指定がない場合は省略可。                                           |
| &ensp;&ensp;/order              | integer    | -            | -    | メタデータ項目の表示順序。値の昇順に表示する。同値の場合の表示順は不定。                                                    |
| /{2番目のキーの名前}            | object     | -            | -    | 2番目のメタデータ項目のキー名。                                                                                             |
| &ensp;&ensp;(以下繰り返し)      |            | -            | -    |                                                                                                                             |

!!! Note
  構築例で提示したmetadata-def.jsonに`variable`という定義にない属性がある。この場合、RDEでは、`variable`を無視して取込は行わない。

## metadata.json

metadata-def.jsoは、データ構造化処理が抽出したメタデータを格納するファイルです。

### metadata.jsonの構築例

<details>
<summary>metadata.jsonの構築例</summary>

```json
{
  "constatn": {
    "operator_identifier": {
      "value": "Mike",
    },
    "comment": {
      "value": "sample data",
    },
    "memo": {
      "value": "test",
    },
    "measurement_operator": {
      "value": "Alice",
    },
  },
  "variable": [
    {
      "specimen": {
        "value": "C",
      },
      "peak": {
        "value": 120,
        "unit": "V"
      }
    },
    {
      "specimen": {
        "value": "H",
      },
      "peak": {
        "value": 58,
        "unit": "V"
      }
    },
    {
      "specimen": {
        "value": "O",
      },
      "peak": {
        "value": 190,
        "unit": "V"
      }
    },
  ]
}
```

</details>

### metadata.jsonの定義

| 項目 (JSONポインタ)                        | バリュー型 | フォーマット | 必須 | 説明                                                                                 |
| ------------------------------------------ | ---------- | ------------ | ---- | ------------------------------------------------------------------------------------ |
| /constant                                  | object     | -            | ○    | 全ての計測に共通なメタデータの集合。このファイル定義での「計測」には計算などを含む。 |
| &ensp;&ensp;/{キーの名前}                  | object     | -            | ○    | メタデータのキーの名前。                                                             |
| &ensp;&ensp;&ensp;&ensp;/value             | キーに依存 | -            | ○    | メタデータの値。                                                                     |
| &ensp;&ensp;&ensp;&ensp;/unit              | string     | -            | -    | メタデータの値の単位。単位が無い場合は省略可。                                       |
| &ensp;&ensp;/{キーの名前}                  | object     | -            | ○    | メタデータのキーの名前。                                                             |
| ...                                        | -          | -            | ○    |                                                                                      |
| /variable                                  | array      | -            | ○    | 計測ごとに異なるメタデータセットの配列。                                             |
| &ensp;&ensp;/0                             | object     | -            | ○    | 最初の計測に固有なメタデータの集合。                                                 |
| &ensp;&ensp;&ensp;&ensp;/{キーの名前}      | object     | -            | -    | メタデータのキーの名前。配列の各要素でキーが存在しない場合は省略可能。               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/value | キーに依存 | -            | ○    | メタデータの値。                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/unit  | string     | -            | -    | メタデータの値の単位。単位が無い場合は省略可。                                       |
| &ensp;&ensp;&ensp;&ensp;/{キーの名前}      | object     | -            | -    | メタデータのキーの名前。                                                             |
| &ensp;&ensp;&ensp;&ensp;...                | -          | -            | ○    |                                                                                      |
| &ensp;&ensp;/1                             | object     | -            | ○    | 2番目の計測に固有なメタデータの集合。                                                |
| &ensp;&ensp;(以下繰り返し)                 | -          | -            | ○    |                                                                                      |

### 繰り返しメタデータについて

RDEには、計測ごとに異なるメタデータセットとして繰り返しメタデータが定義可能です。繰り返しメタデータとして登録する場合、`variable: 1`というフィールドを追加してください。RDEのシステムには、`variable`は取込は行われません。

しかし、`metadata-def.json`で`variable: 1`にセットしたメタデータについては、`metadata.json`で`variable`に追加されます。

## catalog.schema.json

データカタログのスキーマファイル。スキーマの形式はJSON Schemaの標準仕様に準拠します。

### catalog.schema.json構築例

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://rde.nims.go.jp/rde/dataset-templates/dataset_template_custom_sample/catalog.schema.json",
    "type": "object",
    "required": [
        "catalog"
    ],
    "description": "dataset_template_custom_sample",
    "properties": {
        "catalog": {
            "type": "object",
            "label": {
                "ja": "RDEデータセットテンプレートサンプル固有情報",
                "en": "dataset_template__custom_sample"
            },
            "required": [],
            "properties": {
                "dataset_title": {
                    "label": {
                        "ja": "データセット名",
                        "en": "Dataset Title"
                    },
                    "type": "string"
                },
                "abstract": {
                    "label": {
                        "ja": "概要",
                        "en": "Abstract"
                    },
                    "type": "string"
                },
                "data_creator": {
                    "label": {
                        "ja": "作成者",
                        "en": "Data Creator"
                    },
                    "type": "string"
                },
                "language": {
                    "label": {
                        "ja": "言語",
                        "en": "Language"
                    },
                    "type": "string"
                },
                "experimental_apparatus": {
                    "label": {
                        "ja": "使用装置",
                        "en": "Experimental Apparatus"
                    },
                    "type": "string"
                },
                "data_distribution": {
                    "label": {
                        "ja": "データの再配布",
                        "en": "Data Distribution"
                    },
                    "type": "string"
                },
                "raw_data_type": {
                    "label": {
                        "ja": "データの種類",
                        "en": "Raw Data Type"
                    },
                    "type": "string"
                },
                "stored_data": {
                    "label": {
                        "ja": "格納データ",
                        "en": "Stored Data"
                    },
                    "type": "string",
                    "options": {
                        "widget": "textarea",
                        "rows": 5
                    }
                },
                "remarks": {
                    "label": {
                        "ja": "備考",
                        "en": "Remarks"
                    },
                    "type": "string",
                    "options": {
                        "widget": "textarea",
                        "rows": 5
                    }
                },
                "references": {
                    "label": {
                        "ja": "参考論文",
                        "en": "References"
                    },
                    "type": "string"
                }
            }
        }
    }
}
```

### catalog.schema.jsonの定義

| 項目 (JSONポインタ表現)                                                      | バリュー型       | フォーマット | 必須 | 説明                                                                                                     |
| ---------------------------------------------------------------------------- | ---------------- | ------------ | ---- | -------------------------------------------------------------------------------------------------------- |
| (ドキュメントルート)                                                         |                  | object       | -    | ○                                                                                                        |
| /$schema                                                                     | string           | uri          | ○    | メタスキーマ(スキーマのスキーマ)のID。固定文字列`https://json-schema.org/draft/2020-12/schema`を指定。   |
| /$id                                                                         | string           | uri          | ○    | このスキーマのID。ユニークであること。                                                                   |
| /description                                                                 | string           | -            | -    | このスキーマの説明。                                                                                     |
| /type                                                                        | string           | -            | ○    | 値は固定。                                                                                               |
| /required                                                                    | array            | -            | -    | 値は固定。                                                                                               |
| /properties                                                                  | object           | -            | ○    |                                                                                                          |
| &ensp;&ensp;/catalog                                                         | object           | -            | ○    | データカタログ項目を格納するオブジェクト。                                                               |
| &ensp;&ensp;&ensp;&ensp;/type                                                | string           | -            | ○    | 値は固定。                                                                                               |
| &ensp;&ensp;&ensp;&ensp;/label                                               | object           | -            | ○    | 見出しとして使用する文字列。言語別に指定する。                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/ja                                      | string           | -            | ○    | 見出しの日本語表記。                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/en                                      | string           | -            | ○    | 見出しの英語表記。                                                                                       |
| &ensp;&ensp;&ensp;&ensp;/required                                            | object           | -            | ○    | 必須のキー名を指定する。複数指定可。                                                                     |
| &ensp;&ensp;&ensp;&ensp;/properties                                          | object           | -            | ○    | データカタログ項目のマップ。表示や入力する際の項目の順序は、このスキーマでの記述順に従う。               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/{最初のキーの名前}                      | object           | -            | ○    | 最初の項目のキー名。キーの名前はファイル全体でユニークであること。                                       |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/type                        | string           | -            | ○    | 項目の値のデータ型。"boolean", "integer", "number", "string"のいずれか1つを指定する。                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/description                 | string           | -            | -    | 項目の説明。画面には表示しない。                                                                         |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/examples                    | array            | -            | -    | 値の例。画面には表示しない。                                                                             |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/default                     | 任意             | -            | -    | 初期値を指定する。                                                                                       |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/{最初のスキーマキーワード}  | キーワードに依存 | -            | -    | 項目の値に関する制約を指定するキーワード。                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/{2番目のスキーマキーワード} | キーワードに依存 | -            | -    | 同上                                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;…       -                    | -                | -            |      |                                                                                                          |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/label                       | object           | -            | ○    | 画面に表示する項目のラベル。言語別に指定する。                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/ja              | string           | -            | ○    | 日本語表示時のラベル。                                                                                   |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/en              | string           | -            | ○    | 英語表示時のラベル。                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/options                     | object           | -            | -    | 項目に関するオプションの指定。                                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/widget          | string           | -            | -    | 画面部品を明示的に指定する場合に使う。"textarea"のみ指定可。通常はtypeの値に応じた画面部品が生成される。 |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/rows            | integer          | -            | -    | 画面部品がtextareaの場合の行数を指定する。                                                               |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/unit            | string           | -            | -    | 画面に表示する単位。                                                                                     |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/placeholder     | object           | -            | -    | 画面部品に設定するプレイスホルダ。言語別に指定する。省略可能。                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/ja  | string           | -            | -    | 日本語表示時のプレイスホルダ。                                                                           |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/en  | string           | -            | -    | 英語表示時のプレイスホルダ。                                                                             |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;/{2番目のキーの名前}                     | object           | -            | ○    | 2番目の項目のキー名。                                                                                    |
| &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;(以下繰り返し)-              | -                | -            |      |                                                                                                          |

### catalog.schema.jsonで利用可能なスキーマキーワード一覧

項目の値に関する制約として指定可能なスキーマキーワードを下表に示す。

| type                 | キーワード       | 値の型     | 説明                                                                               | 値の制約                           |
| -------------------- | ---------------- | ---------- | ---------------------------------------------------------------------------------- | ---------------------------------- |
| すべて               | type             | string     | 値の型を指定する。取り得る値は"boolean", "integer", "number", "string"のいずれか。 | 指定できる型は1つのみ              |
|                      | const            | typeに依存 | 定数を指定する。このキーワードが存在する場合は入力・編集不可。                     |                                    |
|                      | enum             | array      | 取り得る値を指定する。                                                             |                                    |
| numberまたは integer | maximum          | number     | 数値が指定された値以下であることを宣言する。                                       |                                    |
|                      | exclusiveMaximum | number     | 数値が指定された値未満であることを宣言する。                                       |                                    |
|                      | minimum          | number     | 数値が指定された値以上であることを宣言する。                                       |                                    |
|                      | exclusiveMinimum | number     | 数値が指定された値より大きいことを宣言する。                                       |                                    |
| string               | maxLength        | integer    | 文字列の長さの最大値を指定する。                                                   | 値は2,147,483,647以下であること。  |
|                      | minLength        | integer    | 文字列の長さの最小値を指定する。0以上。                                            |                                    |
|                      | pattern          | string     | 正規表現で指定したパターンを持つことを宣言する。                                   | 開発言語に依存しないパターンに限定 |
|                      | format           | string     | 文字列のフォーマットを指定。指定可能な値は`フォーマット一覧`を参照のこと。         |                                    |

### catalog.schema.jsonのオプションについて

項目に関する各種のオプションはoptionsキーワードによって指定できる。オプションとして指定可能なキーワードを下表に示す。

| キーワード  | 値の型  | 説明                                                                         |
| ----------- | ------- | ---------------------------------------------------------------------------- |
| format      | string  | 生成する画面部品の種類を明示的に指定する。取り得る値は”textarea”のみとする。 |
| widget      | string  | 生成する画面部品の種類を明示的に指定する。取り得る値は”textarea”のみとする。 |
| rows        | integer | widgetの値が”textarea”の場合のrows属性の値を指定する。                       |
| unit        | string  | 単位の表示内容を指定する。                                                   |
| placeholder | object  | 画面部品に設定するプレイスホルダ。日本語と英語を指定できる。                 |
