# invoiceFile

`invocieFile.py`では、送り状を操作する処理が定義されています。

## readExcelInvoice

::: src.rdetoolkit.invoiceFile.readExcelInvoice

## checkExistRawFiles

::: src.rdetoolkit.invoiceFile.checkExistRawFiles

## _assignInvoiceVal

::: src.rdetoolkit.invoiceFile._assignInvoiceVal

## overwriteInvoiceFileforDPFTerm

::: src.rdetoolkit.invoiceFile.overwriteInvoiceFileforDPFTerm

## InvoiceFile

::: src.rdetoolkit.invoiceFile.InvoiceFile
    options:
        members:
            - read
            - overwrite

## ExcelInvoiceFile

::: src.rdetoolkit.invoiceFile.ExcelInvoiceFile
    options:
        members:
            - read
            - overwrite
            - _process_invoice_sheet
            - _process_general_term_sheet
            - _process_specific_term_sheet
            - _check_intermittent_empty_rows
            - _assign_basic
            - _assign_sample
            - _assign_sample_general
            - _assign_sample_specific
            - _assign_custom
            - _ensure_sample_id_order
            - _detect_encoding
            - _load_json
            - _write_json
            - _initialize_sample
            - _initialize_non_sample

## backup_invoice_json_files

::: src.rdetoolkit.invoiceFile.backup_invoice_json_files

## update_description_with_features

::: src.rdetoolkit.invoiceFile.update_description_with_features

## RuleBasedReplacer

マッピングルールを生成・適用するクラス。

> このルールは、運用上invoiceモードの時のみ利用できます。

::: src.rdetoolkit.invoiceFile.RuleBasedReplacer
    options:
        members:
            - load_rules
            - apply_rules
            - set_rule
            - write_rule

## apply_default_filename_mapping_rule

デフォルトで`invoice.baisc.dataName`に`${filename}`がある場合、対象のオブジェクトの値を書き換える

> このルールは、運用上invoiceモードの時のみ利用できます。

::: src.rdetoolkit.invoiceFile.apply_default_filename_mapping_rule
