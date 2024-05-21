# compressed_controller

In `compressed_controller`, processes are defined for handling compressed files input from RDE.

## CompressedFlatFileParser

::: src.rdetoolkit.impl.compressed_controller.CompressedFlatFileParser
    options:
        members:
            - read
            - _unpacked
            - _is_excluded

## CompressedFolderParser

::: src.rdetoolkit.impl.compressed_controller.CompressedFolderParser
    handler: python
    options:
        members:
            - read
            - _unpacked
            - validation_uniq_fspath
            - _is_excluded

## parse_compressedfile_mode

::: src.rdetoolkit.impl.compressed_controller.parse_compressedfile_mode
