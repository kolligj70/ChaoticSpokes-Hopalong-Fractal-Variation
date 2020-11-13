#!/usr/bin/python3
"""
This program was originally designed to manipulate raw data files generated
by the ChaoticSpokesTk.py program. However, the program can load and plot any 
two-column (x,y) data file and plot/colorize the data. 
"""
import os
import sys
import string

import tkinter as tk
from tkinter import filedialog

import matplotlib as mpl
import matplotlib.colors as mc

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
except ImportError:
    from matplotlib.backends.backend_tkagg import \
            NavigationToolbar2Tk as NavigationToolbar2TkAgg

from PIL import ImageTk

import numpy as np

import rawPlotConfig as xfig

# Static configuration data
dpi = xfig.dpi
faceColor = xfig.faceColor
windowWidth = xfig.windowWidth
windowHeight = xfig.windowHeight
xtraXlim = xfig.xtraXlim
xtraYlim = xfig.xtraYlim
defaultStart = xfig.pltStart
defaultStop = xfig.pltStop
defaultDotSize = xfig.dotSize

entryWidth = 15
maxX = 900

fontMainTitle = ("sans-serif 14 bold")
fontLbl = ("sans-serif 12")
fontEnt = ("sans-serif 12")
fontRadio = ("sans-serif 12")
fontMenu = ("sans-serif 13")
fontText = ("sans-serif 12")
fontFixed = ("times 13")

widthRowLbl = 24
widthRowEnt = 40
widthRadio = 21
widthEditBox = 40
heightEditBox = 20

fields = " Raw File Name", " Plot Start", " Plot Stop", " Dot Size", \
         " Standard CMAP", " LinearSegmented CMAP", "ColorList CMAP"
entries = []
entNdx = {'RAW': 0, 'START': 1, 'STOP': 2, 'DOT': 3, 'STD': 4,
          'CUSTLSEG': 5, 'CUSTLIST': 6}

# debug1 - Print first/last rows of loaded raw data file.
# debug2 - Print the custom colormap file lines (when set by radio button)
# debug3 - Print the first/last x-y pair defined by Plot Start/Stop
debugDict = {"debug1": False,
             "debug2": False,
             "debug3": False}


def makeForm(root):
    ipadx = 2
    ipady = 2
    padx = 2
    pady = 2
    global fields, entries
    bgnd = 'snow2'

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=2)

    txt = '**Raw Data Plot**'
    lbl = tk.Label(root, text=txt)
    lbl.config(font=fontMainTitle)
    lbl.grid(row=0, column=0, ipadx=ipadx, ipady=ipady,
             sticky=tk.EW, columnspan=2)

    # Raw File Name
    ndx = entNdx['RAW']
    lbl = tk.Label(root, width=widthRowLbl, text=fields[ndx],
                   anchor=tk.W, font=fontLbl)
    lbl.grid(row=1, column=0, ipadx=ipadx, ipady=ipady, sticky=tk.W)
    root.entRAWFILENAME = tk.Entry(root, width=widthRowEnt,
                                   state=tk.NORMAL, font=fontEnt)
    root.entRAWFILENAME.config(disabledbackground=bgnd)
    root.entRAWFILENAME.grid(row=1, column=1, ipadx=ipadx, ipady=ipady,
                             padx=padx, pady=pady, sticky=tk.W)
    root.entRAWFILENAME.insert(0, 'Use Load Menu...')
    root.entRAWFILENAME.config(state=tk.DISABLED)
    entries.append((fields[ndx], root.entRAWFILENAME))

    # Data row to start plotting
    ndx = entNdx['START']
    lbl = tk.Label(root, width=widthRowLbl, text=fields[ndx],
                   anchor=tk.W, font=fontLbl)
    lbl.grid(row=2, column=0, ipadx=ipadx, ipady=ipady, sticky=tk.W)
    entPLOTSTART = tk.Entry(root, width=widthRowEnt, font=fontEnt)
    entPLOTSTART.grid(row=2, column=1, ipadx=ipadx, ipady=ipady,
                      padx=padx, pady=pady, sticky=tk.W)
    entPLOTSTART.insert(0, defaultStart)
    entries.append((fields[ndx], entPLOTSTART))

    # Data row to stop plotting
    ndx = entNdx['STOP']
    lbl = tk.Label(root, width=widthRowLbl, text=fields[ndx],
                   anchor=tk.W, font=fontLbl)
    lbl.grid(row=3, column=0, ipadx=ipadx, ipady=ipady, sticky=tk.W)
    entPLOTSTOP = tk.Entry(root, width=widthRowEnt, font=fontEnt)
    entPLOTSTOP.grid(row=3, column=1, ipadx=ipadx, ipady=ipady,
                     padx=padx, pady=pady, sticky=tk.W)
    entPLOTSTOP.insert(0, defaultStop)
    entries.append((fields[ndx], entPLOTSTOP))

    # Dot Size
    ndx = entNdx['DOT']
    lbl = tk.Label(root, width=widthRowLbl, text=fields[ndx],
                   anchor=tk.W, font=fontLbl)
    lbl.grid(row=4, column=0, ipadx=ipadx, ipady=ipady, sticky=tk.W)
    entDOTSIZE = tk.Entry(root, width=widthRowEnt, font=fontEnt)
    entDOTSIZE.grid(row=4, column=1, ipadx=ipadx, ipady=ipady,
                    padx=padx, pady=pady, sticky=tk.W)
    entDOTSIZE.insert(0, defaultDotSize)
    entries.append((fields[ndx], entDOTSIZE))

    # Default CMAP type radio button
    varCmapColors.set("STD")

    # Radio button for Standard Matplotlib colormap
    ndx = entNdx['STD']
    radioSTD = tk.Radiobutton(root, text=fields[ndx],
                              variable=varCmapColors, value="STD",
                              font=fontRadio, anchor=tk.W, width=widthRadio)
    radioSTD.grid(row=5, column=0, ipadx=ipadx, ipady=ipady,
                  padx=padx, pady=pady, sticky=tk.W)

    # Name of Standard Matplotlib colormap
    ent = tk.Entry(root, font=fontEnt, width=widthRowEnt)
    ent.grid(row=5, column=1, ipadx=ipadx, ipady=ipady,
             padx=padx, pady=pady, sticky=tk.W)
    entries.append((fields[ndx], ent))

    # Radio button for Linear Segmented colormap
    ndx = entNdx['CUSTLSEG']
    radioCUSTOMLSEG = tk.Radiobutton(root, text=fields[ndx],
                                     variable=varCmapColors,
                                     value="LSEG", font=fontRadio,
                                     anchor=tk.W, width=widthRadio)
    radioCUSTOMLSEG.grid(row=6, column=0, ipadx=ipadx, ipady=ipady,
                         padx=padx, pady=pady, sticky=tk.W)

    # Name of LinearSegmented colormap file
    root.entLSEGFILENAME = tk.Entry(root, width=widthRowEnt,
                                    state=tk.NORMAL, font=fontEnt)
    root.entLSEGFILENAME.config(disabledbackground=bgnd)
    root.entLSEGFILENAME.grid(row=6, column=1, ipadx=ipadx, ipady=ipady,
                              padx=padx, pady=pady, sticky=tk.W)
    root.entLSEGFILENAME.insert(0, 'Use Load Menu...')
    root.entLSEGFILENAME.config(state=tk.DISABLED)
    entries.append((fields[ndx], root.entLSEGFILENAME))

    # Radio button for Color List colormap
    ndx = entNdx['CUSTLIST']
    radioCUSTOMLIST = tk.Radiobutton(
        root, text=fields[ndx],
        variable=varCmapColors, value="LIST",
        font=fontRadio, anchor=tk.W, width=widthRadio)
    radioCUSTOMLIST.grid(row=7, column=0, ipadx=ipadx, ipady=ipady,
                         padx=padx, pady=pady, sticky=tk.W)

    # Name of Color List colormap file
    root.entLISTFILENAME = tk.Entry(root, width=widthRowEnt,
                                    state=tk.NORMAL, font=fontEnt)
    root.entLISTFILENAME.config(disabledbackground=bgnd)
    root.entLISTFILENAME.grid(row=7, column=1, ipadx=ipadx, ipady=ipady,
                              padx=padx, pady=pady, sticky=tk.W)
    root.entLISTFILENAME.insert(0, 'Use Load Menu...')
    root.entLISTFILENAME.config(state=tk.DISABLED)
    entries.append((fields[ndx], root.entLISTFILENAME))

    return entries


# Plot the data
def makePlot():
    global cmFileName
    # Get plot start number
    ndx = entNdx['START']
    tup = entries[ndx]
    pltstart = int(tup[1].get())

    # Get plot stop number
    ndx = entNdx['STOP']
    tup = entries[ndx]
    pltstop = int(tup[1].get())

    # Get dot size
    ndx = entNdx['DOT']
    tup = entries[ndx]
    dotSize = float(tup[1].get())

    # Set raw data vectors. Input data is assumed to be two columns with
    # the x data in column 1 and the y data in column 2.
    xxAll = rawData[:, 0]
    yyAll = rawData[:, 1]
    datLen = len(xxAll)

    # Extract data bounded by the start/stop settings
    xx = xxAll[(pltstart):pltstop]
    yy = yyAll[(pltstart):pltstop]

    if (debugDict["debug3"]):
        print('{0:+2.12e}  {1:+2.12e}'.format(xx[0], yy[0]))
        print('{0:+2.12e}  {1:+2.12e}'.format(xx[-1], yy[-1]))

    xxt = np.arange(len(xx))

    # Print the min/max calculated values
    xPltMin = min(xx)
    xPltMax = max(xx)
    yPltMin = min(yy)
    yPltMax = max(yy)
    print('Full length of raw data = {0:8d}'.format(datLen))
    print('minX = {0:10.1f}  maxX = {1:10.1f}'.format(xPltMin, xPltMax))
    print('minY = {0:10.1f}  maxY = {1:10.1f}'.format(yPltMin, yPltMax))

    # Make plot window
    window = tk.Toplevel()
    title = rawFileName
    tk.Label(window, text=title).pack()
    f = Figure(figsize=(windowWidth, windowHeight), dpi=dpi)
    figPlot = f.add_subplot(111)

    # Set plot facecolor
    figPlot.patch.set_facecolor(faceColor)

    # Minimize the border surrounding the plot area
    f.set_tight_layout(True)

    # Set plot window extents according to data ranges
    figPlot.set_xlim([xPltMin-xtraXlim, xPltMax+xtraXlim])
    figPlot.set_ylim([yPltMin-xtraYlim, yPltMax+xtraYlim])

    # Turn off grid labels
    figPlot.xaxis.set_visible(False)
    figPlot.yaxis.set_visible(False)

    if (varCmapColors.get() == "STD"):
        # Here to apply Standard colormap to plot
        ndx = entNdx['STD']
        tup = entries[ndx]
        temp = tup[1].get()
        cmapStd = temp.strip()
        cmFileName = cmapStd
        # Print colormap name
        if (debugDict["debug2"]):
            print("\n", cmFileName)
        figPlot.scatter(xx, yy, s=dotSize, c=xxt, cmap=cmapStd, 
						edgecolor='black')
    elif (varCmapColors.get() == "LSEG"):
        # Here to generate Linear Segmented colormap and apply to plot
        divisor = 255.0
        colorList = []

        # Print colormap name
        if (debugDict["debug2"]):
            print("\n", cmFileName)

        # Get Linear Segmented custom colormap file
        with open(cmFilePath, "r") as inFile:
            for line in inFile:
                if (debugDict["debug2"]):
                    # Suppress the extra newlines
                    print(line[0:-1])
                # Check for comment line, or blank line
                if (line.startswith('#')) or (len(line.split()) == 0):
                    continue
                else:
                    # Convert colormap from text to data
                    colorLine = eval(line)
                    scaled = (colorLine[0], [x/divisor for x in colorLine[1]])
                    colorList.append(scaled)

        normalize = mc.Normalize(vmin=0, vmax=len(xx))
        # Generate colormap and plot
        cmap = mc.LinearSegmentedColormap.from_list("", colorList)
        figPlot.scatter(xx, yy, s=dotSize, c=normalize(xxt), cmap=cmap, 
					    edgecolor='black')

    elif (varCmapColors.get() == "LIST"):
        # Here to generate Color List colormap and apply to plot

        # Print colormap name
        if (debugDict["debug2"]):
            print("\n", cmFileName)

        # Get Color List custom colormap file
        with open(cmFilePath, "r") as inFile:
            lines = []
            for line in inFile:
                if (debugDict["debug2"]):
                    # Suppress the extra newlines
                    print(line[0:-1])
                # Discard lines starting with #, or zero-length lines
                if (line.startswith('#')) or (len(line.split()) == 0):
                    continue
                else:
                    # Strip trailing newlines
                    line = line.rstrip("\n")
                    lines.append(line)

        for line in lines:
            lineSpl = line.split('=')
            # Parse lines with edge data
            if (lineSpl[0].strip() == 'edgeList'):
                edgeListStr = lineSpl[1].strip()
                edgeListStr = edgeListStr.strip('][').replace(",", "").split()
                edgeList = [float(x) for x in edgeListStr]
            # Parse lines with colors (names of hex codes)
            elif (lineSpl[0].strip() == 'rgbList'):
                rgbListStr = lineSpl[1].strip()
                rgbListStr = rgbListStr.strip('][').replace(",", "").split()
            else:
                continue

        # Check Color List for proper hex format, and named colors
        rgbOK = ckColorList(rgbListStr)
        if rgbOK is False:
            print("makePlot: Color List error")
            return
        # Check Edge List initial/final values and increasing values
        edgeOK = ckEdgeVals(edgeList)
        if edgeOK is False:
            print("makePlot: Edge List error")
            return

        # Adapt Edge List to data array
        bounds = [i*(len(xx)) for i in edgeList]
        # Generate colormap and plot
        cmap = mpl.colors.ListedColormap(rgbListStr)
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N, clip=True)

        figPlot.scatter(xx, yy, s=dotSize, c=xxt, cmap=cmap, norm=norm, 
					    edgecolor='black')
    else:
        print("makePlot: unknown colormap type")
        return

    # Save plot and information used to form the plot in two files.
    def Save():
        # Plot file names = concatenation of parts of: name of the raw
        # data file; name of the colormap.
        temp = rawFileName.split('.')
        outBase = temp[0]
        if (varCmapColors == "STD"):
            outBase = outBase + '.' + cmFileName
        else:
            temp = cmFileName.split('.')
            outBase = outBase + '.' + temp[0]
        picFile = outBase + '.png'
        FigureCanvasTkAgg.print_png(canvas, picFile)

        # Information file contains text lines: name of raw data file;
        # line to start plotting; line to stop plotting; dot size;
        # name of the colormap (file)
        fullText = rawFileName + '\n'
        fullText = fullText + str(pltstart) + '\n'
        fullText = fullText + str(pltstop) + '\n'
        fullText = fullText + str(dotSize) + '\n'
        fullText = fullText + cmFileName
        infoFile = outBase + '.rpd'

        # Write plot information to file
        with open(infoFile, "w") as outfile:
            outfile.write(fullText)

    canvas = FigureCanvasTkAgg(f, master=window)
    try:
        canvas.show()
    except AttributeError:
        canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Define Save button for plot window
    btnSave = tk.Button(master=window, text='Save',
                        command=Save)
    btnSave.pack(side=tk.RIGHT)

    toolbar = NavigationToolbar2TkAgg(canvas, window)
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    try:
        canvas.show()
    except AttributeError:
        canvas.draw()


# Load raw data from file
def getRawData():
    global rawData, rawFileName
    fullRAWFILENAME = filedialog.askopenfilename(
        initialdir=".",
        title="Select file",
        filetypes=(("raw data files", "raw*.txt"), ("all files", "*.*")))
    if (fullRAWFILENAME):
        empty = []
        rawFileName = os.path.basename(fullRAWFILENAME)
        root.entRAWFILENAME.config(state=tk.NORMAL)
        root.entRAWFILENAME.delete(0, tk.END)
        root.entRAWFILENAME.insert(0, rawFileName)
        root.entRAWFILENAME.config(
            state=tk.DISABLED,
            # Otherwise, font is greyed out when state is DISABLED
            disabledforeground='black')
        rawData = np.array(empty)
        rawData = np.loadtxt(fullRAWFILENAME)
        if (debugDict["debug1"]):
            print("\n", rawFileName)
            # Get first lines and last lines from file
            for N in [0, 1, 2, 3, 4, -5, -4, -3, -2, -1]:
                x = rawData[N, 0]
                y = rawData[N, 1]
                print('{0:+2.12e}  {1:+2.12e}'.format(x, y))
    else:
        return


# Load Linear Segmented colormap definition file name
def getLinearSegCMAP():
    global cmFileName, cmFilePath
    cmFilePath = filedialog.askopenfilename(
        initialdir=".",
        title="Select file",
        filetypes=(("Lin Segmented colormaps", "*.cmS"), ("all files", "*.*")))
    if (cmFilePath):
        cmFileName = os.path.basename(cmFilePath)
        root.entLSEGFILENAME.config(state=tk.NORMAL)
        root.entLSEGFILENAME.delete(0, tk.END)
        root.entLSEGFILENAME.insert(0, cmFileName)
        root.entLSEGFILENAME.config(
            state=tk.DISABLED,
            # Otherwise, font is greyed out when state is DISABLED
            disabledforeground='black')
        varCmapColors.set("LSEG")
    else:
        return


# Load Color List colormap definition file name
def getColorListCMAP():
    global cmFileName, cmFilePath
    cmFilePath = filedialog.askopenfilename(
        initialdir=".",
        title="Select file",
        filetypes=(("Color List files", "*.cmL"), ("all files", "*.*")))
    if (cmFilePath):
        cmFileName = os.path.basename(cmFilePath)
        root.entLISTFILENAME.config(state=tk.NORMAL)
        root.entLISTFILENAME.delete(0, tk.END)
        root.entLISTFILENAME.insert(0, cmFileName)
        root.entLISTFILENAME.config(
            state=tk.DISABLED, \
            # Otherwise, font is greyed out when state is DISABLED
            disabledforeground='black')
        varCmapColors.set("LIST")
    else:
        return


# Save colormap text file
def saveTxt(mapType):
    ftypes = [("colormap files", mapType),
              ('All files', '*')]
    outFile = filedialog.asksaveasfile(
        mode='w',
        filetypes=ftypes,
        defaultextension='.cm',
        confirmoverwrite=False)
    if not outFile:
        return
    strBox = root.textBox.get("1.0", 'end-1c')
    outFile.write(strBox)
    outFile.close()
    root.editWindow.destroy()


# Window for editing custom colormap
def cmEditWindow(mapType):
    fullPath = filedialog.askopenfilename(
        initialdir=".",
        title="Select file",
        filetypes=(("colormap files", mapType), ("all files", "*.*")))
    if (fullPath):
        fullName = os.path.basename(fullPath)
        cmapCustom = fullName
        with open(cmapCustom, 'r') as inCmap:
            cmapTxt = inCmap.read()
    else:
        return

    root.editWindow = tk.Toplevel()
    root.editWindow.geometry("+840+220")

    root.editWindow.title("Edit Custom Colormap")
    root.textBox = tk.Text(root.editWindow,
                           width=widthEditBox,
                           height=heightEditBox,
                           bg='white', font=fontText)
    root.textBox.pack(side='top', padx=10, pady=10)
    root.textBox.insert(tk.END, cmapTxt)

    buttonFrame = tk.Frame(root.editWindow, width=400, height=50, bg='grey')
    buttonFrame.pack(side='top', padx=10, pady=10)
    btnSaveTxt = tk.Button(buttonFrame, text='SaveTxt',
                           command=lambda mp=mapType: saveTxt(mp))
    btnSaveTxt.pack(side='left', padx=5, pady=5)


# Edit existing Linear Segmented colormap file
def cmLSegFileEdit():
    mapType = "*.cmS"
    cmEditWindow(mapType)


# Edit existing ColorList colormap file
def cmListFileEdit():
    mapType = "*.cmL"
    cmEditWindow(mapType)


# Create custom Linear Segmented colormap file
def linearSegCreate():
    # Save colormap text box to file
    def saveMapTxt():
        ftypes = [('Linear SegmentedColormap files', '*.cmS'),
                  ('All files', '*')]
        outFile = filedialog.asksaveasfile(mode='w',
                                           filetypes=ftypes,
                                           defaultextension='.cmS',
                                           confirmoverwrite=False)
        if not outFile:
            return
        strBox = textBox.get("1.0", 'end-1c')
        outFile.write(strBox)
        outFile.close()

    # Clear text box
    def clearBox():
        textBox.delete(1.0, tk.END)
        textBox.insert(tk.END, "")

    def R_slider(redVar):
        makeRGB_Stripe()

    def G_slider(greenVar):
        makeRGB_Stripe()

    def B_slider(blueVar):
        makeRGB_Stripe()

    # Display color stripes and combined hex code
    def makeRGB_Stripe():
        # Extract RGB data
        redInt = hex(redVar.get())
        strRed = redInt.lstrip('0x').zfill(2)
        greenInt = hex(greenVar.get())
        strGreen = str(greenInt).lstrip('0x').zfill(2)
        blueInt = hex(blueVar.get())
        strBlue = str(blueInt).lstrip('0x').zfill(2)

        redCanvas.configure(bg='#' + strRed + '0000')
        greenCanvas.configure(bg='#' + '00' + strGreen + '00')
        blueCanvas.configure(bg='#' + '0000' + strBlue)

        strHex = '#' + strRed + strGreen + strBlue
        hexEntry.delete(0, tk.END)
        hexEntry.insert(0, strHex)
        stripeCanvas.configure(bg=strHex)
        return

    # Convert data from text box to numerics
    def parseLine(strLine):
        # Eliminate spaces
        dropSpaces = "".join(strLine.split())
        # Drop '(',  and ')'
        dropParens = dropSpaces.replace("(", "").replace(")", "")
        # Split on commas to get list of strings
        strList = dropParens.split(',')
        # Convert strings to numerics
        parsed = []
        parsed.append(float(strList[0]))
        parsed.append(int(strList[1]))
        parsed.append(int(strList[2]))
        parsed.append(int(strList[3]))
        return(parsed)

    # Check for anchor value in range 0.0 -> 1.0, inclusive
    def anchorCellOK(anchorVal):
        if (0.0 <= anchorVal <= 1.0):
            OK = True
        else:
            OK = False
            msg = 'An anchor value is NOT in range 0.0->1.0'
            print(msg)
        return(OK)

    # Check for RGB value in range 0 -> 255, inclusive
    def rgbCellsOK(cells):
        OK = True
        for N in range(1, 4):
            if (0 <= cells[N] <= 255):
                pass
            else:
                OK = False
        if (OK is False):
            msg = 'An RGB value is NOT in range 0->255'
            print(msg)
        return(OK)

    # Make/display Linear Segmented colorbar
    def lsegColorBar(mstr):
        global fig, figNums, plt
        divisor = 255.0
        strBox = textBox.get("1.0", 'end-2c')
        splitLines = strBox.split("\n")

        colorList = []
        converted = []
        nLines = len(splitLines)
        ndx = 0
        for N in range(nLines):
            # Skip blank or comment lines
            if (len(splitLines[N]) == 0) or \
               (splitLines[N][0] == "#") or \
               (splitLines[N].isspace()):
                pass
            else:
                # Check for erroneous lines since user can edit textBox
                converted.append(parseLine(splitLines[N]))
                # Check anchor values
                OK = anchorCellOK(converted[ndx][0])
                if OK is True:
                    anchor = converted[ndx][0]
                else:
                    return
                # Check color values. Convert to range 0.0->1.0 if OK
                OK = rgbCellsOK(converted[ndx][:])
                if OK is True:
                    r = converted[ndx][1]/divisor
                    g = converted[ndx][2]/divisor
                    b = converted[ndx][3]/divisor
                    tup1 = (r, g, b)
                    colormapLine = (anchor, tup1)
                    colorList.append(colormapLine)
                else:
                    return
                ndx += 1

        # Generate data for colorbar
        gradient = np.linspace(0.0, 1.0, 200)
        gradient = np.vstack((gradient, gradient))

        # Make colormap
        cmap = mc.LinearSegmentedColormap.from_list("", colorList)

        # Create window for colorbar
        window = tk.Toplevel(master=mstr)
        window.geometry("+100+800")

        fig = Figure(figsize=(6, 2))
        ax = fig.add_subplot(111)

        fig.subplots_adjust(top=0.6, bottom=0.4, left=0.2, right=0.8)

        # Plot colorbar data
        ax.imshow(gradient, aspect='auto', cmap=cmap,
                  extent=[0.0, 1.0, 0.0, 1.0])

        # Disable axis labels
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)

        # Enable colorbar
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack()
        canvas.draw()

    # Capture line of: anchor, red, green, blue and add to text box
    def captureLine():
        anchor = anchorVar.get()
        anchorStr = "%3.2f" % anchor
        red = redVar.get()
        green = greenVar.get()
        blue = blueVar.get()
        captureStr = '(' + anchorStr + ', (' + \
                     str(red) + ', ' + \
                     str(green) + ', ' + \
                     str(blue) + '))\n'
        textBox.insert(tk.END, captureStr)

    # Main processing for creation of Linear Segmented colormap
    anchorVar = tk.DoubleVar()
    redVar = tk.IntVar()
    greenVar = tk.IntVar()
    blueVar = tk.IntVar()
    colLabels = ['Anchor', 'Red', 'Green', 'Blue', '']

    createCmWindow = tk.Toplevel()
    createCmWindow.geometry("+480+200")
    createCmWindow.title("Create Custom Linear Segmented Colormap")

    # Labels for sliders
    lblFrame = tk.Frame(createCmWindow, width=maxX, height=80, bg='grey')
    lblFrame.pack(side='top')
    for col in range(0, 5):
        label1 = tk.Label(lblFrame, width=entryWidth, text=colLabels[col],
                          font=fontLbl)
        label1.pack(side='left', padx=2, pady=2)

    # Make/initialize anchor, red, green, blue sliders
    sliderFrame = tk.Frame(createCmWindow, height=80)
    sliderFrame.pack(side='top', padx=2, pady=2)

    anchorSlider = tk.Scale(sliderFrame, length=150, variable=anchorVar,
                            from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                            tickinterval=1.0, sliderlength=20,
                            resolution=0.01)
    anchorSlider.set(0.0)
    anchorSlider.pack(side='left', padx=2, pady=2)

    redSlider = tk.Scale(sliderFrame, length=150, variable=redVar,
                         from_=0, to=255, orient=tk.HORIZONTAL,
                         tickinterval=255, sliderlength=20, showvalue=1)
    redSlider.set(255)
    redSlider.bind('<ButtonRelease-1>', R_slider)
    redSlider.pack(side='left', padx=2, pady=2)

    greenSlider = tk.Scale(sliderFrame, length=150, variable=greenVar,
                           from_=0, to=255, orient=tk.HORIZONTAL,
                           tickinterval=255, sliderlength=20, showvalue=1)
    greenSlider.set(255)
    greenSlider.bind('<ButtonRelease-1>', G_slider)
    greenSlider.pack(side='left', padx=2, pady=2)

    blueSlider = tk.Scale(sliderFrame, length=150, variable=blueVar,
                          from_=0, to=255, orient=tk.HORIZONTAL,
                          tickinterval=255, sliderlength=20, showvalue=1)
    blueSlider.set(255)
    blueSlider.bind('<ButtonRelease-1>', B_slider)
    blueSlider.pack(side='left', padx=2, pady=2)

    btnCapture = tk.Button(sliderFrame, text='Capture Line', width=15,
                           command=captureLine)
    btnCapture.pack(side='right', padx=5, pady=5)

    colorsFrame = tk.Frame(createCmWindow)
    colorsFrame.pack(side='top', padx=2, pady=2)

    # Make individual displays for red, green, blue slider values
    redCanvas = tk.Canvas(colorsFrame, width=150, height=20, bg='white')
    redCanvas.pack(side='left', padx=2, pady=2)

    greenCanvas = tk.Canvas(colorsFrame, width=150, height=20, bg='white')
    greenCanvas.pack(side='left', padx=2, pady=2)

    blueCanvas = tk.Canvas(colorsFrame, width=150, height=20, bg='white')
    blueCanvas.pack(side='left', padx=2, pady=2)

    # Make display for combined red, green, blue slider values
    stripeFrame = tk.Frame(createCmWindow, width=400, height=200)
    stripeFrame.pack(side='top', padx=4, pady=4)
    hexEntry = tk.Entry(stripeFrame, width=entryWidth, font=fontEnt,
                        justify=tk.CENTER)

    # Initialize hex value for combined red, green, blue slider values
    hexEntry.insert(0, "#ffffff")
    hexEntry.pack(side='top', padx=2, pady=2)
    stripeCanvas = tk.Canvas(stripeFrame, width=150, height=80, bg='white')
    stripeCanvas.pack(side='top', padx=80, pady=10)

    # Text box for capturing lines of anchor, red, green, blue values
    textBox = tk.Text(createCmWindow, width=40, height=15, bg='white',
                      font=fontText)
    textBox.pack(side='top', padx=10, pady=10)
    textBox.insert(tk.INSERT,
                   "# Comment lines (whole lines only) begin with '#'\n")
    textBox.insert(tk.END, "")

    # Create buttons
    buttonFrame = tk.Frame(createCmWindow, width=400, height=50, bg='grey')
    buttonFrame.pack(side='top', padx=10, pady=10)
    # Clear text box
    btnClear = tk.Button(buttonFrame, text='ClearBox', command=clearBox)
    btnClear.pack(side='left', padx=5, pady=5)
    # Create colorbar
    btnColorBar = tk.Button(
        buttonFrame, text='ColorBar',
        command=lambda wn=createCmWindow: lsegColorBar(wn))

    btnColorBar.pack(side='left', padx=5, pady=5)

    # Save colormap text definition
    btnSaveTxt = tk.Button(buttonFrame, text='SaveTxt', command=saveMapTxt)
    btnSaveTxt.pack(side='left', padx=5, pady=5)
    btnCloseWindow = tk.Button(buttonFrame, text='Close',
                               command=createCmWindow.destroy)
    btnCloseWindow.pack(side='left', padx=5, pady=5)
    makeRGB_Stripe()


# Color List colormap - check edge value list for mandatory initial/final
# values and increasing values across whole list
def ckEdgeVals(lst):
    # Check list for monotonically increasing values
    def ckIncVals(lst):
        fltList = [float(x) for x in lst]
        OK = np.all(np.diff(fltList) > 0.0)
        return (OK)

    # Check for "equals"
    def ckClose(a, b):
        if (abs(a - b) < 1e-9):
            OK = True
        else:
            OK = False
        return (OK)

    # Check first/last edge values
    if (ckClose(float(lst[0]), 0.0) is False) or \
       (ckClose(float(lst[-1]), 1.0) is False) or \
       (ckIncVals(lst) is False):
        msg = 'First/last edge value error OR values not increasing'
        print(msg)
        OK = False
    else:
        OK = True
    return (OK)


# Get Color List edge values from text box
def getEdgeVals(TextBox):
    edgeStr = TextBox.get("1.0", "end-2c")
    splitLines = edgeStr.split("\n")

    edgeList = []
    nLines = len(splitLines)

    # Parse values from text box
    for N in range(nLines):
        spl = splitLines[N]
        # Strip leading/trailing spaces, trailing comma
        spl = spl.lstrip().rstrip().rstrip(",")
        # Discard no-length, leading #, all spaces lines
        if (len(spl) == 0) or \
           (spl[0] == "#") or \
           (spl.isspace()):
            pass
        else:
            # Build list of edge values
            edgeList.append(spl)

    # Check for edge value errors
    OK = ckEdgeVals(edgeList)
    if (OK is False):
        print("In getEdgeVals - edgeList error")

    return(edgeList, OK)


# Check Color List for proper hex, and recognized named colors
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
            if ((len(N)) != 6) or (isHex(N) is False):
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


# Get Color List from text box
def getColorVals(TextBox):
    rgbStr = TextBox.get("1.0", "end-1c")
    splitLines = rgbStr.split("\n")

    rgbList = []
    nLines = len(splitLines)

    # Parse values from text box
    for N in range(nLines):
        spl = splitLines[N]
        # Strip leading/trailing spaces, trailing comma
        spl = spl.lstrip().rstrip().rstrip(",")
        # Discard no-length, all spaces lines
        if (len(spl) == 0) or \
           (spl.isspace()):
            # Skip line
            pass
        else:
            # Build list of rgb values
            rgbList.append(spl)

    # Check Color List values/names for errors
    OK = ckColorList(rgbList)
    if OK is False:
        rgbList = []
    return(rgbList, OK)


# Create custom Color List colormap file
def colorListCreate():

    def R_slider(redVar):
        makeRGB_Stripe()

    def G_slider(greenVar):
        makeRGB_Stripe()

    def B_slider(blueVar):
        makeRGB_Stripe()

    def saveListMapTxt():
        # Get edge values from text box. Check for errors.
        (edgeList, edgeOK) = getEdgeVals(edgesTextBox)

        # Get color values/names from text box. Check for errors.
        (rgbList, rgbOK) = getColorVals(rgbTextBox)

        if (edgeOK is False):
            print("Edge list error")
            print("edgeList: ", edgeList)
        if (rgbOK is False):
            print("RGB list error")
            print("rgbList: ", rgbList)

        if (edgeOK is True) and (rgbOK is True):
            # Check for correct lengths of the two lists
            if (len(rgbList) + 1 != len(edgeList)):
                msg = "Edge list length not 1 more than RGB list"
                print(msg)
                return
        else:
            return

        # Build text for file output
        sep = ", "
        edgeText = sep.join(edgeList)
        edgeText = "edgeList = [" + edgeText + "]\n\n"

        sep = ", "
        rgbText = sep.join(rgbList)
        rgbText = "rgbList = [" + rgbText + "]\n"

        commentText = "# Comment lines (whole lines only) begin with '#'\n"

        outText = commentText + edgeText + rgbText

        # Output definition to file
        ftypes = [('Color List Colormap files', '*.cmL'), ('All files', '*')]
        outFile = filedialog.asksaveasfile(mode='w',
                                           filetypes=ftypes,
                                           defaultextension='.cmL',
                                           confirmoverwrite=False)
        if not outFile:
            return
        outFile.write(outText)
        outFile.close()

        return

    # Display color stripes and combined hex code
    def makeRGB_Stripe():
        # Extract RGB data
        redInt = hex(redVar.get())
        strRed = redInt.lstrip('0x').zfill(2)
        greenInt = hex(greenVar.get())
        strGreen = str(greenInt).lstrip('0x').zfill(2)
        blueInt = hex(blueVar.get())
        strBlue = str(blueInt).lstrip('0x').zfill(2)

        redCanvas.configure(bg='#' + strRed + '0000')
        greenCanvas.configure(bg='#' + '00' + strGreen + '00')
        blueCanvas.configure(bg='#' + '0000' + strBlue)

        strHex = '#' + strRed + strGreen + strBlue
        hexEntry.delete(0, tk.END)
        hexEntry.insert(0, strHex)
        stripeCanvas.configure(bg=strHex)
        return

    # Get edge value and insert into text box
    def GrabEdgeVal():
        edgeVal = edgesVar.get()
        edgeStr = ("%3.2f" % edgeVal) + '\n'
        edgesTextBox.insert(tk.END, edgeStr)
        return

    # Get RGB value and insert into text box
    def GrabColorVal():
        rgbVal = hexEntry.get()
        rgbStr = '{0:<8}'.format(rgbVal) + '\n'
        rgbTextBox.insert(tk.END, rgbStr)
        return

    # Clear Edges text box
    def clearEdgesBox():
        edgesTextBox.delete(1.0, tk.END)
        edgesTextBox.insert(tk.END, "")

    # Clear RGB Values text box
    def clearValBox():
        rgbTextBox.delete(1.0, tk.END)
        rgbTextBox.insert(tk.END, "")

    # Make/display Color List colorbar
    def listColorBar(mstr):
        # Get edge values from text box. Check for errors.
        (edgeList, edgeOK) = getEdgeVals(edgesTextBox)

        # Get color values/names from text box. Check for errors.
        (rgbList, rgbOK) = getColorVals(rgbTextBox)

        if (edgeOK is True) and (rgbOK is True):
            # Check for correct lengths of the two lists
            if (len(rgbList) + 1 != len(edgeList)):
                msg = "Edge list length not 1 more than RGB list"
                print(msg)
                return
        else:
            return

        # Generate data for colorbar
        gradient = np.linspace(0.0, 1.0, 200)
        gradient = np.vstack((gradient, gradient))

        # Make colormap
        cmap = mpl.colors.ListedColormap(rgbList)
        bounds = []
        for x in edgeList:
            bounds.append(float(x))
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N, clip=True)

        window = tk.Toplevel(master=mstr)
        window.geometry("+80+600")
        fig = Figure(figsize=(6, 2))
        ax = fig.add_subplot(111)

        fig.subplots_adjust(top=0.6, bottom=0.4, left=0.2, right=0.8)
        ax.imshow(gradient, aspect='auto', cmap=cmap, norm=norm,
                  extent=[0.0, 1.0, 0.0, 1.0])

        # Turn off axis display
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack()
        canvas.draw()

        return

    # Display image of known colors and associated hex values
    def showNamedColors():
        makeImage("./Support_rawPlot/colorsAlphHex.png")
        return

    # Main processing for creation of Color List colormap
    padx = 2
    pady = 2
    hgt = 500

    edgesVar = tk.DoubleVar()
    redVar = tk.IntVar()
    greenVar = tk.IntVar()
    blueVar = tk.IntVar()

    createCmWindow = tk.Toplevel()
    createCmWindow.geometry("+380+200")
    createCmWindow.title("Create Custom Colormap from Color List")

    # Frame for capturing edges(boundaries) for the ColorList
    edgesFrame = tk.Frame(createCmWindow, width=300, height=hgt)
    edgesFrame.grid(row=0, column=0, padx=padx, pady=pady, sticky=tk.W)

    edgesLabel = tk.Label(edgesFrame, width=entryWidth, text='Edge Value',
                          font=fontLbl)
    edgesLabel.grid(row=0, column=0, padx=padx, pady=pady, sticky=tk.N)

    # Make/initialize edges slider
    edgesSlider = tk.Scale(edgesFrame, length=150, variable=edgesVar,
                           from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                           tickinterval=1.0, sliderlength=20,
                           resolution=0.01)
    edgesSlider.set(0.0)
    edgesSlider.grid(row=1, column=0, padx=padx, pady=pady, sticky=tk.N)

    # Text box for edges values
    edgesTextBox = tk.Text(edgesFrame, width=12, height=15, bg='white',
                           font=fontText)
    edgesTextBox.grid(row=2, column=0, padx=padx, pady=pady, sticky=tk.N)
    edgesTextBox.insert(tk.END, "")
    edgesGrabVal = tk.Button(edgesFrame, text='Grab Value', width=12,
                             command=GrabEdgeVal)
    edgesGrabVal.grid(row=3, column=0, padx=padx, pady=pady, sticky=tk.N)
    btnEdgesClear = tk.Button(edgesFrame, text='ClearBox', width=12,
                              command=clearEdgesBox)
    btnEdgesClear.grid(row=4, column=0, padx=padx, pady=pady, sticky=tk.N)

    # Separator between Edges and Colors frames
    wallFrame = tk.Frame(createCmWindow, width=20, height=hgt,
                         bd=2, relief=tk.RAISED, bg='grey')
    wallFrame.grid(row=0, column=1, padx=padx, pady=pady, sticky=tk.W)

    # Frame for capturing colors
    colorsFrame = tk.Frame(createCmWindow, width=700, height=hgt)
    colorsFrame.grid(row=0, column=2, padx=padx, pady=pady, sticky=tk.E)

    # Red slider
    lblRed = tk.Label(colorsFrame, width=entryWidth, text='Red',
                      font=fontLbl, bd=2, relief=tk.RAISED)
    lblRed.grid(row=0, column=0, padx=padx, pady=pady, sticky=tk.NW)
    redSlider = tk.Scale(colorsFrame, length=150, variable=redVar,
                         from_=0, to=255, orient=tk.HORIZONTAL,
                         tickinterval=255, sliderlength=20, showvalue=1)
    redSlider.set(255)
    redSlider.bind('<ButtonRelease-1>', R_slider)
    redSlider.grid(row=1, column=0, padx=padx, pady=pady, sticky=tk.W)

    # Green slider
    lblGreen = tk.Label(colorsFrame, width=entryWidth, text='Green',
                        font=fontLbl, bd=2, relief=tk.RAISED)
    lblGreen.grid(row=0, column=1, padx=padx, pady=pady, sticky=tk.NW)
    greenSlider = tk.Scale(colorsFrame, length=150, variable=greenVar,
                           from_=0, to=255, orient=tk.HORIZONTAL,
                           tickinterval=255, sliderlength=20, showvalue=1)
    greenSlider.set(255)
    greenSlider.bind('<ButtonRelease-1>', G_slider)
    greenSlider.grid(row=1, column=1, padx=padx, pady=pady, sticky=tk.W)

    # Blue slider
    lblBlue = tk.Label(colorsFrame, width=entryWidth, text='Blue',
                       font=fontLbl, bd=2, relief=tk.RAISED)
    lblBlue.grid(row=0, column=2, padx=padx, pady=pady, sticky=tk.NW)

    blueSlider = tk.Scale(colorsFrame, length=150, variable=blueVar,
                          from_=0, to=255, orient=tk.HORIZONTAL,
                          tickinterval=255, sliderlength=20, showvalue=1)
    blueSlider.set(255)
    blueSlider.bind('<ButtonRelease-1>', B_slider)
    blueSlider.grid(row=1, column=2, padx=padx, pady=pady, sticky=tk.W)

    # Make individual displays for red, green, blue slider values
    redCanvas = tk.Canvas(colorsFrame, width=150, height=20, bg='white')
    redCanvas.grid(row=2, column=0, padx=padx, pady=pady, sticky=tk.W)

    greenCanvas = tk.Canvas(colorsFrame, width=150, height=20, bg='white')
    greenCanvas.grid(row=2, column=1, padx=padx, pady=pady, sticky=tk.W)

    blueCanvas = tk.Canvas(colorsFrame, width=150, height=20, bg='white')
    blueCanvas.grid(row=2, column=2, padx=padx, pady=pady, sticky=tk.W)

    # RGB hex code
    hexEntry = tk.Entry(colorsFrame, width=entryWidth, font=fontEnt,
                        justify=tk.CENTER)
    hexEntry.insert(0, "#ffffff")
    hexEntry.grid(row=3, column=1, padx=padx, pady=pady, sticky=tk.EW)

    stripeCanvas = tk.Canvas(colorsFrame, width=150, height=80, bg='white')
    stripeCanvas.grid(row=4, column=1, padx=padx, pady=pady, sticky=tk.EW)

    # Text box containing the color list
    rgbTextBox = tk.Text(colorsFrame, width=30, height=12, bg='white',
                         font=fontFixed)
    rgbTextBox.grid(row=5, column=0, columnspan=3, padx=padx,
                    pady=pady, sticky=tk.EW)
    rgbTextBox.insert(tk.END, "")

    buttonFrame1 = tk.Frame(colorsFrame, width=250, height=50)
    buttonFrame1.grid(row=6, column=0, columnspan=3, padx=padx, pady=pady)
    rgbGrabVal = tk.Button(buttonFrame1, text='Grab Value', width=12,
                           command=GrabColorVal)
    rgbGrabVal.grid(row=0, column=0, padx=padx, pady=pady, sticky=tk.E)
    btnValClear = tk.Button(buttonFrame1, text='ClearBox', width=12,
                            command=clearValBox)
    btnValClear.grid(row=0, column=1, padx=padx, pady=pady, sticky=tk.E)

    # Separator between build frames and control buttons
    floorFrame = tk.Frame(createCmWindow, width=660, height=20,
                          bd=2, relief=tk.RAISED, bg='grey')
    floorFrame.grid(row=7, column=0, columnspan=4, padx=padx, pady=pady)

    buttonFrame2 = tk.Frame(createCmWindow, width=660, height=50)
    buttonFrame2.grid(row=8, column=0, columnspan=4, padx=padx, pady=pady)
    btnColorNames = tk.Button(buttonFrame2, text='Color Names',
                              command=showNamedColors)
    btnColorNames.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
    btnSaveListTxt = tk.Button(buttonFrame2, text='SaveTxt',
                               command=saveListMapTxt)
    btnSaveListTxt.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)

    btnListColorBar = tk.Button(
        buttonFrame2, text='ColorBar',
        command=lambda wn=createCmWindow: listColorBar(wn))
    btnListColorBar.grid(row=0, column=3, padx=5, pady=5, sticky=tk.E)

    btnCloseWindow = tk.Button(buttonFrame2, text='Close',
                               command=createCmWindow.destroy)
    btnCloseWindow.grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)

    makeRGB_Stripe()

    return


# Display program overview/help
def overView():
    overviewHelpWindow = tk.Toplevel()
    tk.Label(overviewHelpWindow, text="Program Overview").pack()

    txtBox = tk.Text(overviewHelpWindow, height=50, width=88, padx=20)
    fileHandle = open('./Support_rawPlot/rawPlotHelp.txt', 'r')
    txt = fileHandle.read()  # Read the file to a variable
    fileHandle.close()

    txtBox.insert(0.0, txt)  # Insert the text into the text widget
    txtBox.config(state=tk.DISABLED)  # Disable user modifications

    vbar = tk.Scrollbar(overviewHelpWindow, orient=tk.VERTICAL)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    vbar.config(command=txtBox.yview)
    txtBox.config(yscrollcommand=vbar.set)
    txtBox.pack(expand=1, fill=tk.BOTH)  # Show the text widget


# Gallery Images
def loadGallery1():
    makeImage("./Gallery_rawPlot/galleryImg_1.png")


def loadGallery2():
    makeImage("./Gallery_rawPlot/galleryImg_2.png")


def loadGallery3():
    makeImage("./Gallery_rawPlot/galleryImg_3.png")


# Standard Colormap Images
def loadStdColormaps1():
    makeImage("./Support_rawPlot/colorMaps_1.png")


def loadStdColormaps2():
    makeImage("./Support_rawPlot/colorMaps_2.png")


# Custom Colormap Make Screens/Examples
def loadMakeCm():
    makeImage("./Support_rawPlot/makeScreens.png")


# Make/display program About window
def aboutTxt():
    aboutWindow = tk.Toplevel()
    winWidth = 700
    winHeight = 400

    posRight = int(aboutWindow.winfo_screenwidth()/2 - winWidth/2)
    posDown = int(aboutWindow.winfo_screenheight()/3 - winHeight/2)
    aboutWindow.geometry("+{}+{}".format(posRight, posDown))

    # Add thumbnail to About window
    canvas = tk.Canvas(aboutWindow, width=200, height=350)
    canvas.pack(anchor='w', side=tk.LEFT, padx=2, pady=2)
    photo = tk.PhotoImage(file='./Support_rawPlot/aboutImg.png')
    canvas.create_image(102, 100, image=photo)
    # Attach photo to canvas since photo is a local object
    # that gets garbage collected
    canvas.image = photo

    # Insert version and history text.
    titleTxt = "    ** RAW DATA PLOT **\n"
    txtBox2 = tk.Text(aboutWindow, height=25, width=75, padx=10)
    txtBox2.tag_configure('titleFont', font=('Liberation Serif', 20, 'bold'))
    scroll = tk.Scrollbar(aboutWindow, command=txtBox2.yview)
    txtBox2.configure(yscrollcommand=scroll.set)
    txtBox2.pack(side=tk.LEFT, anchor='nw')
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    txtBox2.insert(tk.END, titleTxt, 'titleFont')

    fileHandle = open('./Support_rawPlot/aboutText.txt', 'r')
    aboutText = fileHandle.read()  # Read the file to a variable
    fileHandle.close()

    txtBox2.tag_configure('textFont', font=('Liberation Serif', 12))
    txtBox2.insert(tk.END, aboutText, 'textFont')
    txtBox2.config(state=tk.DISABLED)


# Display generic window image (Overview, Gallery, ColorMaps,...)
def makeImage(imgStr):
    img = ImageTk.PhotoImage(file=imgStr)
    top = tk.Toplevel()
    wth = img.width()
    hgt = img.height()
    x = 500
    y = 50
    top.geometry('%dx%d+%d+%d' % (wth, hgt, x, y))
    picName = "** " + imgStr.split("/")[-1] + " **"
    top.title(picName)
    frame = tk.Frame(top, bd=0)
    frame.pack()
    canvas = tk.Canvas(frame, bd=0, width=wth, height=hgt)
    canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=0)
    canvas.create_image(0, 0, image=img, anchor=tk.NW)
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
    root.title("Raw Data Plot")
    root.geometry("+80+120")

    varCmapColors = tk.StringVar()

    entries = makeForm(root)

    actionFrame = tk.Frame(root)
    actionFrame.grid(row=8, column=1, sticky=tk.E)

    # Main window "Quit" button
    btnQuit = tk.Button(actionFrame, text='Quit', command=root.destroy)
    btnQuit.grid(row=0, column=1, sticky=tk.E)

    # Main window button to make the plot
    btnPlot = tk.Button(actionFrame, text='Plot',
                        command=(makePlot))
    btnPlot.grid(row=0, column=0, padx=2, pady=2)
    actionFrame.grid(sticky=tk.E)

    # Define menubar
    menubar = tk.Menu(root)

    # Load Menu
    loadMenu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(
        label="Load",
        font=fontMenu,
        menu=loadMenu)
    # Select raw data file name
    loadMenu.add_command(
        label="Raw File",
        font=fontMenu,
        command=getRawData)
    # Load custom colormap
    loadCMAP_Menu = tk.Menu(tearoff=False)
    loadMenu.add_cascade(
        label="Custom CMAP File",
        font=fontMenu,
        menu=loadCMAP_Menu)
    loadCMAP_Menu.add_command(
        label="LinearSegmented",
        font=fontMenu,
        command=getLinearSegCMAP)
    loadCMAP_Menu.add_command(
        label="ColorList",
        font=fontMenu,
        command=getColorListCMAP)

    # Custom colormap edit/create
    customCmMenu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(
        label="CustomMap",
        font=fontMenu,
        menu=customCmMenu)

    editCmMenu = tk.Menu(tearoff=False)
    customCmMenu.add_cascade(
        label="Edit existing",
        font=fontMenu,
        menu=editCmMenu)
    editCmMenu.add_command(
        label="LinearSegmented",
        font=fontMenu,
        command=cmLSegFileEdit)
    editCmMenu.add_command(
        label="ColorList",
        font=fontMenu,
        command=cmListFileEdit)

    newCmMenu = tk.Menu(tearoff=False)
    customCmMenu.add_cascade(
        label="Create new",
        font=fontMenu,
        menu=newCmMenu)
    newCmMenu.add_command(
        label="LinearSegmented",
        font=fontMenu,
        command=linearSegCreate)
    newCmMenu.add_command(
        label="ColorList",
        font=fontMenu,
        command=colorListCreate)

    # Help menu
    helpmenu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(
        label="Help",
        font=fontMenu,
        menu=helpmenu)

    # Program overview
    overviewMenu = tk.Menu(tearoff=False)
    helpmenu.add_command(
        label="Overview",
        font=fontMenu,
        command=overView)

    # Image gallery
    galleryMenu = tk.Menu(tearoff=False)
    helpmenu.add_cascade(
        label="Gallery",
        font=fontMenu,
        menu=galleryMenu)
    galleryMenu.add_command(
        label="Image 1",
        font=fontMenu,
        command=loadGallery1)
    galleryMenu.add_command(
        label="Image 2",
        font=fontMenu,
        command=loadGallery2)
    galleryMenu.add_command(
        label="Image 3",
        font=fontMenu,
        command=loadGallery3)
    stdCmMenu = tk.Menu(tearoff=False)
    helpmenu.add_cascade(
        label="Std Colormaps",
        font=fontMenu,
        menu=stdCmMenu)
    stdCmMenu.add_command(
        label="Pg 1",
        font=fontMenu,
        command=loadStdColormaps1)
    stdCmMenu.add_command(
        label="Pg 2", font=fontMenu,
        command=loadStdColormaps2)
    makeCmMenu = tk.Menu(tearoff=False)
    helpmenu.add_command(
        label="Colormap Screens",
        font=fontMenu,
        command=loadMakeCm)

    helpmenu.add_command(
        label="About",
        font=fontMenu,
        command=aboutTxt)

    root.config(menu=menubar)
    root.mainloop()
