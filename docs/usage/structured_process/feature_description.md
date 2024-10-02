# データタイル説明欄への自動記述について

!!! Reference
    - API Documentation: [update_description_with_features()](/rdetoolkit/invoicefile/#update_description_with_features)

`data/tasksupport/metadata-def.json`に、`_feature`フィールドを定義することで、自動的に説明欄へ記述します。例えば、以下の例では、`length`と、`weight`に`_feature=true`が定義されているため、データタイルの説明欄へ自動的に記述されます。

```json
{
    "length": {
        "name": {
            "ja": "長さ",
            "en": "length"
        },
        "schema": {
            "type": "number"
        },
        "unit": "nm",
        "_feature": true
    },
    "weight": {
        "name": {
            "ja": "重さ",
            "en": "weight"
        },
        "schema": {
            "type": "number"
        },
        "unit": "nm",
        "_feature": true
    },
    "hight": {
        "name": {
            "ja": "高さ",
            "en": "hight"
        },
        "schema": {
            "type": "number"
        },
        "unit": "nm"
    }
}
```

`_feature`フィールドがあるメタデータは、以下のフォーマットで変換され、`invoice/invoice.json`の`basic.description`へ転記されます。

!!! Tip
    key名は日本語名のみの対応です。valueは`meta/metadata.json`を参照します。

=== "単位(unitフィールド)あり"

    `invoice/invoice.json`記載例

    ```json
    {
        "basic": {
            "description": "長さ(nm):100\n重さ(nm):200"
        }
    }
    ```

=== "単位(unitフィールド)なし"

    `invoice/invoice.json`記載例

    ```json
    {
        "basic": {
            "description": "長さ:100\n重さ:200"
        }
    }
    ```
