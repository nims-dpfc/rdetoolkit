# compressed_controller

`compressed_controller`では、RDEから入力された圧縮ファイルを操作するための処理が定義されています。

## CompressedFlatFileParser

::: src.rdetoolkit.impl.compressed_controller.CompressedFlatFileParser
    options:
        members:
            - read
            - _unpacked

## CompressedFolderParser

::: src.rdetoolkit.impl.compressed_controller.CompressedFolderParser
    handler: python
    options:
        members:
            - read
            - _unpacked
            - validation_uniq_fspath

## parse_compressedfile_mode

::: src.rdetoolkit.impl.compressed_controller.parse_compressedfile_mode
