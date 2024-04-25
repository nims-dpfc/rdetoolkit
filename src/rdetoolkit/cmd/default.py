custom_fields = {
    "type": "object",
    "label": {"ja": "固有情報", "en": "Custom Information"},
    "required": [
        "sample1",
    ],
    "properties": {"sample1": {"label": {"ja": "サンプル１", "en": "sample1"}, "type": "string"}, "sample2": {"label": {"ja": "サンプル２", "en": "sample2"}, "type": "number"}},
}

sample_fields = {"type": "object", "label": {"ja": "試料情報", "en": "Sample Information"}, "properties": {}}

propaties = {"custom": custom_fields, "sample": sample_fields}


invoice_json = {
    "datasetId": "3f976089-7b0b-4c66-a035-f48773b018e6",
    "basic": {"dateSubmitted": "", "dataOwnerId": "dummy!7e4792d1a8440bcfa08925d35e9d92b234a963449f03df449e", "dataName": "toy dataset", "instrumentId": None, "experimentId": None, "description": None},
    "custom": {"toy_data1": "2023-01-01", "toy_data2": 1.0},
    "sample": {
        "sampleId": "",
        "names": ["<Please enter a sample name>"],
        "composition": None,
        "referenceUrl": None,
        "description": None,
        "generalAttributes": [],
        "specificAttributes": [],
        "ownerId": "dummy!7e4792d1a8440bcfa08925d35e9d92b234a963449f03df449e",
    },
}
