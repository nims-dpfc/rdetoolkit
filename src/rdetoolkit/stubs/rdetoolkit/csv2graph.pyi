from rdetoolkit.exceptions import StructuredError as StructuredError

maxTitleLen: int

def readOption(csvFilePath, enc: str = ...): ...
def writeGraphImgFile(df, opt, graphTitleOrg, pngFilePath) -> None: ...
def main(fBaseName, twoColumnsCsvFilePathList, pngFilesMainDir, pngFilesOtherDir, makeOtherImages: str = ..., **explicitOptions) -> None: ...
