# filechecker

In `filechecker`, interfaces for handling input file operations are defined.

## IInputFileHelper

The abstract interface `IInputFileHelper` is defined. This interface represents a helper for handling input file operations.

::: src.rdetoolkit.interfaces.filechecker.IInputFileHelper
    options:
        members:
            - get_zipfiles
            - unpacked

## IInputFileChecker

The abstract interface `IInputFileChecker` is defined. This interface represents a helper for checking input files.

::: src.rdetoolkit.interfaces.filechecker.IInputFileChecker
    options:
        members:
            - parse

## ICompressedFileStructParser

The abstract interface `ICompressedFileStructParser` is defined. This interface represents a helper for parsing the structure of compressed files.

::: src.rdetoolkit.interfaces.filechecker.ICompressedFileStructParser
    options:
        members:
            - read
