## Magic Variableによるデータ登録について

- 起動条件: データ登録時に`${filename}`を入力すると入力したファイル名がデータ名に登録される
- 対象モード: invoiceモード、Excelinvoiceモード, マルチファイルモード
- 備考: この機能は`RDEToolKit v0.1.5`以降から利用可能です。

このモードは、デフォルトの入力モードinvoiceモードのみで実行される処理になります。下記のように、データ登録時に`${filename}`という名称でデータ名を登録すると、自動的にファイル名をデータ名に転記するモードです。
以下の例では、データ名に、「`${filename}`」を入力し、ファイル`xrd_CI0034.rasx`を登録すると、データ名が、`xrd_CI0034.rasx`に置換されます。

![magic_filename](../img/magic_filename.svg)

### 実行前のinvoice.json

```json
{
    "datasetId": "4c747c9a-ef13-4058-9e36-d76bb6531658",
    "basic": {
        "dateSubmitted": "2023-06-27",
        "dataOwnerId": "222aaa4798cb8c1c3c19c66062c7e55a9b4255fe336461301233456",
        "dataName": "${filename}",
        "instrumentId": null,
        "experimentId": null,
        "description": ""
    },
    "custom": null
}
```

### 実行後のinvoice.json

```json
{
    "datasetId": "4c747c9a-ef13-4058-9e36-d76bb6531658",
    "basic": {
        "dateSubmitted": "2023-06-27",
        "dataOwnerId": "222aaa4798cb8c1c3c19c66062c7e55a9b4255fe336461301233456",
        "dataName": "data0000.dat",
        "instrumentId": null,
        "experimentId": null,
        "description": ""
    },
    "custom": null
}
```
