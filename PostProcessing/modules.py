########################################################################################################################
# iCorrVision Post-processing Module                                                                                   #
# iCorrVision team:     João Carlos Andrade de Deus Filho,  M.Sc. (PGMEC/UFF¹)      <joaocadf@id.uff.br>               #
#                       Prof. Luiz Carlos da Silva Nunes,   D.Sc.  (PGMEC/UFF¹)     <luizcsn@id.uff.br>                #
#                       Prof. José Manuel Cardoso Xavier,   P.hD.  (FCT/NOVA²)      <jmc.xavier@fct.unl.pt>            #
#                                                                                                                      #
#   1. Department of Mechanical Engineering | PGMEC - Universidade Federal Fluminense (UFF)                            #
#     Campus da Praia Vermelha | Niterói | Rio de Janeiro | Brazil                                                     #
#   2. NOVA SCHOOL OF SCIENCE AND TECHNOLOGY | FCT NOVA - Universidade NOVA de Lisboa (NOVA)                           #
#     Campus de Caparica | Caparica | Portugal                                                                         #
#                                                                                                                      #
# Date: 28-03-2022                                                                                                     #
########################################################################################################################

'''
    iCorrVision Post-processing Module
    Copyright (C) 2022 iCorrVision team

    This file is part of the iCorrVision software.

    The iCorrVision Post-processing Module is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The iCorrVision-3D Calibration Module is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

V = 'v1.04.22' # Version

########################################################################################################################
# Modules
########################################################################################################################
import cv2; import numpy as np
import tkinter as tk; from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import glob
import subprocess
from threading import Thread
import matplotlib
from matplotlib.pyplot import gca; import ntpath
import cv2 as cv; import scipy; import scipy.optimize
from PIL import Image, ImageTk
import datetime
from matplotlib import pyplot as plt
matplotlib.use('Agg', force=True)
plt.rcParams["text.usetex"]= True

########################################################################################################################
# Open user guide 2D
########################################################################################################################
def openguide2D(CurrentDir):
    subprocess.Popen([CurrentDir + '\static\iCorrVision-2D.pdf'], shell=True)

########################################################################################################################
# Open user guide 3D
########################################################################################################################
def openguide3D(CurrentDir):
    subprocess.Popen([CurrentDir + '\static\iCorrVision-3D.pdf'], shell=True)

########################################################################################################################
# Function to select the output folder of the correlation module
########################################################################################################################
def results_folder(console, results_status, resultsFolder):
    global filename_results

    filename_results = filedialog.askdirectory()
    resultsFolder.set(filename_results)

    console.insert(tk.END, '#############################################################################\n\n')
    console.see('insert')

    if not filename_results:
        results_status.configure(bg = 'red') # Red indicator
        console.insert(tk.END, 'The results folder was not selected\n\n')
        console.see('insert')
        messagebox.showerror('Error','The results folder was not selected!')
    else:
        results_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'Results folder - {resultsFolder.get()}\n\n')
        console.see('insert')

########################################################################################################################
# Function - try integer value
########################################################################################################################
def tryint(s):
    try:
        return int(s)
    except:
        return s

########################################################################################################################
# Turn a string into a list of string
########################################################################################################################
def stringToList(s):
    
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

########################################################################################################################
# Function to automatically detect the last instant
########################################################################################################################
def end_instant(Instant, EndInstant):
    global fileNames
    EndInstant.set(0)
    Instant.set(len(fileNames))

########################################################################################################################
# Function to select the cropped images folder of the correlation module (must contain Left and Right folders)
########################################################################################################################
def selection_folder(console, selection_status, selectionFolder):
    global filename_selection, fileNames

    filename_selection = filedialog.askdirectory()
    selectionFolder.set(filename_selection)

    console.insert(tk.END, '#############################################################################\n\n')
    console.see('insert')

    if not filename_selection:
        selection_status.configure(bg = 'red') # Red indicator
        console.insert(tk.END, 'The images folder was not selected\n\n')
        console.see('insert')
        messagebox.showerror('Error','The images folder was not selected!')
    else:
        selection_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'Images folder - {selectionFolder.get()}\n\n')
        console.see('insert')
        # Stereo correlation test:
        if sorted(glob.glob(selectionFolder.get()+'\\Left\\*'),key=stringToList) == []:
            fileNames = sorted(glob.glob(selectionFolder.get()+'\\*'),key=stringToList)
        else:
            fileNames = sorted(glob.glob(selectionFolder.get() + '\\Left\\*'), key=stringToList)

########################################################################################################################
# Function to select the output figures folder
########################################################################################################################
def figure_folder(console, figure_status, figureFolder):
    global filename_figure

    filename_figure = filedialog.askdirectory()
    figureFolder.set(filename_figure)

    console.insert(tk.END, '#############################################################################\n\n')
    console.see('insert')

    if not filename_figure:
        figure_status.configure(bg = 'red') # Red indicator
        console.insert(tk.END, 'The figure folder was not selected\n\n')
        console.see('insert')
        messagebox.showerror('Error','The figure folder was not selected!')
    else:
        figure_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'All figures will be saved in {figureFolder.get()}\n\n')
        console.see('insert')

########################################################################################################################
# Function to select the output folder
########################################################################################################################
def output_folder(console, save_out_status, outputFolder):
    global filename_output

    filename_output = filedialog.askdirectory()
    outputFolder.set(filename_output)

    console.insert(tk.END, '#############################################################################\n\n')
    console.see('insert')

    if not filename_output:
        save_out_status.configure(bg = 'red') # Red indicator
        console.insert(tk.END, 'The figure folder was not selected\n\n')
        console.see('insert')
        messagebox.showerror('Error','The figure folder was not selected!')
    else:
        save_out_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'All figures will be saved in {outputFolder.get()}\n\n')
        console.see('insert')

########################################################################################################################
# Function to check all figures
########################################################################################################################
def checkall(AllPlots, cbs_plot):
    if AllPlots.get() == 1:
        for cb in cbs_plot:
            cb.set(1)
    else:
        for cb in cbs_plot:
            cb.set(0)

########################################################################################################################
# Function to change all axes limits to automatic 
########################################################################################################################
def checkallauto(AllAuto, cbs_auto):
    if AllAuto.get() == 1:
        for cba in cbs_auto:
            cba.set(1)
    else:
        for cba in cbs_auto:
            cba.set(0)

########################################################################################################################
# Function to close the software
########################################################################################################################
def close(menu):
    ans = messagebox.askquestion('Close','Are you sure you want to exit iCorrVision Post-processing module?',icon ='question')
    if ans == 'yes':
        menu.destroy()
        menu.quit()

########################################################################################################################
# Save function - Results log
########################################################################################################################
def save(menu, console, file, file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm, Valpixel, Strain_window,
         Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
         ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, Correlation):

    if file_var.get():

        f = open(file.get(),"w")

        f.write('iCorrVision Post-processing Module - ' + str(datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")))
        f.write('\nResults folder:\n')
        f.write(str(resultsFolder.get().rstrip("\n")))
        f.write('\nImage folder:\n')
        f.write(str(selectionFolder.get().rstrip("\n")))
        f.write('\nFigure folder:\n')
        f.write(str(figureFolder.get().rstrip("\n")))
        f.write('\nOutput folder:\n')
        f.write(str(outputFolder.get().rstrip("\n")))
        f.write('\nMethod:\n')
        f.write(str(Method.get().rstrip("\n")))
        f.write('\nCorrelation:\n')
        f.write(str(Correlation.get().rstrip("\n")))
        f.write('\nCalibration:\n')
        f.write(str(Valmm.get()) + '\n')
        f.write(str(Valpixel.get()))
        f.write('\nStrain window:\n')
        f.write(str(Strain_window.get()))
        f.write('\nShape function:\n')
        f.write(str(Shape_function.get().rstrip("\n")))
        f.write('\nText Font:\n')
        f.write(str(TextFont.get().rstrip("\n")))
        f.write('\nFont size:\n')
        f.write(str(FontSize.get()))
        f.write('\nX ticks:\n')
        f.write(str(xTicks.get()))
        f.write('\nY ticks:\n')
        f.write(str(yTicks.get()))
        f.write('\nAdd title:\n')
        f.write(str(AddTitle.get().rstrip("\n")))
        f.write('\nAdd axes:\n')
        f.write(str(AddAxes.get().rstrip("\n")))
        f.write('\nLine width:\n')
        f.write(str(Linewidth.get()))
        f.write('\nAxes digits:\n')
        f.write(str(AxesDigits.get()))
        f.write('\nColorbar ticks:\n')
        f.write(str(cbarTicks.get()))
        f.write('\nImage format:\n')
        f.write(str(ImgFormat.get().rstrip("\n")))
        f.write('\nTransparency:\n')
        f.write(str(Alpha.get()))
        f.write('\nColorbar digits:\n')
        f.write(str(cbarDigits.get()))
        f.write('\nColorbar format:\n')
        f.write(str(cbarFormat.get().rstrip("\n")))
        f.write('\nImage tag:\n')
        f.write(str(Tag.get().rstrip("\n")))
        f.write('\nInstant:\n')
        f.write(str(Instant.get().rstrip("\n")))
        f.write('\nPreview field:\n')
        f.write(str(Preview_field.get().rstrip("\n")))
        f.write('\nColor map:\n')
        f.write(str(Color_map.get().rstrip("\n")))
        f.write('\nFigures:\n')
        f.write(str(AllPlots.get()) + '\n')
        f.write(str(ReferenceGrid.get()) + '\n')
        f.write(str(CurrentGrid.get()) + '\n')
        f.write(str(Udisplacement.get()) + '\n')
        f.write(str(Vdisplacement.get()) + '\n')
        f.write(str(UVdisplacement.get()) + '\n')
        f.write(str(Wdisplacement.get()) + '\n')
        f.write(str(exx.get()) + '\n')
        f.write(str(eyy.get()) + '\n')
        f.write(str(exy.get()) + '\n')
        f.write(str(Reconstruction.get()))
        f.write('\nAutomatic axes:\n')
        f.write(str(AllAuto.get()) + '\n')
        f.write(str(UdisplacementAuto.get()) + '\n')
        f.write(str(VdisplacementAuto.get()) + '\n')
        f.write(str(UVdisplacementAuto.get()) + '\n')
        f.write(str(WdisplacementAuto.get()) + '\n')
        f.write(str(exxAuto.get()) + '\n')
        f.write(str(eyyAuto.get()) + '\n')
        f.write(str(exyAuto.get()) + '\n')
        f.write(str(ReconstructionAuto.get()))
        f.write('\nAxes max values:\n')
        f.write(str(UdisplacementMax.get()) + '\n')
        f.write(str(VdisplacementMax.get()) + '\n')
        f.write(str(UVdisplacementMax.get()) + '\n')
        f.write(str(WdisplacementMax.get()) + '\n')
        f.write(str(exxMax.get()) + '\n')
        f.write(str(eyyMax.get()) + '\n')
        f.write(str(exyMax.get()) + '\n')
        f.write(str(ReconstructionMax.get()))
        f.write('\nAxes min values:\n')
        f.write(str(UdisplacementMin.get()) + '\n')
        f.write(str(VdisplacementMin.get()) + '\n')
        f.write(str(UVdisplacementMin.get()) + '\n')
        f.write(str(WdisplacementMin.get()) + '\n')
        f.write(str(exxMin.get()) + '\n')
        f.write(str(eyyMin.get()) + '\n')
        f.write(str(exyMin.get()) + '\n')
        f.write(str(ReconstructionMin.get()))
        f.close()
        console.insert(tk.END,'#############################################################################\n\n')
        console.insert(tk.END, f'Data was successfully saved in {file.get()}\n\n')
        console.see('insert')

    else:
        save_as(menu, console, file, file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm, Valpixel, Strain_window,
         Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
         ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin,  Correlation)

########################################################################################################################
# Save as function - Results log
########################################################################################################################
def save_as(menu, console, file, file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm, Valpixel, Strain_window,
         Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
         ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin,  Correlation):

    file_var.set(True)

    console.insert(tk.END, 'Indicate a .dat file to save the results log\n\n')
    console.see('insert')

    file.set(filedialog.asksaveasfilename())

    menu.title('iCorrVision Post-processing Module '+V+' - '+ntpath.basename(file.get()))

    f = open(file.get(),"w+")

    f.write('iCorrVision Post-processing Module - ' + str(datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")))
    f.write('\nResults folder:\n')
    f.write(str(resultsFolder.get().rstrip("\n")))
    f.write('\nImage folder:\n')
    f.write(str(selectionFolder.get().rstrip("\n")))
    f.write('\nFigure folder:\n')
    f.write(str(figureFolder.get().rstrip("\n")))
    f.write('\nOutput folder:\n')
    f.write(str(outputFolder.get().rstrip("\n")))
    f.write('\nMethod:\n')
    f.write(str(Method.get().rstrip("\n")))
    f.write('\nCorrelation:\n')
    f.write(str(Correlation.get().rstrip("\n")))
    f.write('\nCalibration:\n')
    f.write(str(Valmm.get()) + '\n')
    f.write(str(Valpixel.get()))
    f.write('\nStrain window:\n')
    f.write(str(Strain_window.get()))
    f.write('\nShape function:\n')
    f.write(str(Shape_function.get().rstrip("\n")))
    f.write('\nText Font:\n')
    f.write(str(TextFont.get().rstrip("\n")))
    f.write('\nFont size:\n')
    f.write(str(FontSize.get()))
    f.write('\nX ticks:\n')
    f.write(str(xTicks.get()))
    f.write('\nY ticks:\n')
    f.write(str(yTicks.get()))
    f.write('\nAdd title:\n')
    f.write(str(AddTitle.get().rstrip("\n")))
    f.write('\nAdd axes:\n')
    f.write(str(AddAxes.get().rstrip("\n")))
    f.write('\nLine width:\n')
    f.write(str(Linewidth.get()))
    f.write('\nAxes digits:\n')
    f.write(str(AxesDigits.get()))
    f.write('\nColorbar ticks:\n')
    f.write(str(cbarTicks.get()))
    f.write('\nImage format:\n')
    f.write(str(ImgFormat.get().rstrip("\n")))
    f.write('\nTransparency:\n')
    f.write(str(Alpha.get()))
    f.write('\nColorbar digits:\n')
    f.write(str(cbarDigits.get()))
    f.write('\nColorbar format:\n')
    f.write(str(cbarFormat.get().rstrip("\n")))
    f.write('\nImage tag:\n')
    f.write(str(Tag.get().rstrip("\n")))
    f.write('\nInstant:\n')
    f.write(str(Instant.get().rstrip("\n")))
    f.write('\nPreview field:\n')
    f.write(str(Preview_field.get().rstrip("\n")))
    f.write('\nColor map:\n')
    f.write(str(Color_map.get().rstrip("\n")))
    f.write('\nFigures:\n')
    f.write(str(AllPlots.get()) + '\n')
    f.write(str(ReferenceGrid.get()) + '\n')
    f.write(str(CurrentGrid.get()) + '\n')
    f.write(str(Udisplacement.get()) + '\n')
    f.write(str(Vdisplacement.get()) + '\n')
    f.write(str(UVdisplacement.get()) + '\n')
    f.write(str(Wdisplacement.get()) + '\n')
    f.write(str(exx.get()) + '\n')
    f.write(str(eyy.get()) + '\n')
    f.write(str(exy.get()) + '\n')
    f.write(str(Reconstruction.get()))
    f.write('\nAutomatic axes:\n')
    f.write(str(AllAuto.get()) + '\n')
    f.write(str(UdisplacementAuto.get()) + '\n')
    f.write(str(VdisplacementAuto.get()) + '\n')
    f.write(str(UVdisplacementAuto.get()) + '\n')
    f.write(str(WdisplacementAuto.get()) + '\n')
    f.write(str(exxAuto.get()) + '\n')
    f.write(str(eyyAuto.get()) + '\n')
    f.write(str(exyAuto.get()) + '\n')
    f.write(str(ReconstructionAuto.get()))
    f.write('\nAxes max values:\n')
    f.write(str(UdisplacementMax.get()) + '\n')
    f.write(str(VdisplacementMax.get()) + '\n')
    f.write(str(UVdisplacementMax.get()) + '\n')
    f.write(str(WdisplacementMax.get()) + '\n')
    f.write(str(exxMax.get()) + '\n')
    f.write(str(eyyMax.get()) + '\n')
    f.write(str(exyMax.get()) + '\n')
    f.write(str(ReconstructionMax.get()))
    f.write('\nAxes min values:\n')
    f.write(str(UdisplacementMin.get()) + '\n')
    f.write(str(VdisplacementMin.get()) + '\n')
    f.write(str(UVdisplacementMin.get()) + '\n')
    f.write(str(WdisplacementMin.get()) + '\n')
    f.write(str(exxMin.get()) + '\n')
    f.write(str(eyyMin.get()) + '\n')
    f.write(str(exyMin.get()) + '\n')
    f.write(str(ReconstructionMin.get()))
    f.close()

    console.insert(tk.END, '#############################################################################\n\n')
    console.insert(tk.END, f'Data was successfully saved in {file.get()}\n\n')
    console.see('insert')

########################################################################################################################
# Load function - Results log
########################################################################################################################
def load(menu, console, file, file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm, Valpixel, Strain_window,
         Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
         ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, results_status,
         figure_status, selection_status, save_out_status, Correlation):
    global fileNames

    file_var.set(True)

    file_load = filedialog.askopenfilename()

    menu.title('iCorrVision Post-processing Module '+V+' - '+ntpath.basename(file_load))

    file.set(file_load)

    l = open(file_load,"r")
    w = 2
    lines = l.readlines()
    resultsFolder.set(lines[w].rstrip("\n")); w = w + 2
    selectionFolder.set(lines[w].rstrip("\n")); w = w + 2
    figureFolder.set(lines[w].rstrip("\n")); w = w + 2
    outputFolder.set(lines[w].rstrip("\n")); w = w + 2
    Method.set(lines[w].rstrip("\n")); w = w + 2
    Correlation.set(lines[w].rstrip("\n")); w = w + 2
    Valmm.set(lines[w].rstrip("\n")); w = w + 1
    Valpixel.set(lines[w].rstrip("\n")); w = w + 2
    Strain_window.set(lines[w]); w = w + 2
    Shape_function.set(lines[w].rstrip("\n")); w = w + 2
    TextFont.set(lines[w].rstrip("\n")); w = w + 2
    FontSize.set(lines[w].rstrip("\n")); w = w + 2
    xTicks.set(lines[w].rstrip("\n")); w = w + 2
    yTicks.set(lines[w].rstrip("\n")); w = w + 2
    AddTitle.set(lines[w].rstrip("\n")); w = w + 2
    AddAxes.set(lines[w].rstrip("\n")); w = w + 2
    Linewidth.set(lines[w].rstrip("\n")); w = w + 2
    AxesDigits.set(lines[w].rstrip("\n")); w = w + 2
    cbarTicks.set(lines[w].rstrip("\n")); w = w + 2
    ImgFormat.set(lines[w].rstrip("\n")); w = w + 2
    Alpha.set(lines[w].rstrip("\n")); w = w + 2
    cbarDigits.set(lines[w].rstrip("\n")); w = w + 2
    cbarFormat.set(lines[w].rstrip("\n")); w = w + 2
    Tag.set(lines[w].rstrip("\n")); w = w + 2
    Instant.set(lines[w].rstrip("\n")); w = w + 2
    Preview_field.set(lines[w].rstrip("\n")); w = w + 2
    Color_map.set(lines[w].rstrip("\n")); w = w + 2
    AllPlots.set(int(lines[w])); w = w + 1
    ReferenceGrid.set(int(lines[w])); w = w + 1
    CurrentGrid.set(int(lines[w])); w = w + 1
    Udisplacement.set(int(lines[w])); w = w + 1
    Vdisplacement.set(int(lines[w])); w = w + 1
    UVdisplacement.set(int(lines[w])); w = w + 1
    Wdisplacement.set(int(lines[w])); w = w + 1
    exx.set(int(lines[w])); w = w + 1
    eyy.set(int(lines[w])); w = w + 1
    exy.set(int(lines[w])); w = w + 1
    Reconstruction.set(int(lines[w])); w = w + 2
    AllAuto.set(int(lines[w])); w = w + 1
    UdisplacementAuto.set(int(lines[w])); w = w + 1
    VdisplacementAuto.set(int(lines[w])); w = w + 1
    UVdisplacementAuto.set(int(lines[w])); w = w + 1
    WdisplacementAuto.set(int(lines[w])); w = w + 1
    exxAuto.set(int(lines[w])); w = w + 1
    eyyAuto.set(int(lines[w])); w = w + 1
    exyAuto.set(int(lines[w])); w = w + 1
    ReconstructionAuto.set(int(lines[w])); w = w + 2
    UdisplacementMax.set(lines[w]); w = w + 1
    VdisplacementMax.set(lines[w]); w = w + 1
    UVdisplacementMax.set(lines[w]); w = w + 1
    WdisplacementMax.set(lines[w]); w = w + 1
    exxMax.set(lines[w]); w = w + 1
    eyyMax.set(lines[w]); w = w + 1
    exyMax.set(lines[w]); w = w + 1
    ReconstructionMax.set(lines[w]); w = w + 2
    UdisplacementMin.set(lines[w]); w = w + 1
    VdisplacementMin.set(lines[w]); w = w + 1
    UVdisplacementMin.set(lines[w]); w = w + 1
    WdisplacementMin.set(lines[w]); w = w + 1
    exxMin.set(lines[w]); w = w + 1
    eyyMin.set(lines[w]); w = w + 1
    exyMin.set(lines[w]); w = w + 1
    ReconstructionMin.set(lines[w])

    results_status.configure(bg = '#00cd00') # Green indicator
    console.insert(tk.END, '#############################################################################\n\n')
    console.insert(tk.END, f'Results folder - {resultsFolder.get()}\n\n')
    console.see('insert')

    selection_status.configure(bg='#00cd00')  # Green indicator
    console.insert(tk.END, f'Images folder - {selectionFolder.get()}\n\n')
    console.see('insert')

    fileNames = sorted(glob.glob(selectionFolder.get() + '\\*'), key=stringToList)

    figure_status.configure(bg = '#00cd00') # Green indicator
    console.insert(tk.END, f'All figures will be saved in {figureFolder.get()}\n\n')
    console.see('insert')

    save_out_status.configure(bg='#00cd00')  # Green indicator
    console.insert(tk.END, f'The output fields will be saved in {outputFolder.get()}\n\n')
    console.see('insert')

########################################################################################################################
# Function to clear data and restore GUI
########################################################################################################################
def clear(menu, canvas, console, wDisplacementCheck,  wDisplacementCheckAuto, wDisplacementLabel, ReconstructionCheck,ReconstructionCheckAuto,  results_status, selection_status, figure_status, save_out_status,
    Method, Valmm, Valpixel, Calib_factor, Strain_window, Shape_function, TextFont, FontSize,
    xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks, ImgFormat,
    Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, resultsFolder, selectionFolder,
    figureFolder, outputFolder, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, progression, progression_bar, canvas_text, DIC_status_2D, DIC_status_3D, Correlation):

    global fileNames

    menu.title('iCorrVision Post-processing Module '+V)
    console.delete('1.0', END)

    canvas.configure(image='')

    wDisplacementCheck['fg'] = '#282C34'
    wDisplacementCheckAuto['fg'] = '#282C34'
    wDisplacementLabel['fg'] = '#282C34'
    ReconstructionCheck['fg'] = '#282C34'
    ReconstructionCheckAuto['fg'] = '#282C34'

    DIC_status_2D.configure(bg='#ccd9e1')  # Red indicator
    DIC_status_3D.configure(bg='#ccd9e1')  # Red indicator

    results_status.configure(bg =   'red') # Red indicator
    selection_status.configure(bg = 'red') # Red indicator
    figure_status.configure(bg =    'red') # Red indicator
    save_out_status.configure(bg =    'red') # Red indicator

    Method.set('Select')
    Correlation.set('Select')
    Valmm.set(0.0)
    Valpixel.set(0)
    Calib_factor.set(0.0)
    Strain_window.set(5)
    Shape_function.set('Select')
    TextFont.set('Select')
    FontSize.set('Select')
    xTicks.set('Select')
    yTicks.set('Select')
    AddTitle.set('Select')
    AddAxes.set('Select')
    Linewidth.set('Select')
    AxesDigits.set('Select')
    cbarTicks.set('Select')
    ImgFormat.set('Select')
    Alpha.set(0.0)
    cbarDigits.set('Select')
    cbarFormat.set('Select')
    Tag.set('')
    Instant.set('ex: 2,3,4')
    Preview_field.set('Select')
    Color_map.set('Select')

    resultsFolder.set('')
    selectionFolder.set('')
    figureFolder.set('')
    outputFolder.set('')

    AllPlots.set(0)
    ReferenceGrid.set(0)
    CurrentGrid.set(0)
    Udisplacement.set(0)
    Vdisplacement.set(0)
    UVdisplacement.set(0)
    Wdisplacement.set(0)
    exx.set(0)
    eyy.set(0)
    exy.set(0)
    Reconstruction.set(0)
    AllAuto.set(0)
    UdisplacementAuto.set(0)
    VdisplacementAuto.set(0)
    UVdisplacementAuto.set(0)
    WdisplacementAuto.set(0)
    exxAuto.set(0)
    eyyAuto.set(0)
    exyAuto.set(0)
    ReconstructionAuto.set(0)
    UdisplacementMax.set(0.0)
    VdisplacementMax.set(0.0)
    UVdisplacementMax.set(0.0)
    WdisplacementMax.set(0.0)
    exxMax.set(0.0)
    eyyMax.set(0.0)
    exyMax.set(0.0)
    ReconstructionMax.set(0.0)
    UdisplacementMin.set(0.0)
    VdisplacementMin.set(0.0)
    UVdisplacementMin.set(0.0)
    WdisplacementMin.set(0.0)
    exxMin.set(0.0)
    eyyMin.set(0.0)
    exyMin.set(0.0)
    ReconstructionMin.set(0.0)

    progression.coords(progression_bar, 0, 0, 0, 25); progression.itemconfig(canvas_text, text='')

    console.insert(tk.END,
                   f'###################################################################  {V}\n\n'
                   '                 **  iCorrVision Post-processing Module **                   \n\n'
                   '#############################################################################\n\n')
    console.see('insert')

    try:
        del fileNames
    except NameError:
        pass

########################################################################################################################
# Function to initialize the process
########################################################################################################################
def plot_figures(menu, console, file, file_var, canvas, wDisplacementCheck, wDisplacementCheckAuto, wDisplacementLabel, ReconstructionCheck, ReconstructionCheckAuto, progression, progression_bar, canvas_text, resultsFolder,
                selectionFolder, figureFolder, outputFolder, Valmm, Valpixel, Instant, Shape_function, Strain_window, Preview_field, Preview,
                Preview_field_dict, Color_map,color_map_dict,Method, Tag, Alpha, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, AxesDigits,
                cbarTicks, ImgFormat, cbarDigits, cbarFormat, cbs_auto, cbs_plot, var_Min, var_Max, DIC_status_2D, DIC_status_3D, Linewidth,
                 AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx,
                 eyy, exy, Reconstruction, AllAuto,
                 UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto,
                 ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
                 WdisplacementMax,
                 exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin,
                 WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, Correlation):

    global fileNames

    try:
        fileNames
    except NameError:
        messagebox.showerror('Error','Please load file or select the results and figures folder!')
    else:

        save(menu, console, file, file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm,
             Valpixel, Strain_window,
             Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
             ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, Correlation)

        t = Thread(target=plot, args=(
        console, canvas, wDisplacementCheck, wDisplacementCheckAuto,  wDisplacementLabel, ReconstructionCheck, ReconstructionCheckAuto,progression, progression_bar, canvas_text,
        resultsFolder,
        figureFolder, outputFolder, Valmm, Valpixel, Instant, Shape_function, Strain_window, Preview_field, Preview,
        Preview_field_dict,Color_map,color_map_dict, Method, Tag, Alpha, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, AxesDigits,
        cbarTicks, ImgFormat, cbarDigits, cbarFormat, cbs_auto, cbs_plot, var_Min, var_Max, DIC_status_2D,
        DIC_status_3D, Linewidth, Correlation, selectionFolder))
        t.setDaemon(True)
        t.start()

########################################################################################################################
# Function to automatically calculate the calibration factor
########################################################################################################################
def callback(Valmm, Valpixel, Calib_factor):
    if Valmm.get() != "" and Valmm.get() > 0.0:
        vmm = Valmm.get()
        vpixel = Valpixel.get()
        Calib_factor.set(vpixel/vmm)

########################################################################################################################
# Bilinear shape function - 4 unknowns
########################################################################################################################
def fQ4(data, C1, C2, C3, C4):
    x = data[0]
    y = data[1]
    return C1 + C2 * x + C3 * y + C4 * x * y

########################################################################################################################
# Biquadratic shape function - 9 unknowns
########################################################################################################################
def fQ9(data, C1, C2, C3, C4, C5, C6, C7, C8, C9):
    x = data[0]
    y = data[1]
    return C1 + C2 * x + C3 * y + C4 * x * y + C5 * x ** 2 + C6 * y ** 2 + C7 * y * x ** 2 + C8 * x * y ** 2 + C9 * \
           (x ** 2) * (y ** 2)

########################################################################################################################
# Function to calculate the data:
########################################################################################################################
def plot(console, canvas, wDisplacementCheck, wDisplacementCheckAuto, wDisplacementLabel, ReconstructionCheck, ReconstructionCheckAuto, progression, progression_bar, canvas_text, resultsFolder,
         figureFolder, outputFolder, Valmm, Valpixel, Instant, Shape_function, Strain_window, Preview_field, Preview,
         Preview_field_dict,Color_map,color_map_dict, Method, Tag, Alpha, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, AxesDigits,
         cbarTicks, ImgFormat, cbarDigits, cbarFormat, cbs_auto, cbs_plot, var_Min, var_Max, DIC_status_2D, DIC_status_3D, Linewidth, Correlation, selectionFolder):

    global fileNames

    # Color map:
    color_map_var = ['Blues','Greens','Greys','Oranges','Reds','afmhot','autumn','bone','copper','hot','hsv','jet','winter']

    console.insert(tk.END, '#############################################################################\n\n')

    console.insert(tk.END, 'Process has been started. Please wait!\n\n')
    console.see('insert')

    # 3D correlation test:
    wm = sorted(glob.glob(resultsFolder.get() + '/wm*.dat'), key=stringToList)

    # 3D data test variable:
    test_3D = False

    if wm == []:
        wDisplacementCheck['fg'] = 'red'
        wDisplacementCheckAuto['fg'] = 'red'
        wDisplacementLabel['fg'] = 'red'
        ReconstructionCheck['fg'] = 'red'
        ReconstructionCheckAuto['fg'] = 'red'
        console.insert(tk.END, '2D data was found! The w-displacement and 3D reconstruction will be removed from the calculation.\n\n')
        console.see('insert')
        cbs_auto[3].set(0)
        cbs_auto[7].set(0)
        cbs_plot[5].set(0)
        cbs_plot[9].set(0)
        DIC_status_2D.configure(bg='#00cd00')  # Red indicator

        fileNames = sorted(glob.glob(selectionFolder.get() + '\\*'), key=stringToList)

        preview_var = ['umi_mesh', 'vmi_mesh', 'wmi_mesh', 'uvmi_mesh', 'exx', 'eyy', 'exy', 'zmi_mesh']

        xm = sorted(glob.glob(resultsFolder.get() + '/xm*.dat'), key=stringToList)
        ym = sorted(glob.glob(resultsFolder.get() + '/ym*.dat'), key=stringToList)
        um = sorted(glob.glob(resultsFolder.get() + '/um*.dat'), key=stringToList)
        vm = sorted(glob.glob(resultsFolder.get() + '/vm*.dat'), key=stringToList)

        # Calibration factor:
        Cal = Valmm.get() / Valpixel.get()

        test_3D = False
    else:
        console.insert(tk.END, '3D data was found!\n\n')
        console.see('insert')
        DIC_status_3D.configure(bg='#00cd00')  # Red indicator

        fileNames = sorted(glob.glob(selectionFolder.get() + '\\Left\\*'), key=stringToList)

        preview_var = ['umi_meshSPCS', 'vmi_meshSPCS', 'wmi_meshSPCS', 'uvmi_meshSPCS', 'exxSPCS', 'eyySPCS', 'exySPCS', 'zmi_meshSPCS']

        xmWCS = sorted(glob.glob(resultsFolder.get() + '/xmWCS*.dat'), key=stringToList)
        ymWCS = sorted(glob.glob(resultsFolder.get() + '/ymWCS*.dat'), key=stringToList)
        zmWCS = sorted(glob.glob(resultsFolder.get() + '/zmWCS*.dat'), key=stringToList)
        umWCS = sorted(glob.glob(resultsFolder.get() + '/umWCS*.dat'), key=stringToList)
        vmWCS = sorted(glob.glob(resultsFolder.get() + '/vmWCS*.dat'), key=stringToList)
        wmWCS = sorted(glob.glob(resultsFolder.get() + '/wmWCS*.dat'), key=stringToList)
        xmSPCS = sorted(glob.glob(resultsFolder.get() + '/xmSPCS*.dat'), key=stringToList)
        ymSPCS = sorted(glob.glob(resultsFolder.get() + '/ymSPCS*.dat'), key=stringToList)
        zmSPCS = sorted(glob.glob(resultsFolder.get() + '/zmSPCS*.dat'), key=stringToList)
        umSPCS = sorted(glob.glob(resultsFolder.get() + '/umSPCS*.dat'), key=stringToList)
        vmSPCS = sorted(glob.glob(resultsFolder.get() + '/vmSPCS*.dat'), key=stringToList)
        wmSPCS = sorted(glob.glob(resultsFolder.get() + '/wmSPCS*.dat'), key=stringToList)
        xmL = sorted(glob.glob(resultsFolder.get() + '/xmL*.dat'), key=stringToList)
        ymL = sorted(glob.glob(resultsFolder.get() + '/ymL*.dat'), key=stringToList)

        # For 3D-DIC, calibration is performed using a calibration target.
        Cal = 1

        test_3D = True

    auto_var = []
    for cba in cbs_auto:
        auto_var.extend([cba.get()])

    plot_var = []
    for cba in cbs_plot:
        plot_var.extend([cba.get()])

    min_var = []
    for cba in var_Min:
        min_var.extend([cba.get()])

    max_var = []
    for cba in var_Max:
        max_var.extend([cba.get()])

    # Number of evaluated instants using iCorrVision-2D or iCorrVision-3D:
    if test_3D:
        nImages = len(umWCS)
    else:
        nImages = len(um)

    console.insert(tk.END, f'{nImages} instants were evaluated!\n\n')
    console.see('insert')

    console.insert(tk.END, 'Collecting DIC results -')
    console.see('insert')

    # Number of elements in horizontal and vertical direction:
    if test_3D:
        Ney, Nex = np.genfromtxt(xmWCS[0]).shape
    else:
        Ney, Nex = np.genfromtxt(xm[0]).shape

    # Variables declaration for 3D-DIC and 2D-DIC:
    if test_3D:
        xriWCS = np.zeros((nImages + 1, Ney, Nex))
        yriWCS = np.zeros((nImages + 1, Ney, Nex))
        zriWCS = np.zeros((nImages + 1, Ney, Nex))
        umiWCS = np.zeros((nImages + 1, Ney, Nex))
        vmiWCS = np.zeros((nImages + 1, Ney, Nex))
        wmiWCS = np.zeros((nImages + 1, Ney, Nex))

        xriSPCS = np.zeros((nImages + 1, Ney, Nex))
        yriSPCS = np.zeros((nImages + 1, Ney, Nex))
        zriSPCS = np.zeros((nImages + 1, Ney, Nex))
        umiSPCS = np.zeros((nImages + 1, Ney, Nex))
        vmiSPCS = np.zeros((nImages + 1, Ney, Nex))
        wmiSPCS = np.zeros((nImages + 1, Ney, Nex))

        xriL = np.zeros((nImages + 1, Ney, Nex))
        yriL = np.zeros((nImages + 1, Ney, Nex))

        xriWCS[0][:][:] = np.genfromtxt(xmWCS[0])
        yriWCS[0][:][:] = np.genfromtxt(ymWCS[0])
        zriWCS[0][:][:] = np.genfromtxt(zmWCS[0])
        umiWCS[0][:][:] = np.genfromtxt(umWCS[0])
        vmiWCS[0][:][:] = np.genfromtxt(vmWCS[0])
        wmiWCS[0][:][:] = np.genfromtxt(wmWCS[0])

        xriSPCS[0][:][:] = np.genfromtxt(xmSPCS[0])
        yriSPCS[0][:][:] = np.genfromtxt(ymSPCS[0])
        zriSPCS[0][:][:] = np.genfromtxt(zmSPCS[0])
        umiSPCS[0][:][:] = np.genfromtxt(umSPCS[0])
        vmiSPCS[0][:][:] = np.genfromtxt(vmSPCS[0])
        wmiSPCS[0][:][:] = np.genfromtxt(wmSPCS[0])

        xriL[0][:][:] = np.genfromtxt(xmL[0])
        yriL[0][:][:] = np.genfromtxt(ymL[0])

    else:
        xri = np.zeros((nImages + 1, Ney, Nex))
        yri = np.zeros((nImages + 1, Ney, Nex))

        umi = np.zeros((nImages + 1, Ney, Nex))
        vmi = np.zeros((nImages + 1, Ney, Nex))

        dudx = np.zeros((nImages + 1, Ney, Nex))
        dudy = np.zeros((nImages + 1, Ney, Nex))
        dvdx = np.zeros((nImages + 1, Ney, Nex))
        dvdy = np.zeros((nImages + 1, Ney, Nex))

        xri[0][:][:] = np.genfromtxt(xm[0])
        yri[0][:][:] = np.genfromtxt(ym[0])
        umi[0][:][:] = np.genfromtxt(um[0])
        vmi[0][:][:] = np.genfromtxt(vm[0])

    for k in range(1, nImages):

        if test_3D:
            xriWCS[k][:][:] = np.genfromtxt(xmWCS[k])
            yriWCS[k][:][:] = np.genfromtxt(ymWCS[k])
            zriWCS[k][:][:] = np.genfromtxt(zmWCS[k])
            xriSPCS[k][:][:] = np.genfromtxt(xmSPCS[k])
            yriSPCS[k][:][:] = np.genfromtxt(ymSPCS[k])
            zriSPCS[k][:][:] = np.genfromtxt(zmSPCS[k])
            xriL[k][:][:] = np.genfromtxt(xmL[k])
            yriL[k][:][:] = np.genfromtxt(ymL[k])

            if Correlation.get() == 'Incremental':
                umiWCS[k][:][:] = umiWCS[k - 1][:][:] + np.genfromtxt(umWCS[k])
                vmiWCS[k][:][:] = vmiWCS[k - 1][:][:] + np.genfromtxt(vmWCS[k])
                wmiWCS[k][:][:] = wmiWCS[k - 1][:][:] + np.genfromtxt(wmWCS[k])
                umiSPCS[k][:][:] = umiSPCS[k - 1][:][:] + np.genfromtxt(umSPCS[k])
                vmiSPCS[k][:][:] = vmiSPCS[k - 1][:][:] + np.genfromtxt(vmSPCS[k])
                wmiSPCS[k][:][:] = wmiSPCS[k - 1][:][:] + np.genfromtxt(wmSPCS[k])

            else:
                umiWCS[k][:][:] = np.genfromtxt(umWCS[k])
                vmiWCS[k][:][:] = np.genfromtxt(vmWCS[k])
                wmiWCS[k][:][:] = np.genfromtxt(wmWCS[k])
                umiSPCS[k][:][:] = np.genfromtxt(umSPCS[k])
                vmiSPCS[k][:][:] = np.genfromtxt(vmSPCS[k])
                wmiSPCS[k][:][:] = np.genfromtxt(wmSPCS[k])

        else:
            xri[k][:][:] = np.genfromtxt(xm[k])
            yri[k][:][:] = np.genfromtxt(ym[k])

            if Correlation.get() == 'Incremental':
                umi[k][:][:] = umi[k-1][:][:]+np.genfromtxt(um[k])
                vmi[k][:][:] = vmi[k-1][:][:]+np.genfromtxt(vm[k])

            else:
                umi[k][:][:] = np.genfromtxt(um[k])
                vmi[k][:][:] = np.genfromtxt(vm[k])

        green_length = int(515*((k+1)/nImages))
        progression.coords(progression_bar, 0, 0, green_length, 25); progression.itemconfig(canvas_text, text=f'{k+1} of {nImages} - {100*(k+1)/nImages:.2f}%')

    console.insert(tk.END, ' Done\n\n')
    console.see('insert')

    # Center point of strain window. The strain window must be an odd number and integer (pixels).
    sw_step = Strain_window.get()/2-0.5

    # Mesh amplification for boundary analysis - nan values - the least squares regression is performed over the xri domain:
    if test_3D:
        xMeshWCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        yMeshWCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        zMeshWCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        uMeshWCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        vMeshWCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        wMeshWCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        xMeshSPCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        yMeshSPCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        zMeshSPCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        uMeshSPCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        vMeshSPCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        wMeshSPCS = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        xMeshWCS[:] = np.nan
        yMeshWCS[:] = np.nan
        zMeshWCS[:] = np.nan
        uMeshWCS[:] = np.nan
        vMeshWCS[:] = np.nan
        wMeshWCS[:] = np.nan
        xMeshSPCS[:] = np.nan
        yMeshSPCS[:] = np.nan
        zMeshSPCS[:] = np.nan
        uMeshSPCS[:] = np.nan
        vMeshSPCS[:] = np.nan
        wMeshSPCS[:] = np.nan

    else:
        xMesh = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        yMesh = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        uMesh = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        vMesh = np.empty((nImages + 1, int(Ney + sw_step * 2), int(Nex + sw_step * 2),))
        xMesh[:] = np.nan
        yMesh[:] = np.nan
        uMesh[:] = np.nan
        vMesh[:] = np.nan

    # Construction of new Mesh for 2D-DIC and 3D-DIC post processing:
    if test_3D:
        for k in range(0, nImages):
            for i in range(int(sw_step), int(Ney + sw_step)):
                for j in range(int(sw_step), int(Nex + sw_step)):
                    xMeshWCS[k][i][j] = xriWCS[k][int(i - sw_step)][int(j - sw_step)]
                    yMeshWCS[k][i][j] = yriWCS[k][int(i - sw_step)][int(j - sw_step)]
                    zMeshWCS[k][i][j] = zriWCS[k][int(i - sw_step)][int(j - sw_step)]
                    uMeshWCS[k][i][j] = umiWCS[k][int(i - sw_step)][int(j - sw_step)]
                    vMeshWCS[k][i][j] = vmiWCS[k][int(i - sw_step)][int(j - sw_step)]
                    wMeshWCS[k][i][j] = wmiWCS[k][int(i - sw_step)][int(j - sw_step)]
                    xMeshSPCS[k][i][j] = xriSPCS[k][int(i - sw_step)][int(j - sw_step)]
                    yMeshSPCS[k][i][j] = yriSPCS[k][int(i - sw_step)][int(j - sw_step)]
                    zMeshSPCS[k][i][j] = zriSPCS[k][int(i - sw_step)][int(j - sw_step)]
                    uMeshSPCS[k][i][j] = umiSPCS[k][int(i - sw_step)][int(j - sw_step)]
                    vMeshSPCS[k][i][j] = vmiSPCS[k][int(i - sw_step)][int(j - sw_step)]
                    wMeshSPCS[k][i][j] = wmiSPCS[k][int(i - sw_step)][int(j - sw_step)]


    else:
        for k in range(0, nImages):
            for i in range(int(sw_step), int(Ney + sw_step)):
                for j in range(int(sw_step), int(Nex + sw_step)):
                    xMesh[k][i][j] = xri[k][int(i - sw_step)][int(j - sw_step)]
                    yMesh[k][i][j] = yri[k][int(i - sw_step)][int(j - sw_step)]
                    uMesh[k][i][j] = umi[k][int(i - sw_step)][int(j - sw_step)]
                    vMesh[k][i][j] = vmi[k][int(i - sw_step)][int(j - sw_step)]


    if test_3D:
        umi_meshWCS = np.zeros((nImages + 1, Ney, Nex,))
        vmi_meshWCS = np.zeros((nImages + 1, Ney, Nex,))
        wmi_meshWCS = np.zeros((nImages + 1, Ney, Nex,))
        zmi_meshWCS = np.zeros((nImages + 1, Ney, Nex,))
        uvmi_meshWCS = np.zeros((nImages + 1, Ney, Nex,))
        umi_meshWCS[:] = np.nan
        vmi_meshWCS[:] = np.nan
        wmi_meshWCS[:] = np.nan
        zmi_meshWCS[:] = np.nan
        uvmi_meshWCS[:] = np.nan

        umi_meshSPCS = np.zeros((nImages + 1, Ney, Nex,))
        vmi_meshSPCS = np.zeros((nImages + 1, Ney, Nex,))
        wmi_meshSPCS = np.zeros((nImages + 1, Ney, Nex,))
        zmi_meshSPCS = np.zeros((nImages + 1, Ney, Nex,))
        uvmi_meshSPCS = np.zeros((nImages + 1, Ney, Nex,))
        umi_meshSPCS[:] = np.nan
        vmi_meshSPCS[:] = np.nan
        wmi_meshSPCS[:] = np.nan
        zmi_meshSPCS[:] = np.nan
        uvmi_meshSPCS[:] = np.nan

        exxWCS = np.zeros((nImages + 1, Ney, Nex,))
        eyyWCS = np.zeros((nImages + 1, Ney, Nex,))
        exyWCS = np.zeros((nImages + 1, Ney, Nex,))
        exxWCS[:] = np.nan
        eyyWCS[:] = np.nan
        exyWCS[:] = np.nan

        dudxWCS = np.zeros((nImages + 1, Ney, Nex,))
        dudyWCS = np.zeros((nImages + 1, Ney, Nex,))
        dvdxWCS = np.zeros((nImages + 1, Ney, Nex,))
        dvdyWCS = np.zeros((nImages + 1, Ney, Nex,))
        dudxWCS[:] = np.nan
        dudyWCS[:] = np.nan
        dvdxWCS[:] = np.nan
        dvdyWCS[:] = np.nan

        exxSPCS = np.zeros((nImages + 1, Ney, Nex,))
        eyySPCS = np.zeros((nImages + 1, Ney, Nex,))
        exySPCS = np.zeros((nImages + 1, Ney, Nex,))
        exxSPCS[:] = np.nan
        eyySPCS[:] = np.nan
        exySPCS[:] = np.nan

        dudxSPCS = np.zeros((nImages + 1, Ney, Nex,))
        dudySPCS = np.zeros((nImages + 1, Ney, Nex,))
        dvdxSPCS = np.zeros((nImages + 1, Ney, Nex,))
        dvdySPCS = np.zeros((nImages + 1, Ney, Nex,))
        dudxSPCS[:] = np.nan
        dudySPCS[:] = np.nan
        dvdxSPCS[:] = np.nan
        dvdySPCS[:] = np.nan

    else:
        umi_mesh = np.zeros((nImages + 1, Ney, Nex,))
        vmi_mesh = np.zeros((nImages + 1, Ney, Nex,))
        uvmi_mesh = np.zeros((nImages + 1, Ney, Nex,))
        umi_mesh[:] = np.nan
        vmi_mesh[:] = np.nan
        uvmi_mesh[:] = np.nan

        exx = np.zeros((nImages + 1, Ney, Nex,))
        eyy = np.zeros((nImages + 1, Ney, Nex,))
        exy = np.zeros((nImages + 1, Ney, Nex,))
        exx[:] = np.nan
        eyy[:] = np.nan
        exy[:] = np.nan

        dudx = np.zeros((nImages + 1, Ney, Nex,))
        dudy = np.zeros((nImages + 1, Ney, Nex,))
        dvdx = np.zeros((nImages + 1, Ney, Nex,))
        dvdy = np.zeros((nImages + 1, Ney, Nex,))
        dudx[:] = np.nan
        dudy[:] = np.nan
        dvdx[:] = np.nan
        dvdy[:] = np.nan

    if test_3D:
        filexWCS = 'xmWCS{:02d}.dat'
        fileyWCS = 'ymWCS{:02d}.dat'
        filezWCS = 'zmWCS{:02d}.dat'
        fileuWCS = 'umWCS{:02d}.dat'
        filevWCS = 'vmWCS{:02d}.dat'
        fileuvWCS = 'uvmWCS{:02d}.dat'
        filewWCS = 'wmWCS{:02d}.dat'
        filexSPCS = 'xmSPCS{:02d}.dat'
        fileySPCS = 'ymSPCS{:02d}.dat'
        filezSPCS = 'zmSPCS{:02d}.dat'
        fileuSPCS = 'umSPCS{:02d}.dat'
        filevSPCS = 'vmSPCS{:02d}.dat'
        fileuvSPCS = 'uvmSPCS{:02d}.dat'
        filewSPCS = 'wmSPCS{:02d}.dat'

        np.savetxt(f'{outputFolder.get()}/{filexWCS.format(1)}', xriWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileyWCS.format(1)}', yriWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filezWCS.format(1)}', zriWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileuWCS.format(1)}', umi_meshWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filevWCS.format(1)}', vmi_meshWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileuvWCS.format(1)}', uvmi_meshWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filewWCS.format(1)}', wmi_meshWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filexSPCS.format(1)}', xriSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileySPCS.format(1)}', yriSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filezSPCS.format(1)}', zriSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileuSPCS.format(1)}', umi_meshSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filevSPCS.format(1)}', vmi_meshSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileuvSPCS.format(1)}', uvmi_meshSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filewSPCS.format(1)}', wmi_meshSPCS[0][:][:], fmt='%.10e')

        filexL = 'xmL{:02d}.dat'
        fileyL = 'ymL{:02d}.dat'
        np.savetxt(f'{outputFolder.get()}/{filexL.format(1)}', xriL[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileyL.format(1)}', yriL[0][:][:], fmt='%.10e')

        fileexxWCS = 'exxWCS{:02d}.dat'
        fileexyWCS = 'exyWCS{:02d}.dat'
        fileeyyWCS = 'eyyWCS{:02d}.dat'
        filedudxWCS = 'dudxWCS{:02d}.dat'
        filedudyWCS = 'dudyWCS{:02d}.dat'
        filedvdxWCS = 'dvdxWCS{:02d}.dat'
        filedvdyWCS = 'dvdyWCS{:02d}.dat'
        np.savetxt(f'{outputFolder.get()}/{fileexxWCS.format(1)}', exxWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileexyWCS.format(1)}', exyWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileeyyWCS.format(1)}', eyyWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedudxWCS.format(1)}', dudxWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedudyWCS.format(1)}', dudyWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedvdxWCS.format(1)}', dvdxWCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedvdyWCS.format(1)}', dvdyWCS[0][:][:], fmt='%.10e')

        fileexxSPCS = 'exxSPCS{:02d}.dat'
        fileexySPCS = 'exySPCS{:02d}.dat'
        fileeyySPCS = 'eyySPCS{:02d}.dat'
        filedudxSPCS = 'dudxSPCS{:02d}.dat'
        filedudySPCS = 'dudySPCS{:02d}.dat'
        filedvdxSPCS = 'dvdxSPCS{:02d}.dat'
        filedvdySPCS = 'dvdySPCS{:02d}.dat'
        np.savetxt(f'{outputFolder.get()}/{fileexxSPCS.format(1)}', exxSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileexySPCS.format(1)}', exySPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileeyySPCS.format(1)}', eyySPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedudxSPCS.format(1)}', dudxSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedudySPCS.format(1)}', dudySPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedvdxSPCS.format(1)}', dvdxSPCS[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedvdySPCS.format(1)}', dvdySPCS[0][:][:], fmt='%.10e')

    else:

        filex = 'xm{:02d}.dat'
        filey = 'ym{:02d}.dat'
        fileu = 'um{:02d}.dat'
        filev = 'vm{:02d}.dat'
        fileuv = 'uvm{:02d}.dat'
        np.savetxt(f'{outputFolder.get()}/{filex.format(1)}', xri[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filey.format(1)}', yri[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileu.format(1)}', umi_mesh[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filev.format(1)}', vmi_mesh[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileuv.format(1)}', uvmi_mesh[0][:][:], fmt='%.10e')

        fileexx = 'exx{:02d}.dat'
        fileexy = 'exy{:02d}.dat'
        fileeyy = 'eyy{:02d}.dat'
        filedudx = 'dudx{:02d}.dat'
        filedudy = 'dudy{:02d}.dat'
        filedvdx = 'dvdx{:02d}.dat'
        filedvdy = 'dvdy{:02d}.dat'
        np.savetxt(f'{outputFolder.get()}/{fileexx.format(1)}', exx[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileexy.format(1)}', exy[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{fileeyy.format(1)}', eyy[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedudx.format(1)}', dudx[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedudy.format(1)}', dudy[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedvdx.format(1)}', dvdx[0][:][:], fmt='%.10e')
        np.savetxt(f'{outputFolder.get()}/{filedvdy.format(1)}', dvdy[0][:][:], fmt='%.10e')

    if test_3D:

        for k in range(0, nImages):

            console.insert(tk.END, f'Calculating instant {k+1} -')
            console.see('insert')

            for i in range(int(sw_step), int(Ney + sw_step)):
                for j in range(int(sw_step), int(Nex + sw_step)):
                    if ~np.isnan(xMeshWCS[k][i][j]):

                        # Point (x0,y0,z0) in WCS
                        x0WCS = xMeshWCS[0][i][j];
                        y0WCS = yMeshWCS[0][i][j];
                        z0WCS = zMeshWCS[0][i][j];

                        # Point (x0,y0,z0) in SPCS
                        x0SPCS = xMeshSPCS[0][i][j];
                        y0SPCS = yMeshSPCS[0][i][j];
                        z0SPCS = zMeshSPCS[0][i][j];

                        # Points (xx0,yy0,zz0) inside strain window in WCS
                        xx0WCS = xMeshWCS[0][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()
                        yy0WCS = yMeshWCS[0][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()
                        zz0WCS = zMeshWCS[0][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()

                        # Points (xx0,yy0,zz0) inside strain window in SPCS
                        xx0SPCS = xMeshSPCS[0][int(i - sw_step):int(i + sw_step),int(j - sw_step):int(j + sw_step)].flatten()
                        yy0SPCS = yMeshSPCS[0][int(i - sw_step):int(i + sw_step),int(j - sw_step):int(j + sw_step)].flatten()
                        zz0SPCS = zMeshSPCS[0][int(i - sw_step):int(i + sw_step),int(j - sw_step):int(j + sw_step)].flatten()

                        # Displacement of points (xx0,yy0) in WCS
                        uu0WCS = uMeshWCS[k][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()
                        vv0WCS = vMeshWCS[k][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()
                        ww0WCS = wMeshWCS[k][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()

                        # Displacement of points (xx0,yy0) in SPCS
                        uu0SPCS = uMeshSPCS[k][int(i - sw_step):int(i + sw_step),int(j - sw_step):int(j + sw_step)].flatten()
                        vv0SPCS = vMeshSPCS[k][int(i - sw_step):int(i + sw_step),int(j - sw_step):int(j + sw_step)].flatten()
                        ww0SPCS = wMeshSPCS[k][int(i - sw_step):int(i + sw_step),int(j - sw_step):int(j + sw_step)].flatten()

                        # Removing nan values inside strain window in WCS
                        xx0WCS = xx0WCS[~np.isnan(xx0WCS)]
                        yy0WCS = yy0WCS[~np.isnan(yy0WCS)]
                        zz0WCS = zz0WCS[~np.isnan(zz0WCS)]
                        uu0WCS = uu0WCS[~np.isnan(uu0WCS)]
                        vv0WCS = vv0WCS[~np.isnan(vv0WCS)]
                        ww0WCS = ww0WCS[~np.isnan(ww0WCS)]

                        # Removing nan values inside strain window in SPCS
                        xx0SPCS = xx0SPCS[~np.isnan(xx0SPCS)]
                        yy0SPCS = yy0SPCS[~np.isnan(yy0SPCS)]
                        zz0SPCS = zz0SPCS[~np.isnan(zz0SPCS)]
                        uu0SPCS = uu0SPCS[~np.isnan(uu0SPCS)]
                        vv0SPCS = vv0SPCS[~np.isnan(vv0SPCS)]
                        ww0SPCS = ww0SPCS[~np.isnan(ww0SPCS)]

                        if Shape_function.get() == 'None':
                            # Displacements on point (x0,y0,z0) in WCS
                            umi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = uMeshWCS[k][i][j]
                            vmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = vMeshWCS[k][i][j]
                            zmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = zMeshWCS[k][i][j]
                            wmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = wMeshWCS[k][i][j]

                            # Displacement of points (xx0,yy0) in SPCS
                            umi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = uMeshSPCS[k][i][j]
                            vmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = vMeshSPCS[k][i][j]
                            zmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = zMeshSPCS[k][i][j]
                            wmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = wMeshSPCS[k][i][j]



                        if Shape_function.get() == 'Bilinear':
                            # Non-linear least squares using shape functions - p0 is the initial guess for the parameters in WCS
                            fit_u, pcou = scipy.optimize.curve_fit(fQ4, [xx0WCS, yy0WCS], uu0WCS, p0=[0, 0, 0, 0])
                            fit_v, pcov = scipy.optimize.curve_fit(fQ4, [xx0WCS, yy0WCS], vv0WCS, p0=[0, 0, 0, 0])
                            fit_w, pcow = scipy.optimize.curve_fit(fQ4, [xx0WCS, yy0WCS], ww0WCS, p0=[0, 0, 0, 0])
                            fit_z, pcoz = scipy.optimize.curve_fit(fQ4, [xx0WCS, yy0WCS], zz0WCS, p0=[0, 0, 0, 0])

                            # Corrected displacements on point (x0,y0,z0) in WCS
                            umi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = fit_u[0] + fit_u[1] * x0WCS + fit_u[2] * y0WCS + fit_u[3] * x0WCS * y0WCS
                            vmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = fit_v[0] + fit_v[1] * x0WCS + fit_v[2] * y0WCS + fit_v[3] * x0WCS * y0WCS
                            wmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = fit_w[0] + fit_w[1] * x0WCS + fit_w[2] * y0WCS + fit_w[3] * x0WCS * y0WCS
                            zmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = fit_z[0] + fit_z[1] * x0WCS + fit_z[2] * y0WCS + fit_z[3] * x0WCS * y0WCS

                            # Gradients using the estimated parameters in WCS
                            dudxWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_u[1] + fit_u[3] * y0WCS
                            dudyWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_u[2] + fit_u[3] * x0WCS
                            dvdxWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_v[1] + fit_v[3] * y0WCS
                            dvdyWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_v[2] + fit_v[3] * x0WCS

                            # Non-linear least squares using shape functions - p0 is the initial guess for the parameters in SPCS
                            fit_u, pcou = scipy.optimize.curve_fit(fQ4, [xx0SPCS, yy0SPCS], uu0SPCS, p0=[0, 0, 0, 0])
                            fit_v, pcov = scipy.optimize.curve_fit(fQ4, [xx0SPCS, yy0SPCS], vv0SPCS, p0=[0, 0, 0, 0])
                            fit_w, pcow = scipy.optimize.curve_fit(fQ4, [xx0SPCS, yy0SPCS], ww0SPCS, p0=[0, 0, 0, 0])
                            fit_z, pcoz = scipy.optimize.curve_fit(fQ4, [xx0SPCS, yy0SPCS], zz0SPCS, p0=[0, 0, 0, 0])

                            # Corrected displacements on point (x0,y0,z0) in SPCS
                            umi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_u[0] + fit_u[1] * x0SPCS + fit_u[2] * y0SPCS + fit_u[3] * x0SPCS * y0SPCS
                            vmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_v[0] + fit_v[1] * x0SPCS + fit_v[2] * y0SPCS + fit_v[3] * x0SPCS * y0SPCS
                            wmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_w[0] + fit_w[1] * x0SPCS + fit_w[2] * y0SPCS + fit_w[3] * x0SPCS * y0SPCS
                            zmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_z[0] + fit_z[1] * x0SPCS + fit_z[2] * y0SPCS + fit_z[3] * x0SPCS * y0SPCS

                            # Gradients using the estimated parameters in SPCS
                            dudxSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_u[1] + fit_u[3] * y0SPCS
                            dudySPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_u[2] + fit_u[3] * x0SPCS
                            dvdxSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_v[1] + fit_v[3] * y0SPCS
                            dvdySPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_v[2] + fit_v[3] * x0SPCS

                        if Shape_function.get() == 'Biquadratic':
                            # Non-linear least squares using shape functions - p0 is the initial guess for the parameters in WCS
                            fit_u, pcou = scipy.optimize.curve_fit(fQ9, [xx0WCS, yy0WCS], uu0WCS, p0 = [0,0,0,0,0,0,0,0,0])
                            fit_v, pcov = scipy.optimize.curve_fit(fQ9, [xx0WCS, yy0WCS], vv0WCS, p0 = [0,0,0,0,0,0,0,0,0])
                            fit_w, pcow = scipy.optimize.curve_fit(fQ9, [xx0WCS, yy0WCS], ww0WCS, p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])
                            fit_z, pcoz = scipy.optimize.curve_fit(fQ9, [xx0WCS, yy0WCS], zz0WCS, p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])

                            # Corrected displacements on point (x0,y0) in WCS
                            umi_meshWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_u[0]+fit_u[1]*x0WCS+fit_u[2]*y0WCS+fit_u[3]*x0WCS*y0WCS+fit_u[4]*x0WCS**2+fit_u[5]*y0WCS**2+fit_u[6]*y0WCS*x0WCS**2+fit_u[7]*x0WCS*y0WCS**2+fit_u[8]*(x0WCS**2)*(y0WCS**2)
                            vmi_meshWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_v[0]+fit_v[1]*x0WCS+fit_v[2]*y0WCS+fit_v[3]*x0WCS*y0WCS+fit_v[4]*x0WCS**2+fit_v[5]*y0WCS**2+fit_v[6]*y0WCS*x0WCS**2+fit_v[7]*x0WCS*y0WCS**2+fit_v[8]*(x0WCS**2)*(y0WCS**2)
                            wmi_meshWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_w[0]+fit_w[1]*x0WCS+fit_w[2]*y0WCS+fit_w[3]*x0WCS*y0WCS+fit_w[4]*x0WCS**2+fit_w[5]*y0WCS**2+fit_w[6]*y0WCS*x0WCS**2+fit_w[7]*x0WCS*y0WCS**2+fit_w[8]*(x0WCS**2)*(y0WCS**2)
                            zmi_meshWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_z[0]+fit_z[1]*x0WCS+fit_z[2]*y0WCS+fit_z[3]*x0WCS*y0WCS+fit_z[4]*x0WCS**2+fit_z[5]*y0WCS**2+fit_z[6]*y0WCS*x0WCS**2+fit_z[7]*x0WCS*y0WCS**2+fit_z[8]*(x0WCS**2)*(y0WCS**2)

                            # Gradients using the estimated parameters in WCS
                            dudxWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_u[1]+fit_u[3]*y0+2*fit_u[4]*x0+2*fit_u[6]*x0*y0+fit_u[7]*y0**2+2*fit_u[8]*x0*y0**2
                            dudyWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_u[2]+fit_u[3]*x0+2*fit_u[5]*y0+fit_u[6]*x0**2+2*fit_u[7]*x0*y0+2*fit_u[8]*y0*x0**2
                            dvdxWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_v[1]+fit_v[3]*y0+2*fit_v[4]*x0+2*fit_v[6]*x0*y0+fit_v[7]*y0**2+2*fit_v[8]*x0*y0**2
                            dvdyWCS[k][int(i-sw_step)][int(j-sw_step)] = fit_v[2]+fit_v[3]*x0+2*fit_v[5]*y0+fit_v[6]*x0**2+2*fit_v[7]*x0*y0+2*fit_v[8]*y0*x0**2

                            # Non-linear least squares using shape functions - p0 is the initial guess for the parameters in SPCS
                            fit_u, pcou = scipy.optimize.curve_fit(fQ9, [xx0SPCS, yy0SPCS], uu0SPCS,p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])
                            fit_v, pcov = scipy.optimize.curve_fit(fQ9, [xx0SPCS, yy0SPCS], vv0SPCS,p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])
                            fit_w, pcow = scipy.optimize.curve_fit(fQ9, [xx0SPCS, yy0SPCS], ww0SPCS,p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])
                            fit_z, pcoz = scipy.optimize.curve_fit(fQ9, [xx0SPCS, yy0SPCS], zz0SPCS,p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])

                            # Corrected displacements on point (x0,y0) in SPCS
                            umi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_u[0] + fit_u[1] * x0SPCS + fit_u[2] * y0SPCS + fit_u[3] * x0SPCS * y0SPCS + fit_u[4] * x0SPCS ** 2 + fit_u[5] * y0SPCS ** 2 + fit_u[6] * y0SPCS * x0SPCS ** 2 + fit_u[7] * x0SPCS * y0SPCS ** 2 + fit_u[8] * (x0SPCS ** 2) * (y0SPCS ** 2)
                            vmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_v[0] + fit_v[1] * x0SPCS + fit_v[2] * y0SPCS + fit_v[3] * x0SPCS * y0SPCS + fit_v[4] * x0SPCS ** 2 + fit_v[5] * y0SPCS ** 2 + fit_v[6] * y0SPCS * x0SPCS ** 2 + fit_v[7] * x0SPCS * y0SPCS ** 2 + fit_v[8] * (x0SPCS ** 2) * (y0SPCS ** 2)
                            wmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_w[0] + fit_w[1] * x0SPCS + fit_w[2] * y0SPCS + fit_w[3] * x0SPCS * y0SPCS + fit_w[4] * x0SPCS ** 2 + fit_w[5] * y0SPCS ** 2 + fit_w[6] * y0SPCS * x0SPCS ** 2 + fit_w[7] * x0SPCS * y0SPCS ** 2 + fit_w[8] * (x0SPCS ** 2) * (y0SPCS ** 2)
                            zmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_z[0] + fit_z[1] * x0SPCS + fit_z[2] * y0SPCS + fit_z[3] * x0SPCS * y0SPCS + fit_z[4] * x0SPCS ** 2 + fit_z[5] * y0SPCS ** 2 + fit_z[6] * y0SPCS * x0SPCS ** 2 + fit_z[7] * x0SPCS * y0SPCS ** 2 + fit_z[8] * (x0SPCS ** 2) * (y0SPCS ** 2)

                            # Gradients using the estimated parameters in SPCS
                            dudxSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_u[1] + fit_u[3] * y0 + 2 * fit_u[4] * x0 + 2 * fit_u[6] * x0 * y0 + fit_u[7] * y0 ** 2 + 2 * fit_u[8] * x0 * y0 ** 2
                            dudySPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_u[2] + fit_u[3] * x0 + 2 * fit_u[5] * y0 + fit_u[6] * x0 ** 2 + 2 * fit_u[7] * x0 * y0 + 2 * fit_u[8] * y0 * x0 ** 2
                            dvdxSPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_v[1] + fit_v[3] * y0 + 2 * fit_v[4] * x0 + 2 * fit_v[6] * x0 * y0 + fit_v[7] * y0 ** 2 + 2 * fit_v[8] * x0 * y0 ** 2
                            dvdySPCS[k][int(i - sw_step)][int(j - sw_step)] = fit_v[2] + fit_v[3] * x0 + 2 * fit_v[5] * y0 + fit_v[6] * x0 ** 2 + 2 * fit_v[7] * x0 * y0 + 2 * fit_v[8] * y0 * x0 ** 2

                        # Total displacement in WCS
                        uvmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] = np.sqrt(umi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] ** 2 + vmi_meshWCS[k][int(i - sw_step)][int(j - sw_step)] ** 2)

                        # Total displacement in SPCS
                        uvmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] = np.sqrt(umi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] ** 2 + vmi_meshSPCS[k][int(i - sw_step)][int(j - sw_step)] ** 2)

                        # Strain calculation - Green-Lagrangian - in WCS
                        exxWCS[k][int(i - sw_step)][int(j - sw_step)] = dudxWCS[k][int(i - sw_step)][int(j - sw_step)] + (1 / 2) * ((dudxWCS[k][int(i - sw_step)][int(j - sw_step)] ** 2) + (dvdxWCS[k][int(i - sw_step)][int(j - sw_step)] ** 2))
                        eyyWCS[k][int(i - sw_step)][int(j - sw_step)] = dvdyWCS[k][int(i - sw_step)][int(j - sw_step)] + (1 / 2) * ((dudyWCS[k][int(i - sw_step)][int(j - sw_step)] ** 2) + (dvdyWCS[k][int(i - sw_step)][int(j - sw_step)] ** 2))
                        exyWCS[k][int(i - sw_step)][int(j - sw_step)] = (1 / 2) * (dudyWCS[k][int(i - sw_step)][int(j - sw_step)] + dvdxWCS[k][int(i - sw_step)][int(j - sw_step)]) + (1 / 2) * (dudxWCS[k][int(i - sw_step)][int(j - sw_step)] *dudyWCS[k][int(i - sw_step)][int(j - sw_step)] +dvdxWCS[k][int(i - sw_step)][int(j - sw_step)] *dvdyWCS[k][int(i - sw_step)][int(j - sw_step)])

                        # Strain calculation - Green-Lagrangian - in SPCS
                        exxSPCS[k][int(i - sw_step)][int(j - sw_step)] = dudxSPCS[k][int(i - sw_step)][int(j - sw_step)] + (1 / 2) * ((dudxSPCS[k][int(i - sw_step)][int(j - sw_step)] ** 2) + (dvdxSPCS[k][int(i - sw_step)][int(j - sw_step)] ** 2))
                        eyySPCS[k][int(i - sw_step)][int(j - sw_step)] = dvdySPCS[k][int(i - sw_step)][int(j - sw_step)] + (1 / 2) * ((dudySPCS[k][int(i - sw_step)][int(j - sw_step)] ** 2) + (dvdySPCS[k][int(i - sw_step)][int(j - sw_step)] ** 2))
                        exySPCS[k][int(i - sw_step)][int(j - sw_step)] = (1 / 2) * (dudySPCS[k][int(i - sw_step)][int(j - sw_step)] + dvdxSPCS[k][int(i - sw_step)][int(j - sw_step)]) + (1 / 2) * (dudxSPCS[k][int(i - sw_step)][int(j - sw_step)] *dudySPCS[k][int(i - sw_step)][int(j - sw_step)] +dvdxSPCS[k][int(i - sw_step)][int(j - sw_step)] *dvdySPCS[k][int(i - sw_step)][int(j - sw_step)])

            np.savetxt(f'{outputFolder.get()}/{filexWCS.format(k+1)}', xriWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileyWCS.format(k+1)}', yriWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filezWCS.format(k+1)}', zmi_meshWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileuWCS.format(k+1)}', umi_meshWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filevWCS.format(k+1)}', vmi_meshWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileuvWCS.format(k+1)}', uvmi_meshWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filewWCS.format(k+1)}', wmi_meshWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filexSPCS.format(k+1)}', xriSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileySPCS.format(k+1)}', yriSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filezSPCS.format(k+1)}', zmi_meshSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileuSPCS.format(k+1)}', umi_meshSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filevSPCS.format(k+1)}', vmi_meshSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileuvSPCS.format(k+1)}', uvmi_meshSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filewSPCS.format(k+1)}', wmi_meshSPCS[k][:][:], fmt='%.10e')

            np.savetxt(f'{outputFolder.get()}/{filexL.format(k+1)}', xriL[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileyL.format(k+1)}', yriL[k][:][:], fmt='%.10e')

            np.savetxt(f'{outputFolder.get()}/{fileexxWCS.format(k+1)}', exxWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileexyWCS.format(k+1)}', exyWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileeyyWCS.format(k+1)}', eyyWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedudxWCS.format(k+1)}', dudxWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedudyWCS.format(k+1)}', dudyWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedvdxWCS.format(k+1)}', dvdxWCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedvdyWCS.format(k+1)}', dvdyWCS[k][:][:], fmt='%.10e')

            np.savetxt(f'{outputFolder.get()}/{fileexxSPCS.format(k+1)}', exxSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileexySPCS.format(k+1)}', exySPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileeyySPCS.format(k+1)}', eyySPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedudxSPCS.format(k+1)}', dudxSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedudySPCS.format(k+1)}', dudySPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedvdxSPCS.format(k+1)}', dvdxSPCS[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedvdySPCS.format(k+1)}', dvdySPCS[k][:][:], fmt='%.10e')

            # Preview post processed field:
            if Preview.get() == 1:
                # Load image:
                I = cv2.imread(fileNames[k])

                ymax, xmax, miscel = I.shape

                preview_field_var = vars()[f'{preview_var[Preview_field_dict.get(Preview_field.get())]}'][k][:][:]

                locscb = np.linspace(np.min(preview_field_var[~np.isnan(preview_field_var)]),
                                     np.max(preview_field_var[~np.isnan(preview_field_var)]), 8,
                                     endpoint=True)

                fig_instant = plt.figure(facecolor='#99b3c3')
                plt.imshow(I)

                contour = plt.contourf(xriL[k][:][:] / Cal, yriL[k][:][:] / Cal, preview_field_var, levels=100,
                                       cmap=color_map_var[color_map_dict.get(Color_map.get())],
                                       alpha=Alpha.get(), antialiased=True)

                plt.axis('off')
                cb = plt.colorbar(ticks=locscb, format='%.2e')
                cb.ax.tick_params(labelsize=12)
                for l in cb.ax.yaxis.get_ticklabels():
                    l.set_family('Times New Roman')
                cb.set_alpha(1)
                cb.draw_all()
                plt.axis('equal')

                plt.title(f'{Preview_field.get()} field of instant {k + 1}', fontname='Times New Roman', fontsize=12)

                fig_instant.canvas.draw()
                image_instant = np.frombuffer(fig_instant.canvas.tostring_rgb(), dtype=np.uint8)
                wR, hR = fig_instant.canvas.get_width_height()
                image_instant = image_instant.reshape((hR, wR, 3))

                plt.cla()
                plt.clf()
                plt.close()
                ax = None
                fig_instant = None

                image_right = cv.resize(image_instant, (int(640 * 0.98), int(480 * 0.98)))
                image_right = ImageTk.PhotoImage(Image.fromarray(image_right))

                canvas.image_right = image_right
                canvas.configure(image=image_right)

            console.insert(tk.END, ' Done\n\n')
            console.see('insert')

            green_length = int(515 * ((k + 1) / nImages))
            progression.coords(progression_bar, 0, 0, green_length, 25);
            progression.itemconfig(canvas_text, text=f'{k + 1} of {nImages} - {100 * (k + 1) / nImages:.2f}%')

    else:

        for k in range(0, nImages):

            console.insert(tk.END, f'Calculating instant {k + 1} -')
            console.see('insert')

            for i in range(int(sw_step), int(Ney + sw_step)):
                for j in range(int(sw_step), int(Nex + sw_step)):
                    if ~np.isnan(xMesh[k][i][j]):

                        # Point (x0,y0)
                        x0 = xMesh[k][i][j];
                        y0 = yMesh[k][i][j];

                        # Points (xx0,yy0) inside strain window
                        xx0 = xMesh[k][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()
                        yy0 = yMesh[k][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()

                        # Displacement of points (xx0,yy0)
                        uu0 = uMesh[k][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()
                        vv0 = vMesh[k][int(i - sw_step):int(i + sw_step), int(j - sw_step):int(j + sw_step)].flatten()

                        # Removing nan values inside strain window
                        xx0 = xx0[~np.isnan(xx0)]
                        yy0 = yy0[~np.isnan(yy0)]
                        uu0 = uu0[~np.isnan(uu0)]
                        vv0 = vv0[~np.isnan(vv0)]

                        if Shape_function.get() == 'None':
                            # Displacements on point (x0,y0)
                            umi_mesh[k][int(i - sw_step)][int(j - sw_step)] = uMesh[k][i][j]
                            vmi_mesh[k][int(i - sw_step)][int(j - sw_step)] = vMesh[k][i][j]

                            # Gradients using the estimated parameters
                            dudx[k][int(i - sw_step)][int(j - sw_step)] = 0
                            dudy[k][int(i - sw_step)][int(j - sw_step)] = 0
                            dvdx[k][int(i - sw_step)][int(j - sw_step)] = 0
                            dvdy[k][int(i - sw_step)][int(j - sw_step)] = 0

                        if Shape_function.get() == 'Bilinear':
                            # Non-linear least squares using shape functions - p0 is the initial guess for the parameters
                            fit_u, pcou = scipy.optimize.curve_fit(fQ4, [xx0, yy0], uu0, p0=[0, 0, 0, 0])
                            fit_v, pcov = scipy.optimize.curve_fit(fQ4, [xx0, yy0], vv0, p0=[0, 0, 0, 0])

                            # Corrected displacements on point (x0,y0)
                            umi_mesh[k][int(i - sw_step)][int(j - sw_step)] = fit_u[0] + fit_u[
                                1] * x0 + fit_u[2] * y0 + fit_u[3] * x0 * y0
                            vmi_mesh[k][int(i - sw_step)][int(j - sw_step)] = fit_v[0] + fit_v[
                                1] * x0 + fit_v[2] * y0 + fit_v[3] * x0 * y0

                            # Gradients using the estimated parameters
                            dudx[k][int(i - sw_step)][int(j - sw_step)] = fit_u[1] + fit_u[3] * y0
                            dudy[k][int(i - sw_step)][int(j - sw_step)] = fit_u[2] + fit_u[3] * x0
                            dvdx[k][int(i - sw_step)][int(j - sw_step)] = fit_v[1] + fit_v[3] * y0
                            dvdy[k][int(i - sw_step)][int(j - sw_step)] = fit_v[2] + fit_v[3] * x0

                        if Shape_function.get() == 'Biquadratic':
                            # Non-linear least squares using shape functions - p0 is the initial guess for the parameters
                            fit_u, pcou = scipy.optimize.curve_fit(fQ9, [xx0, yy0], uu0, p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])
                            fit_v, pcov = scipy.optimize.curve_fit(fQ9, [xx0, yy0], vv0, p0=[0, 0, 0, 0, 0, 0, 0, 0, 0])

                            # Corrected displacements on point (x0,y0)
                            umi_mesh[k][int(i - sw_step)][int(j - sw_step)] = fit_u[0] + fit_u[1] * x0 + fit_u[2] * y0 + \
                                                                              fit_u[3] * x0 * y0 + fit_u[4] * x0 ** 2 + \
                                                                              fit_u[5] * y0 ** 2 + fit_u[
                                                                                  6] * y0 * x0 ** 2 + fit_u[
                                                                                  7] * x0 * y0 ** 2 + fit_u[8] * (
                                                                                          x0 ** 2) * (y0 ** 2)
                            vmi_mesh[k][int(i - sw_step)][int(j - sw_step)] = fit_v[0] + fit_v[1] * x0 + fit_v[2] * y0 + \
                                                                              fit_v[3] * x0 * y0 + fit_v[4] * x0 ** 2 + \
                                                                              fit_v[5] * y0 ** 2 + fit_v[
                                                                                  6] * y0 * x0 ** 2 + fit_v[
                                                                                  7] * x0 * y0 ** 2 + fit_v[8] * (
                                                                                          x0 ** 2) * (y0 ** 2)

                            # Gradients using the estimated parameters
                            dudx[k][int(i - sw_step)][int(j - sw_step)] = fit_u[1] + fit_u[3] * y0 + 2 * fit_u[
                                4] * x0 + 2 * fit_u[6] * x0 * y0 + fit_u[7] * y0 ** 2 + 2 * fit_u[8] * x0 * y0 ** 2
                            dudy[k][int(i - sw_step)][int(j - sw_step)] = fit_u[2] + fit_u[3] * x0 + 2 * fit_u[5] * y0 + \
                                                                          fit_u[6] * x0 ** 2 + 2 * fit_u[
                                                                              7] * x0 * y0 + 2 * fit_u[8] * y0 * x0 ** 2
                            dvdx[k][int(i - sw_step)][int(j - sw_step)] = fit_v[1] + fit_v[3] * y0 + 2 * fit_v[
                                4] * x0 + 2 * fit_v[6] * x0 * y0 + fit_v[7] * y0 ** 2 + 2 * fit_v[8] * x0 * y0 ** 2
                            dvdy[k][int(i - sw_step)][int(j - sw_step)] = fit_v[2] + fit_v[3] * x0 + 2 * fit_v[5] * y0 + \
                                                                          fit_v[6] * x0 ** 2 + 2 * fit_v[
                                                                              7] * x0 * y0 + 2 * fit_v[8] * y0 * x0 ** 2

                        # Total displacement
                        uvmi_mesh[k][int(i - sw_step)][int(j - sw_step)] = np.sqrt(
                            umi_mesh[k][int(i - sw_step)][int(j - sw_step)] ** 2 + vmi_mesh[k][int(i - sw_step)][
                                int(j - sw_step)] ** 2)

                        # Strain calculation - Green-Lagrangian
                        exx[k][int(i - sw_step)][int(j - sw_step)] = dudx[k][int(i - sw_step)][int(j - sw_step)] + (
                                1 / 2) * ((dudx[k][int(i - sw_step)][int(j - sw_step)] ** 2) + (
                                dvdx[k][int(i - sw_step)][int(j - sw_step)] ** 2))
                        eyy[k][int(i - sw_step)][int(j - sw_step)] = dvdy[k][int(i - sw_step)][int(j - sw_step)] + (
                                1 / 2) * ((dudy[k][int(i - sw_step)][int(j - sw_step)] ** 2) + (
                                dvdy[k][int(i - sw_step)][int(j - sw_step)] ** 2))
                        exy[k][int(i - sw_step)][int(j - sw_step)] = (1 / 2) * (
                                dudy[k][int(i - sw_step)][int(j - sw_step)] + dvdx[k][int(i - sw_step)][
                            int(j - sw_step)]) + (1 / 2) * (dudx[k][int(i - sw_step)][int(j - sw_step)] *
                                                            dudy[k][int(i - sw_step)][int(j - sw_step)] +
                                                            dvdx[k][int(i - sw_step)][int(j - sw_step)] *
                                                            dvdy[k][int(i - sw_step)][int(j - sw_step)])

            filex = 'xm{:02d}.dat'
            filey = 'ym{:02d}.dat'
            fileu = 'um{:02d}.dat'
            filev = 'vm{:02d}.dat'
            fileuv = 'uvm{:02d}.dat'
            fileexx = 'exx{:02d}.dat'
            fileexy = 'exy{:02d}.dat'
            fileeyy = 'eyy{:02d}.dat'
            filedudx = 'dudx{:02d}.dat'
            filedudy = 'dudy{:02d}.dat'
            filedvdx = 'dvdx{:02d}.dat'
            filedvdy = 'dvdy{:02d}.dat'
            np.savetxt(f'{outputFolder.get()}/{filex.format(k+1)}', xri[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filey.format(k+1)}', yri[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileu.format(k+1)}', umi_mesh[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filev.format(k+1)}', vmi_mesh[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileuv.format(k+1)}', uvmi_mesh[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileexx.format(k+1)}', exx[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileexy.format(k+1)}', exy[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{fileeyy.format(k+1)}', eyy[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedudx.format(k+1)}', dudx[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedudy.format(k+1)}', dudy[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedvdx.format(k+1)}', dvdx[k][:][:], fmt='%.10e')
            np.savetxt(f'{outputFolder.get()}/{filedvdy.format(k+1)}', dvdy[k][:][:], fmt='%.10e')

            # Preview post processed field:
            if Preview.get() == 1:
                # Load image:
                I = cv2.imread(fileNames[k])

                ymax, xmax, miscel = I.shape

                preview_field_var = vars()[f'{preview_var[Preview_field_dict.get(Preview_field.get())]}'][k][:][:]

                locscb = np.linspace(np.min(preview_field_var[~np.isnan(preview_field_var)]),
                                     np.max(preview_field_var[~np.isnan(preview_field_var)]), 8,
                                     endpoint=True)

                fig_instant = plt.figure(facecolor='#99b3c3')
                plt.imshow(I)

                contour = plt.contourf(xri[k][:][:] / Cal, yri[k][:][:] / Cal, preview_field_var, levels=100,
                                       cmap=color_map_var[color_map_dict.get(Color_map.get())],
                                       alpha=Alpha.get(), antialiased=True)

                plt.axis('off')
                cb = plt.colorbar(ticks=locscb, format='%.2e')
                cb.ax.tick_params(labelsize=12)
                for l in cb.ax.yaxis.get_ticklabels():
                    l.set_family('Times New Roman')
                cb.set_alpha(1)
                cb.draw_all()
                plt.axis('equal')

                plt.title(f'{Preview_field.get()} field of instant {k + 1}', fontname='Times New Roman', fontsize=12)

                fig_instant.canvas.draw()
                image_instant = np.frombuffer(fig_instant.canvas.tostring_rgb(), dtype=np.uint8)
                wR, hR = fig_instant.canvas.get_width_height()
                image_instant = image_instant.reshape((hR, wR, 3))

                plt.cla()
                plt.clf()
                plt.close()
                ax = None
                fig_instant = None

                image_right = cv.resize(image_instant, (int(640 * 0.98), int(480 * 0.98)))
                image_right = ImageTk.PhotoImage(Image.fromarray(image_right))

                canvas.image_right = image_right
                canvas.configure(image=image_right)

            console.insert(tk.END, ' Done\n\n')
            console.see('insert')

            green_length = int(515 * ((k + 1) / nImages))
            progression.coords(progression_bar, 0, 0, green_length, 25);
            progression.itemconfig(canvas_text, text=f'{k + 1} of {nImages} - {100 * (k + 1) / nImages:.2f}%')

    console.insert(tk.END, f'Generating images to be exported to {figureFolder.get()}\n\n')
    console.see('insert')

    # Instants to plot:
    Plot_Inst = np.array(list(map(int, Instant.get().split(","))))


    if test_3D:
        figure_save_name = ['Reference', 'Current', 'u', 'v', 'uv', 'w', 'exx', 'eyy', 'exy', '3D']
        figure_title = ['Reference', 'Current', 'u', 'v', 'uv', 'w', 'exx', 'eyy', 'exy', '3D']
        figure_field = ['umi_meshSPCS', 'vmi_meshSPCS', 'uvmi_meshSPCS', 'wmi_meshSPCS','exxSPCS', 'eyySPCS', 'exySPCS', 'zmi_meshSPCS']
    else:
        figure_save_name = ['Reference', 'Current', 'u', 'v', 'uv', 'w', 'exx', 'eyy', 'exy', '3D']
        figure_title = ['Reference', 'Current', 'u', 'v', 'uv', 'w', 'exx', 'eyy', 'exy', '3D']
        figure_field = ['umi_mesh', 'vmi_mesh', 'uvmi_mesh','wmi_mesh', 'exx', 'eyy', 'exy','zmi_mesh']

    cbar_format = {'Integer': 'd', 'Float': 'f', 'Scientific': 'e'}

    # Reference grid plot:
    if plot_var[0] == 1:
        generate_figure_grid(console, k, Nex, Ney, xriL if test_3D else xri, yriL if test_3D else yri, Cal, Method, Tag, Alpha, TextFont, FontSize,
                             xTicks, yTicks, AddTitle, AddAxes, AxesDigits, cbarTicks, ImgFormat, figure_save_name[0],
                             figure_title[0], figureFolder, Linewidth)

    # Current grid plot:
    for k in Plot_Inst:
        if plot_var[1] == 1:
            generate_figure_grid(console, k, Nex, Ney, xriL if test_3D else xri, yriL if test_3D else yri, Cal, Method, Tag, Alpha, TextFont, FontSize,
                                 xTicks, yTicks, AddTitle, AddAxes, AxesDigits, cbarTicks, ImgFormat,
                                 figure_save_name[1],
                                 figure_title[1], figureFolder, Linewidth)

        for n in range(2, len(figure_save_name)):

            if plot_var[n] == 1:
                generate_figure_field(console, k, Nex, Ney, xriL if test_3D else xri, yriL if test_3D else yri, Cal, Method, Tag, Alpha, TextFont, FontSize,
                                      xTicks, yTicks, AddTitle, AddAxes, AxesDigits, cbarTicks, ImgFormat, cbarDigits,
                                      cbarFormat, cbar_format, vars()[f'{figure_field[n - 2]}'], auto_var[n - 2],
                                      min_var[n - 2], max_var[n - 2],
                                      figure_save_name[n], figure_title[n], figureFolder,Color_map, color_map_dict)

########################################################################################################################
# Function to generate the grid figure
########################################################################################################################
def generate_figure_grid(console, Image, Nex, Ney, X, Y, Cal, Method, Tag, Alpha, TextFont, FontSize,
                          xTicks, yTicks, AddTitle, AddAxes, AxesDigits, cbarTicks, ImgFormat, Name, Title,
                          figureFolder, Linewidth):
    # Captured image:
    I = cv2.imread(fileNames[Image-1]) if Name == 'Current' else cv2.imread(fileNames[0])

    # Select the mesh according to the chosen method:
    Xi = X[Image-1][:][:] if Name == 'Current' else X[0][:][:]
    Yi = Y[Image - 1][:][:] if Name == 'Current' else Y[0][:][:]

    console.insert(tk.END, f'Saving image {Name}_' + str(Image) + '_' + str(Tag.get()) + ImgFormat.get() + ' -')
    console.see('insert')

    ymax, xmax, miscel = I.shape

    fig_out = plt.figure(dpi=800)
    plt.imshow(I, extent=[0, xmax, ymax, 0])
    plt.plot(Xi / Cal, Yi / Cal, color='red', linewidth=Linewidth.get())
    plt.plot(np.transpose(Xi / Cal), np.transpose(Yi / Cal), color='red', linewidth=Linewidth.get())
    if AddAxes.get() == 'Yes':
        a = gca()
        a.set_xticklabels(a.get_xticks(),
                          fontname=TextFont.get(),
                          fontsize=FontSize.get())
        a.set_yticklabels(a.get_yticks(),
                          fontname=TextFont.get(),
                          fontsize=FontSize.get())
        locsx = np.linspace(0, abs(xmax), xTicks.get(), endpoint=True)
        locsy = np.linspace(0, abs(ymax), yTicks.get(), endpoint=True)
        plt.xticks(locsx, np.round(np.array(locsx * Cal), AxesDigits.get()))
        plt.yticks(locsy, np.round(np.array(locsy * Cal), AxesDigits.get()))
        plt.xlabel(r'$x$ [mm]', fontname=TextFont.get(), fontsize=FontSize.get())
        plt.ylabel(r'$y$ [mm]', fontname=TextFont.get(), fontsize=FontSize.get())

    else:
        plt.axis('off')

    if AddTitle.get() == 'Yes':
        plt.title(f'{Title}', fontname=TextFont.get(), fontsize=FontSize.get())

    plt.savefig(figureFolder.get() + '/' + f'{Name}_' + str(Image) + '_' + str(Tag.get()) + ImgFormat.get(), dpi=800)

    plt.cla()
    plt.clf()
    plt.close()

    console.insert(tk.END, ' Done\n\n')
    console.see('insert')

########################################################################################################################
# Function to generate the full-field maps figure
########################################################################################################################
def generate_figure_field(console, Image, Nex, Ney, X, Y, Cal, Method, Tag, Alpha, TextFont, FontSize,
                          xTicks, yTicks, AddTitle, AddAxes, AxesDigits, cbarTicks, ImgFormat, cbarDigits,
                          cbarFormat, cbar_format, Field_Var, Field_Var_Auto, Field_Var_Min, Field_Var_Max, Name, Title,
                          figureFolder,Color_map, color_map_dict):

    # Captured image - Eulerian (reference image) - Lagrangian (current image):
    I = cv2.imread(fileNames[Image-1]) if Method.get() == 'Lagrangian' else cv2.imread(fileNames[0])

    # Color map:
    color_map_var = ['Blues','Greens','Greys','Oranges','Reds','afmhot','autumn','bone','copper','hot','hsv','jet','winter']

    ymax, xmax, miscel = I.shape

    console.insert(tk.END,f'Saving image {Name}_' + str(Image) + '_' + str(Tag.get()) + ImgFormat.get() + ' -')
    console.see('insert')

    fig_out = plt.figure(tight_layout=True)
    plt.imshow(I)
    Field_Var_Range = Field_Var[Image - 1][:][:]
    Field_Var_Range_F = Field_Var_Range.flatten()
    locscb = np.linspace(np.min(Field_Var_Range_F[~np.isnan(Field_Var_Range_F)]),
                         np.max(Field_Var_Range_F[~np.isnan(Field_Var_Range_F)]), cbarTicks.get(), endpoint=True)
    if Field_Var_Auto != 1:
        for i in range(0, Ney):
            for j in range(0, Nex):
                if Field_Var[Image - 1][i][j] > Field_Var_Max:
                    Field_Var_Range[i][j] = Field_Var_Max
                elif Field_Var[Image - 1][i][j] < Field_Var_Min:
                    Field_Var_Range[i][j] = Field_Var_Min
        contour = plt.contourf(X[Image - 1][:][:] / Cal, Y[Image - 1][:][:] / Cal,
                               Field_Var_Range,
                               levels=np.linspace(Field_Var_Min, Field_Var_Max, 100),
                               cmap=color_map_var[color_map_dict.get(Color_map.get())],
                               alpha=Alpha.get(),
                               antialiased=True)
    else:
        contour = plt.contourf(X[Image - 1][:][:] / Cal, Y[Image - 1][:][:] / Cal,
                               Field_Var_Range,
                               levels=100, cmap=color_map_var[color_map_dict.get(Color_map.get())],
                               alpha=Alpha.get(),
                               antialiased=True)
    if AddAxes.get() == 'Yes':

        if Field_Var_Auto != 1:
            a = gca()
            cb = plt.colorbar(format=f'%.{cbarDigits.get()}{cbar_format.get(cbarFormat.get())}')
            cb.ax.set_yticklabels(np.linspace(Field_Var_Min, Field_Var_Max, num=cbarTicks.get()))
            a.set_xticklabels(a.get_xticks(),
                              fontname=TextFont.get(),
                              fontsize=FontSize.get())
            a.set_yticklabels(a.get_yticks(),
                              fontname=TextFont.get(),
                              fontsize=FontSize.get())
            locsx = np.linspace(0, abs(xmax), xTicks.get(), endpoint=True)
            locsy = np.linspace(0, abs(ymax), yTicks.get(), endpoint=True)
            plt.xticks(locsx, np.round(np.array(locsx * Cal), AxesDigits.get()))
            plt.yticks(locsy, np.round(np.array(locsy * Cal), AxesDigits.get()))
            plt.xlabel(r'$x$ [mm]', fontname=TextFont.get(), fontsize=FontSize.get())
            plt.ylabel(r'$y$ [mm]', fontname=TextFont.get(), fontsize=FontSize.get())
            #cb = plt.colorbar(ticks=locscb,
            #                  format=f'%.{cbarDigits.get()}{cbar_format.get(cbarFormat.get())}')

        else:
            a = gca()
            a.set_xticklabels(a.get_xticks(),
                              fontname=TextFont.get(),
                              fontsize=FontSize.get())
            a.set_yticklabels(a.get_yticks(),
                              fontname=TextFont.get(),
                              fontsize=FontSize.get())
            locsx = np.linspace(0, abs(xmax), xTicks.get(), endpoint=True)
            locsy = np.linspace(0, abs(ymax), yTicks.get(), endpoint=True)
            plt.xticks(locsx, np.round(np.array(locsx * Cal), AxesDigits.get()))
            plt.yticks(locsy, np.round(np.array(locsy * Cal), AxesDigits.get()))
            plt.xlabel(r'$x$ [mm]', fontname=TextFont.get(), fontsize=FontSize.get())
            plt.ylabel(r'$y$ [mm]', fontname=TextFont.get(), fontsize=FontSize.get())
            cb = plt.colorbar(ticks=locscb,
                              format=f'%.{cbarDigits.get()}{cbar_format.get(cbarFormat.get())}')

        cb.ax.tick_params(labelsize=FontSize.get())
        if Name == 'u' or Name == 'v' or Name == 'uv' or Name == 'w' or Name == '3D':
            cb.ax.set_title('[mm]',
                            style='italic',
                            fontname=TextFont.get(),
                            fontsize=FontSize.get())
        for l in cb.ax.yaxis.get_ticklabels():
            l.set_family(TextFont.get())
        cb.set_alpha(1)
        cb.draw_all()
    else:
        plt.axis('off')

    if AddTitle.get() == 'Yes':
        plt.title(f'{Title}', fontname=TextFont.get(), fontsize=FontSize.get())

    plt.savefig(figureFolder.get() + '/' + f'{Name}_' + str(Image) + '_' + str(Tag.get()) + ImgFormat.get(), dpi=800)

    plt.cla()
    plt.clf()
    plt.close()

    console.insert(tk.END, ' Done\n\n')
    console.see('insert')