# filechecker

`filechecker`では、入力ファイル操作に関するインターフェースが定義されています。

## IInputFileHelper

抽象インターフェース `IInputFileHelper` を定義しています。このインターフェースは、入力ファイル操作のためのヘルパーを表すものです。

::: src.rdetoolkit.interfaces.filechecker.IInputFileHelper
    options:
        members:
            - get_zipfiles
            - unpacked

## IInputFileChecker

抽象インターフェース `IInputFileChecker` を定義しています。このインターフェースは、入力ファイルのチェックのためのヘルパーを表すものです。

::: src.rdetoolkit.interfaces.filechecker.IInputFileChecker
    options:
        members:
            - parse

## ICompressedFileStructParser

抽象インターフェース `ICompressedFileStructParser` を定義しています。このインターフェースは、圧縮ファイルの構造解析のためのヘルパーを表すものです。

::: src.rdetoolkit.interfaces.filechecker.ICompressedFileStructParser
    options:
        members:
            - read
