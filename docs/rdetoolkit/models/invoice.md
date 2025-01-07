# invoice

The `models/invoice` module defines models for the Invoice and provides a registry model that is referenced in the ExcelInvoice implementation.

## FixedHeaders

::: src.rdetoolkit.models.invoice.FixedHeaders
    options:
        members:
            - to_template_dataframe

### HeaderRow1

::: src.rdetoolkit.models.invoice.HeaderRow1

### HeaderRow2

::: src.rdetoolkit.models.invoice.HeaderRow2

### HeaderRow3

::: src.rdetoolkit.models.invoice.HeaderRow3

### HeaderRow4

::: src.rdetoolkit.models.invoice.HeaderRow4

## TemplateConfig

::: src.rdetoolkit.models.invoice.TemplateConfig

## BaseTermRegistry

::: src.rdetoolkit.models.invoice.BaseTermRegistry

## GeneralTermRegistry

::: src.rdetoolkit.models.invoice.GeneralTermRegistry
    options:
        members:
            - search
            - by_term_id
            - by_ja
            - by_en

## SpecificTermRegistry

::: src.rdetoolkit.models.invoice.GeneralTermRegistry
    options:
        members:
            - search
            - by_term_and_class_id
            - by_key_name
            - by_ja
            - by_en

## GeneralAttributeConfig

::: src.rdetoolkit.models.invoice.GeneralAttributeConfig

## SpecificAttributeConfig

::: src.rdetoolkit.models.invoice.SpecificAttributeConfig
