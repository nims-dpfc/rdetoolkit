# input_controller

In `input_controller`, processes for file operations according to various input modes of RDE are defined.

Depending on the input file, RDE has the following four modes:

- Invoice mode
- ExcelInvoice mode
- RDEformat mode
- Multifile mode

## InvoiceChecke

::: src.rdetoolkit.impl.input_controller.InvoiceChecker
    handler: python
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
    handler: python
    options:
        members:
            - parse
            - _get_zipfiles
            - _unpacked
            - _get_rawfiles

## MultiFileChecker

::: src.rdetoolkit.impl.input_controller.MultiFileChecker
    handler: python
    options:
        members:
            - parse
            - _get_group_by_files
            - _unpacked
