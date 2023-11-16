# input_controller

`input_controller`では、RDEの各種入力モードに応じたファイル操作の処理が定義されています。

RDEには、入力ファイルに応じて、以下の4つのモードが存在します。

- インボイスモード
- エクセルインボイスモード
- RDEフォーマットモード
- マルチファイルモード

## InvoiceChechker

::: src.rdetoolkit.impl.input_controller.InvoiceChechker
    options:
        members:
            - parse
            - _get_group_by_files

## ExcelInvoiceChecker

::: src.rdetoolkit.impl.input_controller.ExcelInvoiceChecker
    handler: python
    options:
        members:
            - read
            - get_index
            - _get_group_by_files
            - _get_rawfiles
            - _validate_files
            - _detect_invalid_zipfiles
            - _detect_invalid_excel_invoice_files
            - _detect_invalid_other_files

## RDEFormatChecker

::: src.rdetoolkit.impl.input_controller.RDEFormatChecker
    options:
        members:
            - parse
            - _get_zipfiles
            - _unpacked
            - _get_rawfiles

## MultiFileChecker

::: src.rdetoolkit.impl.input_controller.MultiFileChecker
    options:
        members:
            - parse
            - _get_group_by_files
            - _unpacked
