#!/usr/bin/python3
"""
This is the ChaoticSpokesTk.py program, which is a variation on the 
so-called Martin Attractor, or Hopalong, from Dr. Barry Martin that was 
described in a 1986 edition of Scientific America. The Chaotic Spokes 
program provides various "tweaks" to the original Hopalong equations,
which results in spoke-like patterns that emerge from a central, often
Hopalong-like pattern. 
"""

import os
import sys
import string
import math
import datetime
from collections import OrderedDict
from collections import namedtuple

import matplotlib
import matplotlib as mpl
import matplotlib.colors as mc

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import numpy as np

import tkinter as tk
from tkinter import filedialog
from tkinter import VERTICAL, RIGHT, LEFT
from tkinter import TOP, BOTH, DISABLED
from tkinter import X, Y, NW, YES, END

from PIL import ImageTk

import configDictTk as cd

matplotlib.use('TkAgg')

fontMainTitle = ("sans-serif 14 bold")
fontSectionTitle = ("sans-serif 12 bold")
fontRadio = ("sans-serif 11")
fontLbl = ("sans-serif 11")
fontEnt = ("sans-serif 11")
fontMenu = ("sans-serif 11")
widthMainTitle = 25
widthSectionTitle = 30
widthRowLbl = 20
widthRowEnt = 25
widthRadio = 17
widthCkBtn = 18

cmapTypes = ["STD", "LSEG", "LIST"]

# Debug dictionary
# debug1 - Print dictionary lines from loaded config file
# debug2 - Print config values at start of "Run"
# debug3 - Print values of "b" and Bscale.
# debug4 - Print Linear Segmented Colormap text file used for plot
# debug5 - Print Color List Colormap text file used for plot
debugDict = {"debug1": False,
             "debug2": False,
             "debug3": False,
             "debug4": False,
             "debug5": False}

# Color List colormap - check edge value list for mandatory initial/final
# values and increasing values across whole list
def ckEdgeVals(lst):
    # Check list for monotonically increasing values
    def ckIncVals(lst):
        fltList = [float(x) for x in lst]
        OK = np.all(np.diff(fltList) > 0.0)
        return (OK)

    def ckClose(a, b):
        if (abs(a - b) < 1e-9):
            OK = True
        else:
            OK = False
        return (OK)

    # Check for end values being 0.0 and 1.0
    if (ckClose(float(lst[0]), 0.0) is False) or \
       (ckClose(float(lst[-1]), 1.0) is False) or \
       (ckIncVals(lst) is False):
        msg = 'First/last edge value error OR values not increasing'
        print(msg)
        OK = False
    else:
        OK = True
    return (OK)


# Check Color List for proper hex, or proper named colors
def ckColorList(lst):
    # Check for digit is allowable hex
    def isHex(N):
        hexDigits = string.hexdigits
        OK = True
        for d in N:
            if d not in hexDigits:
                OK = False
                break
        return (OK)

    # Get known colors dictionary
    namedColorsDict = mc.cnames
    namedColorsList = []
    # Extract known color names from dictionary
    for k in namedColorsDict.keys():
        namedColorsList.append(k)
        # Sort the color list
        namedColorsList.sort(key=str.lower)

    # Check each digit is hex and correct number of digits
    OK = True
    for N in lst:
        # Check hex value
        if N[0] == "#":
            N = N.lstrip("#")
            if ((len(N)) != 6) or \
               (isHex(N) is False):
                msg = 'Erroneous hex number'
                print(msg)
                OK = False
        else:
            # Check named color against known colors list
            if N not in namedColorsList:
                msg = "Named color not in referenced list"
                print(msg)
                OK = False
    return(OK)


# Get data from GUI, generate potential output configuration file,
# calculate set of (x,y) points, plot data.
def fetch(entriesDict):

    # Get values from lines with two elements
    def get2Vals(inStr, typ):
        inStr = inStr.lstrip()
        nums = inStr.split(",")
        if typ == "int":
            val1 = int(nums[0])
            val2 = int(nums[1])
        elif typ == "float":
            val1 = float(nums[0])
            val2 = float(nums[1])
        else:
            print("Error processing dual entry: ", inStr)
            return(-1, -1)
        return(val1, val2)

    # Get latest values via dictionary
    niters = int(entriesDict["Iterations"].get())
    Ascale = float(entriesDict["ascale"].get())
    Bscale = float(entriesDict["bscale"].get())
    Cscale = float(entriesDict["cscale"].get())
    tweakMinMax = entriesDict["tweakMinMax"].get()
    tweakMinMaxQuotes = '"int(' + tweakMinMax.lstrip() + ')"'
    tweakMin, tweakMax = get2Vals(tweakMinMax, 'int')
    freq = float(entriesDict["freq"].get())
    a = float(entriesDict["a"].get())
    b = float(entriesDict["b"].get())
    c = float(entriesDict["c"].get())
    xyStart = entriesDict["xyStart"].get()
    xyStartQuotes = '"float(' + xyStart.lstrip() + ')"'
    x, y = get2Vals(xyStart, 'float')
    nDeg = float(entriesDict["rotate"].get())
    nRad = math.radians(nDeg)
    nDelRad = nRad/niters
    windowWidthHgt = entriesDict["windowWidthHgt"].get()
    winWidthHgtStr = '"float(' + windowWidthHgt.lstrip() + ')"'
    windowWidth, windowHeight = get2Vals(windowWidthHgt, 'float')
    pltLimPercent = float(entriesDict["pltLimPercent"].get())
    xpltMinMax = entriesDict["xpltMinMax"].get()
    xpltMinMaxQuotes = '"float(' + xpltMinMax.lstrip() + ')"'
    xpltMin, xpltMax = get2Vals(xpltMinMax, 'float')
    ypltMinMax = entriesDict["ypltMinMax"].get()
    ypltMinMaxQuotes = '"float(' + ypltMinMax.lstrip() + ')"'
    ypltMin, ypltMax = get2Vals(ypltMinMax, 'float')
    dpi = float(entriesDict["DPI"].get())
    faceColor = entriesDict["faceColor"].get().lstrip()
    dotSize = float(entriesDict["dotSize"].get())
    pStartStop = entriesDict["plotStartStop"].get()
    pStStQuotes = '"int(' + pStartStop.lstrip() + ')"'
    pStart, pStop = get2Vals(pStartStop, 'int')
    cmapStdName = entriesDict["cMapStd"].get()
    cmapLsegName = entriesDict["cMapLseg"].get()
    cmapListName = entriesDict["cMapList"].get()

    boolRawSave = saveRaw.get()
    if boolRawSave is True:
        flagRawSave = 'True'
    else:
        flagRawSave = 'False'

    boolPltLimPercent = usePltLimPercent.get()
    if boolPltLimPercent is True:
        flagPltLimPercent = 'True'
    else:
        flagPltLimPercent = 'False'

    if (debugDict["debug2"]):
        print()
        print('niters = {0:8d}'.format(niters))
        print('Ascale = {0:8.5e}'.format(Ascale))
        print('Bscale = {0:8.5e}'.format(Bscale))
        print('Cscale = {0:8.5e}'.format(Cscale))
        print('tweakMinMax = {0:20s}'.format(tweakMinMax))
        print('tweakMin = {0:8d}'.format(tweakMin))
        print('tweakMax = {0:8d}'.format(tweakMax))
        print('freq = {0:8.3f}'.format(freq))
        print('a = {0:8.3f}'.format(a))
        print('b = {0:8.3f}'.format(b))
        print('c = {0:8.3f}'.format(c))
        print('xyStart = {0:20s}'.format(xyStart))
        print('x = {0:8.3f}'.format(x))
        print('y = {0:8.3f}'.format(y))
        print('nDeg = {0:8.2f}'.format(nDeg))
        print('windowWidthHgt = {0:25s}'.format(windowWidthHgt))
        print('windowWidth  = {0:8.2f}'.format(windowWidth))
        print('windowHeight = {0:8.2f}'.format(windowHeight))
        print('flagPltLimPercent = {0:8s}'.format(flagPltLimPercent))
        print('pltLimPercent = {0:8.1f}'.format(pltLimPercent))
        print('xpltMinMax  = {0:25s}'.format(xpltMinMax))
        print('xpltMin = {0:8.2f}'.format(xpltMin))
        print('xpltMax = {0:8.2f}'.format(xpltMax))
        print('ypltMinMax  = {0:25s}'.format(ypltMinMax))
        print('yPltMin = {0:8.2f}'.format(ypltMin))
        print('yPltMax = {0:8.2f}'.format(ypltMax))
        print('dpi = {0:8.2f}'.format(dpi))
        print('dotSize = {0:8.2f}'.format(dotSize))
        print('faceColor = {0:10s}'.format(str(faceColor)))
        print('plotStartStop = {0:20s}'.format(pStartStop))
        print('plotStart = {0:8d}'.format(pStart))
        print('plotStop = {0:8d}'.format(pStop))
        print('varCmapType = {0:8s}'.format(str(varCmapType.get())))
        print('cmapStdName = {0:14s}'.format(str(cmapStdName)))
        print('cmapLseg    = {0:14s}'.format(str(cmapLsegName)))
        print('cmapList    = {0:14s}'.format(str(cmapListName)))
        print('flagRawSave = {0:8s}'.format(flagRawSave))
        print()

    # Create text template for saving configuration data file
    header = """#!/usr/bin/python3
# -*- coding: utf-8 -*-

configurationData = {
    # [Algorithm Data]
"""
    trailer = '}\n\n\n'

    nitersLine = \
        '    "ITERATIONS": ("Iterations", int(' + str(niters) + ')),\n'

    AscaleLine = \
        '    "ASCALE": ("ascale", float(' + str(Ascale) + ')),\n'

    BscaleLine = \
        '    "BSCALE": ("bscale", float(' + str(Bscale) + ')),\n'

    CscaleLine = \
        '    "CSCALE": ("cscale", float(' + str(Cscale) + ')),\n'

    tweakMinMaxLine = \
        '    "TWEAKMINMAX": ("tweakMinMax", ' + tweakMinMaxQuotes + '),\n'

    freqLine = \
        '    "FREQ": ("freq", float(' + str(freq) + ')),\n'

    aLine = \
        '    "A": ("a", float(' + str(a) + ')),\n'

    bLine = \
        '    "B": ("b", float(' + str(b) + ')),\n'

    cLine = \
        '    "C": ("c", float(' + str(c) + ')),\n'

    xyStartLine = \
        '    "XYSTART": ("xyStart", ' + xyStartQuotes + '),\n'

    nDegLine = \
        '    "ROTATE": ("rotate", float(' + str(nDeg) + ')),\n'

    txtScreen = \
        '    # [Screen Data]\n'

    windowWidHgtLine = \
        '    "WINDOWWIDTHHGT": ("windowWidthHgt", ' + winWidthHgtStr + '),\n'

    usePltLimPercentLine = \
        '    "USEPLTLIMPERCENT": "' + flagPltLimPercent + '",\n'

    tempStr = str(pltLimPercent)
    pltLimPercentLine = \
        '    "PLTLIMPERCENT": ("pltLimPercent", float(' + tempStr + ')),\n'

    xpltMinMaxLine = \
        '    "XPLTMINMAX": ("xpltMinMax", ' + xpltMinMaxQuotes + '),\n'

    ypltMinMaxLine = \
        '    "YPLTMINMAX": ("ypltMinMax", ' + ypltMinMaxQuotes + '),\n'

    dpiLine = \
        '    "DPI": ("DPI", float(' + str(dpi) + ')),\n'

    faceColorLine = \
        '    "FACECOLOR": ("faceColor", "' + str(faceColor) + '"),\n'

    dotSizeLine = \
        '    "DOTSIZE": ("dotSize", float(' + str(dotSize) + ')),\n'

    pStartStopLine = \
        '    "PLTSTARTSTOP": ("plotStartStop", ' + pStStQuotes + '),\n'

    txtCmap = \
        '    # [Color Map]\n'

    cmapTypeLine = \
        '    "CMAPTYPE": "' + str(varCmapType.get()) + '",\n'

    cmapStdLine = \
        '    "CMAPSTD": ("cMapStd", "' + str(cmapStdName) + '"),\n'

    cmapLsegLine = \
        '    "CMAPLSEG": ("cMapLseg", "' + str(cmapLsegName) + '"),\n'

    cmapListLine = \
        '    "CMAPLIST": ("cMapList", "' + str(cmapListName) + '"),\n'

    txtFileData = \
        '    # [File Data]\n'

    picBaseLine = \
        '    "PICBASE": "' + str(baseFileNames["PICBASE"]) + '",\n'

    configBaseLine = \
        '    "CONFIGBASE": "' + str(baseFileNames["CONFIGBASE"]) + '",\n'

    rawSaveLine = \
        '    "RAWSAVE": "' + flagRawSave + '",\n'

    rawBaseLine = \
        '    "RAWBASE": "' + str(baseFileNames["RAWBASE"]) + '",\n'

    fullTxt = header + nitersLine + AscaleLine + \
        BscaleLine + CscaleLine + tweakMinMaxLine + \
        freqLine + aLine + bLine + cLine + xyStartLine +  \
        nDegLine + txtScreen + windowWidHgtLine + \
        usePltLimPercentLine + pltLimPercentLine + \
        xpltMinMaxLine + ypltMinMaxLine + \
        dpiLine + faceColorLine + dotSizeLine + \
        pStartStopLine + txtCmap + cmapTypeLine + cmapStdLine + \
        cmapLsegLine + cmapListLine + txtFileData + picBaseLine + \
        configBaseLine + rawSaveLine + rawBaseLine + trailer

    datTime = datetime.datetime.now()
    datTime = datTime.strftime("%m%d%y_%H%M%S")
    title = 'Plot' + '_' + datTime

    # Create plot window
    window = tk.Toplevel()

    tk.Label(window, text=title).pack()
    f = Figure(figsize=(windowWidth, windowHeight), dpi=dpi)
    figPlot = f.add_subplot(111)

    figPlot.patch.set_facecolor(faceColor)

    # Minimize the border surrounding the plot area
    f.set_tight_layout(True)

    # Calculate next (x,y) point
    def update(x, y, a, b, c):
        sig = math.copysign(1, x)
        # x1 = y-sig*math.sqrt(abs(b*x+c))
        x1 = y-sig*math.sqrt(abs(b*x-c))
        y1 = a-x
        return x1, y1

    def ckmin(m, ck):
        if m < ck:
            return m
        else:
            return ck

    def ckmax(m, ck):
        if m > ck:
            return m
        else:
            return ck

    # Save image file and configuration data file. Include min/max data
    # in the configuration data file save.
    def Save():
        picBase = baseFileNames["PICBASE"]
        picFile = picBase + "_" + datTime + ".png"
        FigureCanvasTkAgg.print_png(canvas, picFile)

        configBase = baseFileNames["CONFIGBASE"]
        outFile = configBase + '_' + datTime + '.py'

        xminStr = '# xmin = {0:8.1f}\n'.format(xmin)
        xmaxStr = '# xmax = {0:8.1f}\n'.format(xmax)
        yminStr = '# ymin = {0:8.1f}\n'.format(ymin)
        ymaxStr = '# ymax = {0:8.1f}'.format(ymax)
        minmaxStr = xminStr + xmaxStr + yminStr + ymaxStr

        with open(outFile, "w") as outfile:
            outfile.write(fullTxt)
            outfile.write(minmaxStr)
            outfile.write("\n")

        # Conditionally save raw x-y data
        flag = saveRaw.get()
        if flag is True:
            rawfileBase = baseFileNames["RAWBASE"]
            rawFile = rawfileBase + '_' + datTime + '.txt'
            np.savetxt(rawFile, np.array([xx, yy]).T, fmt='%+2.12e')

    if (debugDict["debug3"]):
        print('\nbscale = {0:8.5e}\n'.format(Bscale))

    # Initialize min/max values
    lgPos = 1.0E9
    lgNeg = -lgPos

    xmin = lgPos
    xmax = lgNeg
    ymin = lgPos
    ymax = lgNeg

    # Loop over specified number of iterations
    xx = [x]
    yy = [y]

    # Limit percent of iterations to calculate
    flag = usePltLimPercent.get()
    if flag is True:
        fract = pltLimPercent/100.0
        niters = int(fract*niters)

    for i in range(niters):
        # Hop to next ordered pair
        x, y = update(x, y, a, b, c)

        # Conditionally rotate point to new (x,y) location
        if abs(nDeg) > 0.0:
            dist = math.sqrt(x*x + y*y)    # Distance from origin to (x,y)
            xyAng = math.atan2(y, x)        # Angle from pos x-axis to (x,y)
            ttlAng = xyAng + nDelRad
            x = dist*math.cos(ttlAng)
            y = dist*math.sin(ttlAng)

        # Populate x- and y-arrays
        if i >= pStart and i <= pStop:
            xx.append(x)
            yy.append(y)

        # Perform a,b,c tweaking.
        if i >= tweakMin and i <= tweakMax:
            # Conditionally apply sine wave to "b"
            aa = 2*math.pi*freq*i/niters
            if abs(aa) < 1.0e-15:
                b = b + Bscale*b
            else:
                b = b + Bscale*b*math.sin(aa)
            a = a + Ascale*a
            c = c + Cscale*c

        if (debugDict["debug3"]):
            print('b = {0:11.8e}'.format(b))

        xxt = np.arange(len(xx))

        # Collect min/max x and y. Use to adjust window in future run
        xmin = ckmin(xmin, x)
        xmax = ckmax(xmax, x)
        ymin = ckmin(ymin, y)
        ymax = ckmax(ymax, y)

    # Output min/max x and y values to screen.
    print('niters = {0:<8d}'.format(niters))
    print('xmin = {0:8.1f}'.format(xmin))
    print('xmax = {0:8.1f}'.format(xmax))

    print('ymin = {0:8.1f}'.format(ymin))
    print('ymax = {0:8.1f}'.format(ymax))

    # Set plot window limits
    flag = usePltLimPercent.get()
    if flag is True:
        fract = pltLimPercent/100.0
        figPlot.set_xlim([fract*xmin, fract*xmax])
        figPlot.set_ylim([fract*ymin, fract*ymax])
    else:
        figPlot.set_xlim([xpltMin, xpltMax])
        figPlot.set_ylim([ypltMin, ypltMax])

    figPlot.xaxis.set_visible(False)
    figPlot.yaxis.set_visible(False)

    # Generate plot image
    if (varCmapType.get() == "STD"):
        # Plot using Standard colormap
        figPlot.scatter(xx, yy, s=dotSize, c=xxt, cmap=cmapStdName)
    elif (varCmapType.get() == "LSEG"):
        # Plot using custom Linear Segmented colormap
        divisor = 256.0
        colorFile = cmapLsegName
        colorList = []

        if (debugDict["debug4"]):
            print("LSEG colorFile: ", colorFile)

        ff = open(colorFile, "r")
        line = ff.readline()
        # Parse text file
        while (line != ""):
            if (debugDict["debug4"]):
                print(line.rstrip())

            # Check for comment line, or blank line
            if (line.startswith('#')) or (len(line.split()) == 0):
                line = ff.readline()
                continue
            else:
                colorLine = eval(line)
                scaled = (colorLine[0], [x/divisor for x in colorLine[1]])
                colorList.append(scaled)

            line = ff.readline()
        ff.close()

        normalize = mc.Normalize(vmin=0, vmax=len(xx))
        cmap = mc.LinearSegmentedColormap.from_list("", colorList)
        figPlot.scatter(xx, yy, s=dotSize, c=normalize(xxt), cmap=cmap)
    elif (varCmapType.get() == "LIST"):
        # Plot using custom Color List colormap
        if (debugDict["debug5"]):
            print("LIST colorFile: ", cmapListName)

        with open(cmapListName, "r") as inFile:
            lines = []
            for line in inFile:
                if (debugDict["debug5"]):
                    print(line.rstrip())

                # Discard lines starting with #, or zero-length lines
                if (line.startswith('#')) or (len(line.split()) == 0):
                    continue
                else:
                    line = line.rstrip("\n")
                    lines.append(line)
        # Parse text file into Edge List and Color List
        for line in lines:
            lineSpl = line.split('=')
            if (lineSpl[0].strip() == 'edgeList'):
                edgeListStr = lineSpl[1].strip()
                edgeListStr = edgeListStr.strip('][').replace(",", "").split()
                edgeList = [float(x) for x in edgeListStr]
            elif (lineSpl[0].strip() == 'rgbList'):
                rgbListStr = lineSpl[1].strip()
                rgbListStr = rgbListStr.strip('][').replace(",", "").split()
            else:
                continue

        # Check Color List for proper hex format, and named colors
        rgbOK = ckColorList(rgbListStr)
        if rgbOK is False:
            print("Plotting image: Color List error")
            return
        # Check Edge List initial/final values and increasing values
        edgeOK = ckEdgeVals(edgeList)
        if edgeOK is False:
            print("Plotting image: Edge List error")
            return

        # Adapt Edge List to data array
        bounds = [i*(len(xx)) for i in edgeList]
        cmap = mpl.colors.ListedColormap(rgbListStr)
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N, clip=True)

        figPlot.scatter(xx, yy, s=dotSize, c=xxt, cmap=cmap, norm=norm)
    else:
        print("Colormap type not recognized. Exiting.")
        return

    # Create canvas to hold plot
    canvas = FigureCanvasTkAgg(f, master=window)
    canvas.show()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    # Create image Save button
    btnSave = tk.Button(master=window, text='Save', command=Save)
    btnSave.pack(side=RIGHT)

    toolbar = NavigationToolbar2TkAgg(canvas, window)
    toolbar.update()

    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
    canvas.show()


# Make initial GUI form
def makeform(root):
    global entITERATIONS, entASCALE, entBSCALE, entCSCALE, entTWEAKMINMAX
    global entFREQ, entA, entB, entC, entXYSTART, entROTATE, entWINDOWWIDTHHGT
    global entPLTLIMPERCENT, entXPLTMINMAX, entYPLTMINMAX, entDPI, entDOTSIZE
    global entFACECOLOR, entPLTSTARTSTOP, entCMAPSTD

    def setRow(master, namedTup, entriesDict):
        row = tk.Frame(master)
        row.pack(side=TOP, fill=X, pady=1)
        lbl = tk.Label(row, width=widthRowLbl, text=' '+namedTup.label,
                       anchor=tk.W, font=fontLbl)
        lbl.pack(side=LEFT, fill=X)
        ent = tk.Entry(row, width=widthRowEnt, font=fontEnt)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        ent.insert(0, ' '+str(namedTup.val))
        entriesDict[namedTup.label] = ent

        return(row, ent, entriesDict)

    def setRowDual(master, label, valStr, entriesDict):
        row = tk.Frame(master)
        row.pack(side=TOP, fill=X, pady=1)
        lbl = tk.Label(row, width=widthRowLbl, text=' '+label,
                       anchor=tk.W, font=fontLbl)
        lbl.pack(side=LEFT, fill=X)
        ent = tk.Entry(row, width=widthRowEnt, font=fontEnt)
        ent = tk.Entry(row, width=widthRowEnt, font=fontEnt)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        ent.insert(0, ' '+str(valStr))
        entriesDict[label] = ent
        return(row, ent, entriesDict)

    entryRow = namedtuple("entryRow", ["label", "val"])
    entriesDict = {}

    # Configuration Data 
    lblFrame1 = tk.Frame(root).pack(side=TOP)
    txt = '**Chaotic Spokes**'
    lbl = tk.Label(lblFrame1, width=widthMainTitle, text=txt)
    lbl.config(font=fontMainTitle)
    lbl.pack(side=TOP)

    # Algorithm Data 
    txt = '*Algorithm Data*'
    lbl = tk.Label(lblFrame1, width=widthSectionTitle, text=txt, anchor='w')
    lbl.config(font=fontSectionTitle)
    lbl.pack(side=TOP)

    rowFrame1 = tk.Frame(root)
    rowFrame1.pack(side=TOP, expand=True)

    # Number of iterations
    namedTup = entryRow._make(cd.configurationData["ITERATIONS"])
    rowITERATIONS, entITERATIONS, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowITERATIONS.pack(side=TOP)

    # Tweaking factor for <a> algorithm parameter
    namedTup = entryRow._make(cd.configurationData["ASCALE"])
    rowASCALE, entASCALE, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowASCALE.pack(side=TOP)

    # Tweaking factor for <b> algorithm parameter
    namedTup = entryRow._make(cd.configurationData["BSCALE"])
    rowBSCALE, entBSCALE, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowBSCALE.pack(side=TOP)

    # Tweaking factor for <c> algorithm parameter
    namedTup = entryRow._make(cd.configurationData["CSCALE"])
    rowCSCALE, entCSCALE, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowCSCALE.pack(side=TOP)

    # Minumum/maximum iterations to apply scaling/tweaking factor
    namedTup = entryRow._make(cd.configurationData["TWEAKMINMAX"])
    rowLabel = str(namedTup.label)
    rowVals = str(namedTup.val)
    ndx = rowVals.find("(")
    valStr = rowVals[ndx+1:-1]
    rowTWEAKMINMAX, entTWEAKMINMAX, entriesDict = \
        setRowDual(rowFrame1, rowLabel, valStr, entriesDict)
    rowTWEAKMINMAX.pack(side=TOP)

    # Frequency (hz) of sinusoidal adjustment of <b> parameter
    namedTup = entryRow._make(cd.configurationData["FREQ"])
    rowFREQ, entFREQ, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowFREQ.pack(side=TOP)

    # Main algorithm <a> parameter
    namedTup = entryRow._make(cd.configurationData["A"])
    rowA, entA, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowA.pack(side=TOP)

    # Main algorithm <b> parameter
    namedTup = entryRow._make(cd.configurationData["B"])
    rowB, entB, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowB.pack(side=TOP)

    # Main algorithm <c> parameter
    namedTup = entryRow._make(cd.configurationData["C"])
    rowC, entC, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowC.pack(side=TOP)

    # Starting values - x coordinate, y coordinate
    namedTup = entryRow._make(cd.configurationData["XYSTART"])
    rowLabel = str(namedTup.label)
    rowVals = str(namedTup.val)
    ndx = rowVals.find("(")
    valStr = rowVals[ndx+1:-1]
    rowXYSTART, entXYSTART, entriesDict = \
        setRowDual(rowFrame1, rowLabel, valStr, entriesDict)
    rowXYSTART.pack(side=TOP)

    # (x,y) rotation angle (deg)
    namedTup = entryRow._make(cd.configurationData["ROTATE"])
    rowROTATE, entROTATE, entriesDict = \
        setRow(rowFrame1, namedTup, entriesDict)
    rowROTATE.pack(side=TOP)

    lblFrame2 = tk.Frame(root).pack(side=TOP)
    txt = '*Screen Data*'
    lbl = tk.Label(lblFrame2, width=widthSectionTitle, text=txt, anchor='w')
    lbl.config(font=fontSectionTitle)
    lbl.pack(side=TOP)

    rowFrame2 = tk.Frame(root)
    rowFrame2.pack(side=TOP)

    # Plot window width/height, inches
    namedTup = entryRow._make(cd.configurationData["WINDOWWIDTHHGT"])
    rowLabel = str(namedTup.label)
    rowVals = str(namedTup.val)
    ndx = rowVals.find("(")
    valStr = rowVals[ndx+1:-1]
    rowWINDOWWIDTHHGT, entWINDOWWIDTHHGT, entriesDict = \
        setRowDual(rowFrame2, rowLabel, valStr, entriesDict)
    rowWINDOWWIDTHHGT.pack(side=TOP)

    rowFrame3 = tk.Frame(root)
    rowFrame3.pack(side=TOP, anchor=tk.W)

    # Checkbox - Use % of min/max plot limits
    limCkBtn = tk.Checkbutton(
                    rowFrame3, text=" UsePltLim %",
                    variable=usePltLimPercent, onvalue=True,
                    offvalue=False, font=fontLbl, anchor=tk.W,
                    width=widthCkBtn)
    limCkBtn.pack(side=LEFT)

    flagPltLimPercent = cd.configurationData["USEPLTLIMPERCENT"]
    if (flagPltLimPercent.upper() == 'TRUE'):
        usePltLimPercent.set(True)
    else:
        usePltLimPercent.set(False)

    rowFrame4 = tk.Frame(root)
    rowFrame4.pack(side=TOP)

    # Plot limits, percent of min/max values
    namedTup = entryRow._make(cd.configurationData["PLTLIMPERCENT"])
    rowPLTLIMPERCENT, entPLTLIMPERCENT, entriesDict = \
        setRow(rowFrame4, namedTup, entriesDict)
    rowPLTLIMPERCENT.pack(side=TOP)

    # MinMax x value to plot, pixels
    namedTup = entryRow._make(cd.configurationData["XPLTMINMAX"])
    rowLabel = str(namedTup.label)
    rowVals = str(namedTup.val)
    ndx = rowVals.find("(")
    valStr = rowVals[ndx+1:-1]
    rowXPLTMINMAX, entXPLTMINMAX, entriesDict = \
        setRowDual(rowFrame4, rowLabel, valStr, entriesDict)
    rowXPLTMINMAX.pack(side=TOP)

    # MinMax y value to plot, pixels
    namedTup = entryRow._make(cd.configurationData["YPLTMINMAX"])
    rowLabel = str(namedTup.label)
    rowVals = str(namedTup.val)
    ndx = rowVals.find("(")
    valStr = rowVals[ndx+1:-1]
    rowYPLTMINMAX, entYPLTMINMAX, entriesDict = \
        setRowDual(rowFrame4, rowLabel, valStr, entriesDict)
    rowYPLTMINMAX.pack(side=TOP)

    # Figure resolution, dots per inch
    namedTup = entryRow._make(cd.configurationData["DPI"])
    rowDPI, entDPI, entriesDict = \
        setRow(rowFrame4, namedTup, entriesDict)
    rowDPI.pack(side=TOP)

    # Scatter plot dot size in points**2
    namedTup = entryRow._make(cd.configurationData["DOTSIZE"])
    rowDOTSIZE, entDOTSIZE, entriesDict = \
        setRow(rowFrame4, namedTup, entriesDict)
    rowDOTSIZE.pack(side=TOP)

    # Figure background color name
    namedTup = entryRow._make(cd.configurationData["FACECOLOR"])
    rowFACECOLOR, entFACECOLOR, entriesDict = \
        setRow(rowFrame4, namedTup, entriesDict)
    rowFACECOLOR.pack(side=TOP)

    # Iteration to start/stop plotting of data
    namedTup = entryRow._make(cd.configurationData["PLTSTARTSTOP"])
    rowLabel = str(namedTup.label)
    rowVals = str(namedTup.val)
    ndx = rowVals.find("(")
    valStr = rowVals[ndx+1:-1]
    rowPLTSTARTSTOP, entPLTSTARTSTOP, entriesDict = \
        setRowDual(rowFrame4, rowLabel, valStr, entriesDict)
    rowPLTSTARTSTOP.pack(side=TOP)

    # CMAP radio buttons variable
    typeStr = cd.configurationData["CMAPTYPE"]
    varCmapType.set(typeStr)

    # Save Raw Data checkbox
    flagRaw = cd.configurationData["RAWSAVE"]
    if (flagRaw.upper() == 'TRUE'):
        saveRaw.set(True)
    else:
        saveRaw.set(False)

    # Radio button for standard cmap
    rowRADIOSTD = tk.Frame(rowFrame4)
    rowRADIOSTD.pack(side=TOP, fill=X, pady=2)
    radioSTD = tk.Radiobutton(
          rowRADIOSTD, text=" Standard",
          variable=varCmapType, value="STD",
          font=fontRadio, anchor=tk.W, width=widthRadio)
    radioSTD.pack(side=LEFT)

    # Standard color map name
    namedTup = entryRow._make(cd.configurationData["CMAPSTD"])
    ent = tk.Entry(rowRADIOSTD, width=widthRowEnt, font=fontEnt)
    ent.pack(side=RIGHT, expand=YES, fill=X)
    ent.insert(0, namedTup.val)
    entriesDict[namedTup.label] = ent
    entCMAPSTD = ent

    # Radio button for Linear Segmented custom cmap
    rowRADIOLSEG = tk.Frame(rowFrame4)
    rowRADIOLSEG.pack(side=TOP, fill=X, pady=2)
    radioLSEG = tk.Radiobutton(
                       rowRADIOLSEG,
                       text=" LinearSegmented", variable=varCmapType,
                       value="LSEG", font=fontRadio,
                       anchor=tk.W, width=widthRadio)
    radioLSEG.pack(side=LEFT)

    # Linear Segmented custom color map name
    namedTup = entryRow._make(cd.configurationData["CMAPLSEG"])
    ent = tk.Entry(rowRADIOLSEG, width=widthRowEnt, font=fontEnt)
    ent.pack(side=RIGHT, expand=YES, fill=X)
    ent.insert(0, namedTup.val)
    entriesDict[namedTup.label] = ent
    root.entCMAPLSEG = ent

    # Radio button for Color List custom cmap
    rowRADIOLIST = tk.Frame(rowFrame4)
    rowRADIOLIST.pack(side=TOP, fill=X, pady=2)
    radioLIST = tk.Radiobutton(
                       rowRADIOLIST,
                       text=" Color List", variable=varCmapType,
                       value="LIST", font=fontRadio,
                       anchor=tk.W, width=widthRadio)
    radioLIST.pack(side=LEFT)

    # Linear Segmented custom color map name
    namedTup = entryRow._make(cd.configurationData["CMAPLIST"])
    ent = tk.Entry(rowRADIOLIST, width=widthRowEnt, font=fontEnt)
    ent.pack(side=RIGHT, expand=YES, fill=X)
    ent.insert(0, namedTup.val)
    entriesDict[namedTup.label] = ent
    root.entCMAPLIST = ent

    picBase = cd.configurationData["PICBASE"]
    baseFileNames["PICBASE"] = picBase

    configBase = cd.configurationData["CONFIGBASE"]
    baseFileNames["CONFIGBASE"] = configBase

    rawBase = cd.configurationData["RAWBASE"]
    baseFileNames["RAWBASE"] = rawBase

    return (entriesDict)


# Load and parse Configuration file
def getConfigFile():
    # Parse line from input file
    def getVal(tup, numerical=True):
        tupSplit = tup.split(",", 1)
        str1 = tupSplit[1]
        valStr = str1[0:-1]
        if numerical is True:
            valStr = str(eval(valStr))
        return (valStr)

    # Load/read Configuration file
    def configFileReader():
        configDict = OrderedDict()
        name = filedialog.askopenfilename(
                initialdir=".",
                title="Select file",
                filetypes=(("Config files", "*.py"), ("all files", "*.*")))
        if name is None:
            return(None)
        else:
            with open(name, 'r') as inFile:
                for line in inFile:
                    line = line.rstrip()
                    if (line.find("#") == -1) and (line.find(":") != -1):
                        key, value = line.strip().split(':')
                        configDict[key.strip('"')] = value.rstrip(",")
        if (debugDict["debug1"]):
            for key in configDict:
                print(key, configDict[key])
        return (configDict)

    configDict = configFileReader()
    if configDict is None:
        return

    tup = configDict["ITERATIONS"]
    newVal = getVal(tup)
    entITERATIONS.delete(0, END)
    entITERATIONS.insert(0, newVal)

    tup = configDict["ASCALE"]
    newVal = getVal(tup)
    entASCALE.delete(0, END)
    entASCALE.insert(0, newVal)

    tup = configDict["BSCALE"]
    newVal = getVal(tup)
    entBSCALE.delete(0, END)
    entBSCALE.insert(0, newVal)

    tup = configDict["CSCALE"]
    newVal = getVal(tup)
    entCSCALE.delete(0, END)
    entCSCALE.insert(0, newVal)

    tup = configDict["TWEAKMINMAX"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    ndx = newVal.find("(")
    newVal = newVal[ndx+1:-1]
    entTWEAKMINMAX.delete(0, END)
    entTWEAKMINMAX.insert(0, newVal)

    tup = configDict["FREQ"]
    newVal = getVal(tup)
    entFREQ.delete(0, END)
    entFREQ.insert(0, newVal)

    tup = configDict["A"]
    newVal = getVal(tup)
    entA.delete(0, END)
    entA.insert(0, newVal)

    tup = configDict["B"]
    newVal = getVal(tup)
    entB.delete(0, END)
    entB.insert(0, newVal)

    tup = configDict["C"]
    newVal = getVal(tup)
    entC.delete(0, END)
    entC.insert(0, newVal)

    tup = configDict["XYSTART"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    ndx = newVal.find("(")
    newVal = newVal[ndx+1:-1]
    entXYSTART.delete(0, END)
    entXYSTART.insert(0, newVal)

    tup = configDict["ROTATE"]
    newVal = getVal(tup)
    entROTATE.delete(0, END)
    entROTATE.insert(0, newVal)

    tup = configDict["WINDOWWIDTHHGT"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    ndx = newVal.find("(")
    newVal = newVal[ndx+1:-1]
    entWINDOWWIDTHHGT.delete(0, END)
    entWINDOWWIDTHHGT.insert(0, newVal)

    flagPltLimPercent = configDict["USEPLTLIMPERCENT"]
    flagPltLimPercent = flagPltLimPercent.strip().strip('"')
    if (flagPltLimPercent.upper() == 'TRUE'):
        usePltLimPercent.set(True)
    else:
        usePltLimPercent.set(False)

    tup = configDict["PLTLIMPERCENT"]
    newVal = getVal(tup)
    entPLTLIMPERCENT.delete(0, END)
    entPLTLIMPERCENT.insert(0, newVal)

    tup = configDict["XPLTMINMAX"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    ndx = newVal.find("(")
    newVal = newVal[ndx+1:-1]
    entXPLTMINMAX.delete(0, END)
    entXPLTMINMAX.insert(0, newVal)

    tup = configDict["YPLTMINMAX"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    ndx = newVal.find("(")
    newVal = newVal[ndx+1:-1]
    entYPLTMINMAX.delete(0, END)
    entYPLTMINMAX.insert(0, newVal)

    tup = configDict["DPI"]
    newVal = getVal(tup)
    entDPI.delete(0, END)
    entDPI.insert(0, newVal)

    tup = configDict["FACECOLOR"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    entFACECOLOR.delete(0, END)
    entFACECOLOR.insert(0, newVal)

    tup = configDict["DOTSIZE"]
    newVal = getVal(tup)
    entDOTSIZE.delete(0, END)
    entDOTSIZE.insert(0, newVal)

    tup = configDict["PLTSTARTSTOP"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    ndx = newVal.find("(")
    newVal = newVal[ndx+1:-1]
    entPLTSTARTSTOP.delete(0, END)
    entPLTSTARTSTOP.insert(0, newVal)

    strTemp = configDict["CMAPTYPE"]
    strTemp = strTemp.strip().strip('"')
    if strTemp in cmapTypes:
        varCmapType.set(strTemp)
    else:
        print("Invalid CMAPTYPE from config file. Defaulting to STD")
        varCmapType.set("STD")

    tup = configDict["CMAPSTD"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    entCMAPSTD.delete(0, END)
    entCMAPSTD.insert(0, newVal)

    tup = configDict["CMAPLSEG"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    root.entCMAPLSEG.delete(0, END)
    root.entCMAPLSEG.insert(0, newVal)

    tup = configDict["CMAPLIST"]
    newVal = getVal(tup, False)
    newVal = newVal.strip().strip('"')
    root.entCMAPLIST.delete(0, END)
    root.entCMAPLIST.insert(0, newVal)

    picBase = configDict["PICBASE"]
    picBase = picBase.strip().strip('"')
    baseFileNames["PICBASE"] = picBase

    configBase = configDict["CONFIGBASE"]
    configBase = configBase.strip().strip('"')
    baseFileNames["CONFIGBASE"] = configBase

    flagRaw = configDict["RAWSAVE"]
    flagRaw = flagRaw.strip().strip('"')
    if (flagRaw.upper() == 'TRUE'):
        saveRaw.set(True)
    else:
        saveRaw.set(False)

    rawBase = configDict["RAWBASE"]
    rawBase = rawBase.strip().strip('"')
    baseFileNames["RAWBASE"] = rawBase


# Get Linear Segmented colormap definition file name
def getLinearSegCMAP():
    root.cmFilePath = filedialog.askopenfilename(
                initialdir=".",
                title="Select file",
                filetypes=(("Linear Segmented colormap files", "*.cmS"),
                           ("all files", "*.*")))
    if (root.cmFilePath):
        root.cmFileName = os.path.basename(root.cmFilePath)

        root.entCMAPLSEG.delete(0, END)
        root.entCMAPLSEG.insert(0, root.cmFileName)
        varCmapType.set("LSEG")

    else:
        return


# Get Color List colormap definition file name
def getColorListCMAP():
    root.cmFilePath = filedialog.askopenfilename(
                initialdir=".",
                title="Select file",
                filetypes=(("Color List colormap files", "*.cmL"),
                           ("all files", "*.*")))
    if (root.cmFilePath):
        root.cmFileName = os.path.basename(root.cmFilePath)

        root.entCMAPLIST.delete(0, END)
        root.entCMAPLIST.insert(0, root.cmFileName)
        varCmapType.set("LIST")

    else:
        return


# Various images/text files from the Help menu
def hopImage():
    makeImage("./Support_ChaoticSpokes/Hopalong1.png")


def spokesImage1():
    makeImage("./Support_ChaoticSpokes/Spokes1.png")


def spokesImage2():
    makeImage("./Support_ChaoticSpokes/Spokes2.png")


def spokesImage3():
    makeImage("./Support_ChaoticSpokes/Spokes3.png")


def spokesImage4():
    makeImage("./Support_ChaoticSpokes/Spokes4.png")


def spokesImage5():
    makeImage("./Support_ChaoticSpokes/Spokes5.png")


def overviewPg1():
    makeImage("./Support_ChaoticSpokes/Overview_1.png")


def overviewPg2():
    makeImage("./Support_ChaoticSpokes/Overview_2.png")


# Standard Colormap Images
def loadStdColormaps1():
    makeImage("./Support_ChaoticSpokes/colorMaps_1.png")


def loadStdColormaps2():
    makeImage("./Support_ChaoticSpokes/colorMaps_2.png")


# Custom Colormap Examples
def loadCustColormaps1():
    makeImage("./Support_ChaoticSpokes/customColormaps_1.png")


# Load/display Help text
def configHelpTxt():
    configHelpWindow = tk.Toplevel()
    tk.Label(configHelpWindow, text="Configuration Data Help").pack()

    txtBox = tk.Text(configHelpWindow, height=50, width=88, padx=20)
    fileHandle = open('./Support_ChaoticSpokes/help_ver_1_0.txt', 'r')
    txt = fileHandle.read()  # Read the file to a variable
    fileHandle.close()

    txtBox.insert(0.0, txt)  # Insert the text into the text widget
    txtBox.config(state=DISABLED)  # Disable user modifications

    vbar = tk.Scrollbar(configHelpWindow, orient=VERTICAL)
    vbar.pack(side=RIGHT, fill=Y)
    vbar.config(command=txtBox.yview)
    txtBox.config(yscrollcommand=vbar.set)
    txtBox.pack(expand=1, fill=BOTH)  # Show the text widget


# Load display About file
def aboutTxt():
    aboutWindow = tk.Toplevel()
    winWidth = 700
    winHeight = 400

    posRight = int(aboutWindow.winfo_screenwidth()/2 - winWidth/2)
    posDown = int(aboutWindow.winfo_screenheight()/3 - winHeight/2)
    aboutWindow.geometry("+{}+{}".format(posRight, posDown))

    # Add thumbnail to About window
    txtBox1 = tk.Text(aboutWindow, height=15, width=30, bg='black')
    photo = tk.PhotoImage(file='./Support_ChaoticSpokes/aboutImg.png')
    txtBox1.image_create(tk.END, image=photo)
    txtBox1.pack(anchor='nw', side=LEFT)
    txtBox1.config(state=DISABLED)
    # Attach photo to text box since photo is a local object
    # that gets garbage collected
    txtBox1.image = photo

    # Insert version and history text.
    titleTxt = "    **CHAOTIC SPOKES **\n"
    txtBox2 = tk.Text(aboutWindow, height=25, width=75, padx=10)
    txtBox2.tag_configure('titleFont', font=('Liberation Serif', 20, 'bold'))
    scroll = tk.Scrollbar(aboutWindow, command=txtBox2.yview)
    txtBox2.configure(yscrollcommand=scroll.set)
    txtBox2.pack(side=LEFT, anchor='nw')

    scroll.pack(side=RIGHT, fill=tk.Y)
    txtBox2.insert(tk.END, titleTxt, 'titleFont')

    fileHandle = open('./Support_ChaoticSpokes/aboutText.txt', 'r')
    aboutText = fileHandle.read()  # Read the file to a variable
    fileHandle.close()

    txtBox2.tag_configure('textFont', font=('Liberation Serif', 12))
    txtBox2.insert(tk.END, aboutText, 'textFont')
    txtBox2.config(state=DISABLED)


# General purpose display for Help images
def makeImage(img):
    img = ImageTk.PhotoImage(file=img)
    top = tk.Toplevel()
    wth = img.width()
    hgt = img.height()
    x = 500
    y = 50
    top.geometry('%dx%d+%d+%d' % (wth, hgt, x, y))
    frame = tk.Frame(top, bd=0)
    frame.pack()
    canvas = tk.Canvas(frame, bd=0, width=wth, height=hgt)
    canvas.pack(side=TOP, fill=BOTH, expand=0)
    canvas.create_image(0, 0, image=img, anchor=NW)
    # Following prevents image garbage collection after return
    # which allows display of the image.
    canvas.img = img

if __name__ == '__main__':
    # Get any command line arguments
    narg = len(sys.argv)

    if narg > 1:
        for k in range(1, narg):
            if sys.argv[k] in debugDict:
                debugDict[sys.argv[k]] = True
            else:
                print('Unrecognized command line arg: ', sys.argv[k])
                print('Exiting....')
                sys.exit()

    root = tk.Tk()
    root.title("Chaotic Spokes")
    root.geometry("+80+50")
    saveRaw = tk.BooleanVar()
    baseFileNames = {}
    usePltLimPercent = tk.BooleanVar()
    varCmapType = tk.StringVar()

    # Build/display top-level GUI
    entsDict = makeform(root)
    root.bind('<Return>', (lambda event, ed=entsDict: fetch(ed)))
    actionFrame = tk.Frame(root)
    rawCkBtn = tk.Checkbutton(
        actionFrame, text=' SaveRaw',
        variable=saveRaw, onvalue=True, offvalue=False,
        font=fontLbl, anchor=tk.W, width=widthCkBtn)
    rawCkBtn.pack(side=LEFT, padx=2, pady=2)
    btnQuit = tk.Button(actionFrame, text='Quit', command=root.quit)
    btnQuit.pack(side=RIGHT, padx=2, pady=2)
    btnRun = tk.Button(
        actionFrame, text='Run',
        command=(lambda ed=entsDict: fetch(ed)))
    btnRun.pack(side=RIGHT, padx=2, pady=2)
    actionFrame.pack(side=LEFT)

    # Define menubar
    menubar = tk.Menu(root)

    # Load menu
    loadMenu = tk.Menu(menubar, tearoff=False)
    configMenu = tk.Menu(loadMenu, tearoff=False)
    colormapMenu = tk.Menu(loadMenu, tearoff=False)

    menubar.add_cascade(label="Load", font=fontMenu, menu=loadMenu)
    # Load configuration data file
    loadMenu.add_command(
        label="Config", font=fontMenu,
        command=getConfigFile)
    # Load custom colormap name
    loadCMAP_Menu = tk.Menu(tearoff=False)
    loadMenu.add_cascade(
        label="Custom CMAP File", font=fontMenu,
        menu=loadCMAP_Menu)
    loadCMAP_Menu.add_command(
        label="LinearSegmented", font=fontMenu,
        command=getLinearSegCMAP)
    loadCMAP_Menu.add_command(
        label="ColorList",
        font=fontMenu,
        command=getColorListCMAP)

    # Help menu
    helpmenu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Help", font=fontMenu, menu=helpmenu)

    # Program overview
    overviewMenu = tk.Menu(tearoff=False)
    helpmenu.add_cascade(label="Overview", font=fontMenu, menu=overviewMenu)
    overviewMenu.add_command(label="Pg 1", font=fontMenu, command=overviewPg1)
    overviewMenu.add_command(label="Pg 2", font=fontMenu, command=overviewPg2)

    # Image gallery
    galleryMenu = tk.Menu(tearoff=False)
    helpmenu.add_cascade(label="Gallery", font=fontMenu, menu=galleryMenu)
    galleryMenu.add_command(label="Hopalong", font=fontMenu, command=hopImage)
    galleryMenu.add_command(
        label="Spokes_1",
        font=fontMenu,
        command=spokesImage1)
    galleryMenu.add_command(
        label="Spokes_2",
        font=fontMenu,
        command=spokesImage2)
    galleryMenu.add_command(
        label="Spokes_3",
        font=fontMenu,
        command=spokesImage3)
    galleryMenu.add_command(
        label="Spokes_4",
        font=fontMenu,
        command=spokesImage4)
    galleryMenu.add_command(
        label="Spokes_5",
        font=fontMenu,
        command=spokesImage5)

    # Configuration data file details
    helpmenu.add_command(
        label="Config Info",
        font=fontMenu,
        command=configHelpTxt)

    # Colormap images
    cmapMenu = tk.Menu(tearoff=False)
    helpmenu.add_cascade(
        label="Colormaps",
        font=fontMenu,
        menu=cmapMenu)
    cmapMenu.add_command(
        label="Pg 1",
        font=fontMenu,
        command=loadStdColormaps1)
    cmapMenu.add_command(
        label="Pg 2",
        font=fontMenu,
        command=loadStdColormaps2)
    cmapMenu.add_command(
        label="Pg 3",
        font=fontMenu,
        command=loadCustColormaps1)

    helpmenu.add_command(label="About", font=fontMenu, command=aboutTxt)

    # Main loop
    root.config(menu=menubar)
    root.mainloop()
