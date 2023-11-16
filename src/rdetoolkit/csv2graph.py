# ---------------------------------------------------------
# Copyright (c) 2022, Materials Data Platform Center, NIMS
#
# This software is released under the MIT License.
#
#  Contributor:
#       Hiroshi Shinotsuka
# ---------------------------------------------------------
# coding: utf-8

__version__ = "1.0.7"

import csv
import os.path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import ScalarFormatter

from rdetoolkit.exceptions import StructuredError

maxTitleLen = 35


def readOption(csvFilePath, enc="utf_8"):
    """
    Parses specific options from a CSV file and returns them as a dictionary.

    This function recognizes lines in the CSV file that start with '#' as options.
    Each option follows the format:

    title, Title
    dimension, x, y
    x, Name of x-axis, Unit of x-axis
    y, Name of y-axis, Unit of y-axis
    legend, Legend1, Legend2, ...

    Args:
        csvFilePath (str): Path to the CSV file.
        enc (str, optional): Encoding of the CSV file. Defaults to "utf_8".

    Returns:
        dict: A dictionary where the key is the option name and the value is the option value.

    Note:
        - Currently, only 2D plots (x, y) are considered.
        - Options that don't fit the expected format or are unknown are also registered in the dictionary.

    Caution:
        正確な実装の内容は、この関数を実装した開発者に問い合わせてください。
    """
    ret = {}
    axis = []
    for tokens in csv.reader(open(csvFilePath, "r", encoding=enc)):
        if len(tokens) == 0:
            continue
        if len(tokens[0]) == 0:
            continue
        if not tokens[0].startswith("#"):
            continue
        tokens = [
            tokens[0][1:].strip(),
        ] + [tok.strip() for tok in tokens[1:]]
        if tokens[0].startswith("#"):
            continue

        if tokens[0] == "title":
            ret[tokens[0]] = tokens[1]
        elif tokens[0] == "dimension":
            axis = tokens[1:]
            ret[tokens[0]] = axis  # 現状では"x,y"の2次元プロットのみを想定している
        elif tokens[0] in axis:
            ret["axisName_" + tokens[0]] = tokens[1]
            if len(tokens) > 2:
                ret["axisUnit_" + tokens[0]] = tokens[2]
            if len(tokens) > 3:
                ret["axisInverse_" + tokens[0]] = True
        elif tokens[0] == "legend":
            ret[tokens[0]] = tokens[1:]
        else:
            ret[tokens[0]] = tokens[1:]  # 不明なオプションも辞書登録しておく

    return ret


def _writeGraphImgFile_impl(df, opt, graphTitleShort, showLegend, pngFilePath):
    """
    Generates a graph from the provided dataframe and saves it as an image file.

    This function creates a graph based on the data from the dataframe `df` and various options
    provided in the `opt` dictionary. The graph is then saved to the specified file path `pngFilePath`.

    Args:
        df (pandas.DataFrame): Dataframe containing the data to be plotted. Expected to have
            even columns, where every two columns represent x and y data respectively.
        opt (dict): Dictionary of options to modify the appearance and behavior of the graph.
            Expected keys include but are not limited to:
            - "axisInverse_x", "axisInverse_y": Whether to invert the respective axis.
            - "axisScale_x", "axisScale_y": The scale type for the respective axis (e.g., "log").
            - "axisFormat_y": The format for the y-axis (e.g., "sci").
            - "axisUnit_x", "axisUnit_y": Units for the respective axis.
            - "axisName_x", "axisName_y": Names for the respective axis.
            - "grid": Whether to show a grid on the graph.
            - "scaleFactor_x", "scaleFactor_y": Scaling factors for the respective axis data.
            - "legend": List of legend labels for the plotted data.
        graphTitleShort (str): Short title to be displayed on the graph. If empty, no title is displayed.
        showLegend (bool): Whether to display the legend on the graph.
        pngFilePath (str): Path to save the generated graph as a PNG image.

    Note:
        - The function assumes that the dataframe `df` has even columns, where every two columns represent x and y data respectively.
        - Some functionalities or options commented out in the original code are not included in this description.

    Caution:
        正確な実装の内容は、この関数を実装した開発者に問い合わせてください。
    """
    fig = plt.figure(figsize=(6.4, 4.8))
    ax = fig.add_subplot(1, 1, 1)
    fig.subplots_adjust(left=0.17, bottom=0.155, right=0.95, top=0.9, wspace=None, hspace=None)
    formatter = ScalarFormatter(useMathText=True)
    ax.yaxis.set_major_formatter(formatter)
    if opt.get("axisInverse_x", False):
        ax.invert_xaxis()
    if opt.get("axisInverse_y", False):
        ax.invert_yaxis()
    if opt.get("axisScale_x", "") == "log":
        ax.set_xscale("log")
    # if opt.get("axisFormat_x", opt.get("axisScale_x", "")) == "":   # 元プログラムではy側のみを形式指定していた
    #     ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    #     ax.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
    if opt.get("axisScale_y", "") == "log":
        ax.set_yscale("log")
    if opt.get("axisFormat_y", opt.get("axisScale_y", "sci")) == "sci":
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    if "axisUnit_x" in opt:
        ax.set_xlabel(f"{opt['axisName_x']} ({opt['axisUnit_x']})")
    else:
        ax.set_xlabel(f"{opt['axisName_x']}")
    if "axisUnit_y" in opt:
        ax.set_ylabel(f"{opt['axisName_y']} ({opt['axisUnit_y']})")
    else:
        ax.set_ylabel(f"{opt['axisName_y']}")
    if opt.get("grid", False):
        ax.grid(True)

    if len(graphTitleShort) > 0:
        ax.set_title(graphTitleShort)

    xFactor = opt.get("scaleFactor_x", 1.0)
    yFactor = opt.get("scaleFactor_y", 1.0)
    for iLegend in range(0, len(df.columns), 2):
        ax.plot(
            xFactor * df.iloc[:, iLegend],
            yFactor * df.iloc[:, iLegend + 1],
            lw=1,
            label=opt["legend"][int(iLegend / 2)],
        )
    if showLegend:
        ax.legend()

    def _getScalarFloat(opt, key):
        if key not in opt:
            return None
        return float(opt[key][0])

    ax.set_xlim(xmin=_getScalarFloat(opt, "xmin"), xmax=_getScalarFloat(opt, "xmax"))
    ax.set_ylim(ymin=_getScalarFloat(opt, "ymin"), ymax=_getScalarFloat(opt, "ymax"))

    fig.savefig(pngFilePath)
    plt.close(fig)


def writeGraphImgFile(df, opt, graphTitleOrg, pngFilePath):
    if len(graphTitleOrg) > maxTitleLen:  # タイトルは最大文字列長以上は省略する
        graphTitleShort = graphTitleOrg[:maxTitleLen] + "..."
    else:
        graphTitleShort = graphTitleOrg

    if "showLegend" in opt:
        showLegend = opt["showLegend"]
    elif len(df.columns) <= 2:  # XYの2列で1系列を表す。列数2ならば1系統のみなので凡例表示しない
        showLegend = False
    else:
        showLegend = True
    _writeGraphImgFile_impl(df, opt, graphTitleShort, showLegend, pngFilePath)


def main(
    fBaseName,
    twoColumnsCsvFilePathList,
    pngFilesMainDir,
    pngFilesOtherDir,
    makeOtherImages="auto",
    **explicitOptions,
):
    """
    Generates main and other images based on provided CSV files and options.

    This function creates a primary graph image using the data from the concatenated CSV files
    and saves it to the specified directory `pngFilesMainDir`. If `makeOtherImages` is set to True,
    it will also generate individual images for each CSV file and save them to the `pngFilesOtherDir` directory.

    Args:
        fBaseName (str): Base name for the generated image files.
        twoColumnsCsvFilePathList (List[str]): List of paths to the two-columns CSV files to be processed.
        pngFilesMainDir (str): Directory to save the primary graph image.
        pngFilesOtherDir (str): Directory to save the individual graph images for each CSV file.
        makeOtherImages (Union[str, bool], optional): Determines whether to generate individual images for
            each CSV file. If set to "auto", the decision is made based on the number of legends in the CSV.
            Defaults to "auto".
        **explicitOptions: Variable length keyword arguments for customizing the generated graph images.
            To modify settings only for the main image, prefix the option with "main_" (e.g., main_title="graph_main").
            To modify settings only for the other images, prefix with "other_" (e.g., other_title="graph_001").
            To modify settings for all images, provide the option without a prefix (e.g., title="graphs").

    Raises:
        StructuredError: If there's a mismatch between the number of columns in the dataframe and the expected columns
            based on the legend and dimensions.

    Note:
        - The function uses the first row of the first CSV file to determine axis names and units.
        - The `writeGraphImgFile` function is used internally to generate the images.
        - Commented-out parts in the original code are not included in this description.

    Caution:
        正確な実装の内容は、この関数を実装した開発者に問い合わせてください。
    """
    # get options from header and argument

    # get legend list from csv file names, ["hoge_O1s.csv", "hoge_Si2p.csv"]
    legendList = [os.path.basename(f).split("_")[-1].split(".")[0] for f in twoColumnsCsvFilePathList]

    # concatenate several csv files along y-axis. legend is added to each column.
    dfList = []
    for legend, f in zip(legendList, twoColumnsCsvFilePathList):
        df = pd.read_csv(f)
        df.columns = [f"{legend}_{col}" for col in df.columns]
        dfList.append(df)

    dfMain = pd.concat(dfList, axis=1)

    # read one file again, to get option
    df = pd.read_csv(twoColumnsCsvFilePathList[0], nrows=1)
    columns = df.columns.values
    axis = columns[0].split("(")
    axisName_x = axis[0].strip()
    axisUnit_x = axis[1].strip().rstrip(")")
    axis = columns[1].split("(")
    axisName_y = axis[0].strip()
    axisUnit_y = axis[1].strip().rstrip(")")

    opt = {
        "title": "",
        "dimension": ["x", "y"],
        "axisName_x": axisName_x,
        "axisUnit_x": axisUnit_x,
        "axisInverse_x": True,
        "axisName_y": axisName_y,
        "axisUnit_y": axisUnit_y,
        "legend": legendList,
    }
    if makeOtherImages == "auto":
        makeOtherImages = len(opt["legend"]) > 1

    # main image
    #    opt = {**headerOptions, **_expOptShare, **_expOptMain}  # 三つの辞書を結合した新たな辞書を作成。キー重複の場合は後ろの辞書オブジェクトの値が優先

    if len(dfMain.columns) == len(opt["legend"]) * len(opt["dimension"]):
        columnNames = []
        for col in opt["legend"]:
            columnNames += [f"{col}_{i}" for i in range(len(opt["dimension"]) - 1)] + [
                col,
            ]
        dfMain = dfMain.rename(columns={i: columnNames[i] for i in range(len(columnNames))})
    else:
        raise StructuredError("ERROR in csv2graph: csv columns are invalid")

    fpathMainImage = os.path.join(pngFilesMainDir, f"{fBaseName}.png")
    writeGraphImgFile(dfMain, opt, opt["title"], fpathMainImage)

    if makeOtherImages:
        # other images
        for legend, df in zip(legendList, dfList):
            graphTitleOtherImage = f"{fBaseName}_{legend}"
            fpathOtherImage = os.path.join(pngFilesOtherDir, f"{fBaseName}_{legend}.png")
            writeGraphImgFile(df, opt, graphTitleOtherImage, fpathOtherImage)
