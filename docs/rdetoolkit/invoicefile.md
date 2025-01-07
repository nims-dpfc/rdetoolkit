# invoicefile

In `invoicefile.py`, processes for handling invoices are defined.

## read_excelinvoice

::: src.rdetoolkit.invoicefile.read_excelinvoice

## check_exist_rawfiles

::: src.rdetoolkit.invoicefile.check_exist_rawfiles

## _assign_invoice_val

::: src.rdetoolkit.invoicefile._assign_invoice_val

## overwrite_invoicefile_for_dpfterm

::: src.rdetoolkit.invoicefile.overwrite_invoicefile_for_dpfterm

## InvoiceFile

::: src.rdetoolkit.invoicefile.InvoiceFile
    options:
        members:
            - read
            - overwrite

## ExcelInvoiceFile

::: src.rdetoolkit.invoicefile.ExcelInvoiceFile
    options:
        members:
            - read
            - overwrite
            - generate_template
            - save
            - check_intermittent_empty_rows

## ExcelInvoiceTemplateGenerator

::: src.rdetoolkit.invoicefile.ExcelInvoiceTemplateGenerator
    options:
        members:
            - generate
            - save

## backup_invoice_json_files

::: src.rdetoolkit.invoicefile.backup_invoice_json_files

## update_description_with_features

::: src.rdetoolkit.invoicefile.update_description_with_features

## RuleBasedReplacer

::: src.rdetoolkit.invoicefile.RuleBasedReplacer
    options:
        members:
            - load_rules
            - get_apply_rules_obj
            - set_rule
            - write_rule

## apply_default_filename_mapping_rule

::: src.rdetoolkit.invoicefile.apply_default_filename_mapping_rule

## apply_magic_variable

::: src.rdetoolkit.invoicefile.apply_magic_variable
