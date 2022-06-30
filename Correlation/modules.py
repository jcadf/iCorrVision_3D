########################################################################################################################
# iCorrVision-3D Correlation Module                                                                                    #
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
    iCorrVision-3D Correlation Module
    Copyright (C) 2022 iCorrVision team

    This file is part of the iCorrVision-3D software.

    The iCorrVision-3D Correlation Module is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The iCorrVision-3D Correlation Module is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

V = 'v1.04.22' # Version

import csv
import ctypes
import datetime;
import glob
import multiprocessing as mp
import ntpath
import os
import subprocess
import time
########################################################################################################################
# Modules
########################################################################################################################
import tkinter as tk;
from math import pi
from multiprocessing.sharedctypes import RawArray
from threading import Thread;
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox;
from tkinter import ttk

import cv2 as cv;
import matplotlib;
import numpy as np;
from PIL import Image;
from PIL import ImageTk;
from matplotlib import pyplot as plt
from numpy import genfromtxt
from scipy import interpolate
from scipy.interpolate import interp2d
from scipy.spatial.transform import Rotation
from shapely.geometry import Point;
from shapely.geometry.polygon import Polygon;

matplotlib.use('Agg', force=True)

########################################################################################################################
# Open user guide
########################################################################################################################
def openguide(CurrentDir):
    subprocess.Popen([CurrentDir + '\static\iCorrVision-3D.pdf'], shell=True)

########################################################################################################################
# Configure combobox
########################################################################################################################
def combo_configure(event):
    width = 40
    style = ttk.Style()
    style.configure(style='TCombobox', postoffset=(0, 0, width, 0))

########################################################################################################################
# Global variables declaration for parallel computing (x0, y0, u0, v0, x1, y1, u1 and v1)
########################################################################################################################
process_x0_mem = None
process_x0_shape = None
process_y0_mem = None
process_y0_shape = None
process_u0_mem = None
process_u0_shape = None
process_v0_mem = None
process_v0_shape = None
process_x1_mem = None
process_x1_shape = None
process_y1_mem = None
process_y1_shape = None
process_u1_mem = None
process_u1_shape = None
process_v1_mem = None
process_v1_shape = None

########################################################################################################################
# Line drawing using mouse event functions
########################################################################################################################
def drawLineMouse(event,x,y,flags,param):
    global point_x1, point_y1, pressed, points, subsetImage

    if event == cv.EVENT_LBUTTONDOWN:

        pressed = True
        point_x1,point_y1=x,y
        points.append((x, y))

    elif event == cv.EVENT_MOUSEMOVE:

        if pressed == True:
            
            cv.line(subsetImage,(point_x1,point_y1),(x,y),color=(255,0,0),thickness=1)
            point_x1, point_y1 = x, y
            points.append((x, y))

    elif event==cv.EVENT_LBUTTONUP:

        pressed=False
        cv.line(subsetImage,(point_x1,point_y1),(x,y),color=(255,0,0),thickness=1)

########################################################################################################################
# Freehand cut region using drawLineMouse function
########################################################################################################################
def freehandCut(name, img):
    global point_x1, point_y1, pressed, points, subsetImage

    subsetImage = img

    pressed = False
    point_x1 , point_y1 = None , None

    points =[]

    cv.namedWindow(name)
    cv.setMouseCallback(name, drawLineMouse)

    while(1):
        cv.imshow(name,subsetImage)
        if cv.waitKey(1) & 0xFF == 13:
            break
    cv.destroyAllWindows()

    return points

########################################################################################################################
# Function - try integer value
########################################################################################################################
def tryInt(s):
    try:
        return int(s)
    except:
        return s

########################################################################################################################
# Turn a string into a list of string
########################################################################################################################
def stringToList(s):

    return [ tryInt(c) for c in re.split('([0-9]+)', s) ]

########################################################################################################################
# Function to select the captured images folder
########################################################################################################################
def captured_folder(capturedFolder, captured_status, console, canvas_left, canvas_right):
    global filename_captured, test_captured, fileNamesLeft, fileNamesRight, Format, Images

    filename_captured = filedialog.askdirectory()
    capturedFolder.set(filename_captured)

    console.insert(tk.END,
        '##################################################################################################################\n\n')
    console.see('insert')

    if not filename_captured:
        captured_status.configure(bg = 'red') # Red indicator
        console.insert(tk.END, 'The captured folder was not selected\n\n')
        console.see('insert')
        messagebox.showerror('Error','The captured folder was not selected!')
    else:
        captured_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'Image captured folder - {capturedFolder.get()}\n\n')
        console.see('insert')

        # Captured image files:
        fileNamesLeft = sorted(glob.glob(filename_captured+'\\Left\\*'),key=stringToList)
        fileNamesRight = sorted(glob.glob(filename_captured+'\\Right\\*'),key=stringToList)
        Format = '.'+fileNamesLeft[0].rsplit('.', 1)[1]
        Images = len(fileNamesLeft)

        # Left image resolution correction:
        fig_left = plt.figure()
        ax = fig_left.gca()
        dxplot = int(cv.imread(fileNamesLeft[0]).shape[1])
        dyplot = int(cv.imread(fileNamesLeft[0]).shape[0])

        ratio_plot = dxplot / dyplot;

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesLeft[0]), zorder=2)
            ax.plot([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], color='black',
                zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesLeft[0]), zorder=2)
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        fig_left.canvas.draw()

        image_left = np.frombuffer(fig_left.canvas.tostring_rgb(), dtype=np.uint8)
        w, h = fig_left.canvas.get_width_height()
        image_left = np.flip(image_left.reshape((h, w, 3)), axis=0)

        # Right image resolution correction:
        fig_right = plt.figure()
        ax = fig_right.gca()
        dxplot = int(cv.imread(fileNamesRight[0]).shape[1])
        dyplot = int(cv.imread(fileNamesRight[0]).shape[0])

        ratio_plot = dxplot / dyplot;

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesRight[0]), zorder=2)
            ax.plot([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], color='black',
                zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesRight[0]), zorder=2)
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        fig_right.canvas.draw()

        image_right = np.frombuffer(fig_right.canvas.tostring_rgb(), dtype=np.uint8)
        w, h = fig_right.canvas.get_width_height()
        image_right = np.flip(image_right.reshape((h, w, 3)), axis=0)

        plt.cla()
        plt.clf()

        image_left = cv.resize(image_left, (426, 320))
        cv.putText(image_left,'MASTER L',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
        image_left = ImageTk.PhotoImage (Image.fromarray (image_left))

        image_right = cv.resize(image_right, (426, 320))
        cv.putText(image_right,'SLAVE R',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
        image_right = ImageTk.PhotoImage (Image.fromarray (image_right))

        canvas_left.image_left = image_left
        canvas_left.configure(image = image_left)

        canvas_right.image_right = image_right
        canvas_right.configure(image = image_right)

        console.insert(tk.END, f'{Images} image pairs were imported with {Format} format\n\n')
        console.see('insert')
        test_captured = True

########################################################################################################################
# Function to select the calibration file
########################################################################################################################
def calib_file(console, calibFile,calib_status):
    global filename_calib, test_calib, calib

    filename_calib = filedialog.askopenfilename()

    calibFile.set(filename_calib)

    console.insert(tk.END,
                   '##################################################################################################################\n\n')
    console.see('insert')

    if not filename_calib:
        calib_status.configure(bg = 'red') # Red indicator
        console.insert(tk.END, 'The calibration file was not selected\n\n')
        console.see('insert')
        messagebox.showerror('Error','The calibration file was not selected!')
    else:
        calib_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'Calibration file - {calibFile.get()}\n\n')
        console.see('insert')

        with open(filename_calib) as f:
            reader = csv.reader(f, delimiter=';')
            data = [(col1, float(col2)) for col1, col2 in reader]
            f.close()

        if data[0][1] == 0:
            K1 = np.zeros((3, 3))
            D1 = np.zeros((1, 5))
            K2 = np.zeros((3, 3))
            D2 = np.zeros((1, 5))
            ROT = np.zeros((3, 3))
            TRANS = np.zeros((1, 3))

            w = 1
            K1[0, 0] = data[w][1]; w = w + 1
            K1[1, 1] = data[w][1]; w = w + 1
            K1[0, 1] = data[w][1]; w = w + 1
            K1[0, 2] = data[w][1]; w = w + 1
            K1[1, 2] = data[w][1]; w = w + 1
            K1[2, 2] = 1
            D1[0, 0] = data[w][1]; w = w + 1
            D1[0, 1] = data[w][1]; w = w + 1
            D1[0, 4] = data[w][1]; w = w + 1
            D1[0, 2] = data[w][1]; w = w + 1
            D1[0, 3] = data[w][1]; w = w + 1
            K2[0, 0] = data[w][1]; w = w + 1
            K2[1, 1] = data[w][1]; w = w + 1
            K2[0, 1] = data[w][1]; w = w + 1
            K2[0, 2] = data[w][1]; w = w + 1
            K2[1, 2] = data[w][1]; w = w + 1
            K2[2, 2] = 1
            D2[0, 0] = data[w][1]; w = w + 1
            D2[0, 1] = data[w][1]; w = w + 1
            D2[0, 4] = data[w][1]; w = w + 1
            D2[0, 2] = data[w][1]; w = w + 1
            D2[0, 3] = data[w][1]; w = w + 1
            TRANS[0,0] = data[w][1]; w = w + 1
            TRANS[0,1] = data[w][1]; w = w + 1
            TRANS[0,2] = data[w][1]; w = w + 1
            ROT[0, 0] =data[w][1]; w = w + 1
            ROT[0, 1] =data[w][1]; w = w + 1
            ROT[0, 2] =data[w][1]; w = w + 1
            ROT[1, 0] =data[w][1]; w = w + 1
            ROT[1, 1] =data[w][1]; w = w + 1
            ROT[1, 2] =data[w][1]; w = w + 1
            ROT[2, 0] =data[w][1]; w = w + 1
            ROT[2, 1] =data[w][1]; w = w + 1
            ROT[2, 2] =data[w][1]

        else:
            K1 = np.zeros((3, 3))
            D1 = np.zeros((1, 5))
            K2 = np.zeros((3, 3))
            D2 = np.zeros((1, 5))
            TRANS = np.zeros((1, 3))
            ANGLE = np.zeros(3)

            w = 1
            K1[0, 0] = data[w][1];w = w + 1
            K1[1, 1] = data[w][1];w = w + 1
            K1[0, 1] = data[w][1];w = w + 1
            K1[0, 2] = data[w][1];w = w + 1
            K1[1, 2] = data[w][1];w = w + 1
            K1[2, 2] = 1
            D1[0, 0] = data[w][1];w = w + 1
            D1[0, 1] = data[w][1];w = w + 1
            D1[0, 4] = data[w][1];w = w + 1
            D1[0, 2] = data[w][1];w = w + 1
            D1[0, 3] = data[w][1];w = w + 1
            K2[0, 0] = data[w][1];w = w + 1
            K2[1, 1] = data[w][1];w = w + 1
            K2[0, 1] = data[w][1];w = w + 1
            K2[0, 2] = data[w][1];w = w + 1
            K2[1, 2] = data[w][1];w = w + 1
            K2[2, 2] = 1
            D2[0, 0] = data[w][1];w = w + 1
            D2[0, 1] = data[w][1];w = w + 1
            D2[0, 4] = data[w][1];w = w + 1
            D2[0, 2] = data[w][1];w = w + 1
            D2[0, 3] = data[w][1];w = w + 1
            TRANS[0,0] = data[w][1];w = w + 1
            TRANS[0,1] = data[w][1];w = w + 1
            TRANS[0,2] = data[w][1];w = w + 1
            ANGLE[0] = data[w][1];w = w + 1
            ANGLE[1] = data[w][1];w = w + 1
            ANGLE[2] = data[w][1]

            ROT = Rotation.from_euler('xyz', ANGLE, degrees=True).as_matrix()

        calib = {1: K1, 2: D1, 3: K2, 4: D2, 5: ROT, 6: TRANS}

        del data

        console.insert(tk.END, f'Intrinsic matrix of the master camera (L)\n{calib[1]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Lens distortion coefficients of the master camera (L)\n{calib[2]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Intrinsic matrix of the slave camera (R)\n{calib[3]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Lens distortion coefficients of the slave camera (R)\n{calib[4]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Rotation matrix (R)\n{calib[5]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Translation vector (T)\n{calib[6]}\n\n')
        console.see('insert')

        console.insert(tk.END, 'Calibration data has been successfully imported\n\n')
        console.see('insert')

        test_calib = True

########################################################################################################################
# Save function - DIC parameters
########################################################################################################################
def save(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny, Opi,
    OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation, Filtering, Kernel):

    if file_var.get():

        f = open(file.get(),"w")

        f.write('iCorrVision-3D Correlation Module - '+str(datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")))
        f.write('\nImage captured folder:\n')
        f.write(str(capturedFolder.get().rstrip("\n")))
        f.write('\nCalibration file:\n')
        f.write(str(calibFile.get().rstrip("\n")))
        f.write('\nReference subset size for stereo correlation:\n')
        f.write(str(SubIrS.get()))
        f.write('\nSearch subset size for stereo correlation:\n')
        f.write(str(SubIbS.get()))
        f.write('\nReference subset size for temporal correlation:\n')
        f.write(str(SubIrT.get()))
        f.write('\nSearch subset size for temporal correlation:\n')
        f.write(str(SubIbT.get()))
        f.write('\nSubset step:\n')
        f.write(str(Step.get()))
        f.write('\nNumber of steps in x direction:\n')
        f.write(str(Nx.get()))
        f.write('\nNumber of steps in y direction:\n')
        f.write(str(Ny.get()))
        f.write('\nInterpolation type:\n')
        f.write(str(Interpolation.get().rstrip("\n")))
        f.write('\nImage interpolation factor (kb):\n')
        f.write(str(Opi.get()))
        f.write('\nSubpixel level (ka):\n')
        f.write(str(OpiSub.get()))
        f.write('\nCorrelation type:\n')
        f.write(str(Correlation.get().rstrip("\n")))
        f.write('\nFiltering:\n')
        f.write(str(Filtering.get().rstrip("\n")))
        f.write('\nKernel size (max is 5):\n')
        f.write(str(Kernel.get()))
        f.write('\nMethod:\n')
        f.write(str(Method.get().rstrip("\n")))
        f.write('\nCorrelation criterion (max is 1):\n')
        f.write(str(Criterion.get()))
        f.write('\nSelected version:\n')
        f.write(str(Version.get().rstrip("\n")))
        f.write('\nType of mesh cut:\n')
        f.write(str(TypeCut.get().rstrip("\n")))
        f.write('\nNumber of cuts:\n')
        f.write(str(NumCut.get()))
        f.write('\nContrast adjust:\n')
        f.write(str(Adjust.get()))
        f.close()

        console.insert(tk.END,
                       '##################################################################################################################\n\n')
        console.insert(tk.END, f'Data was successfully saved in {file.get()}\n\n')
        console.see('insert')

    else:

        save_as(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
            Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
            Filtering, Kernel)

########################################################################################################################
# Save as function - DIC parameters
########################################################################################################################
def save_as(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
    Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
    Filtering, Kernel):

    file_var.set(True)

    console.insert(tk.END, 'Indicate a .dat file to save the DIC parameters\n\n')
    console.see('insert')

    file.set(filedialog.asksaveasfilename())

    menu.title('iCorrVision-3D Correlation Module '+V+' - '+ntpath.basename(file.get()))

    f = open(file.get(),"w+")

    f.write('iCorrVision-3D Correlation Module  - '+str(datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")))
    f.write('\nImage captured folder:\n')
    f.write(str(capturedFolder.get().rstrip("\n")))
    f.write('\nCalibration file:\n')
    f.write(str(calibFile.get().rstrip("\n")))
    f.write('\nReference subset size for stereo correlation:\n')
    f.write(str(SubIrS.get()))
    f.write('\nSearch subset size for stereo correlation:\n')
    f.write(str(SubIbS.get()))
    f.write('\nReference subset size for temporal correlation:\n')
    f.write(str(SubIrT.get()))
    f.write('\nSearch subset size for temporal correlation:\n')
    f.write(str(SubIbT.get()))
    f.write('\nSubset step:\n')
    f.write(str(Step.get()))
    f.write('\nNumber of steps in x direction:\n')
    f.write(str(Nx.get()))
    f.write('\nNumber of steps in y direction:\n')
    f.write(str(Ny.get()))
    f.write('\nInterpolation type:\n')
    f.write(str(Interpolation.get().rstrip("\n")))
    f.write('\nImage interpolation factor (kb):\n')
    f.write(str(Opi.get()))
    f.write('\nSubpixel level (ka):\n')
    f.write(str(OpiSub.get()))
    f.write('\nCorrelation type:\n')
    f.write(str(Correlation.get().rstrip("\n")))
    f.write('\nFiltering:\n')
    f.write(str(Filtering.get().rstrip("\n")))
    f.write('\nKernel size (max is 5):\n')
    f.write(str(Kernel.get()))
    f.write('\nMethod:\n')
    f.write(str(Method.get().rstrip("\n")))
    f.write('\nCorrelation criterion (max is 1):\n')
    f.write(str(Criterion.get()))
    f.write('\nSelected version:\n')
    f.write(str(Version.get().rstrip("\n")))
    f.write('\nType of mesh cut:\n')
    f.write(str(TypeCut.get().rstrip("\n")))
    f.write('\nNumber of cuts:\n')
    f.write(str(NumCut.get()))
    f.write('\nContrast adjust:\n')
    f.write(str(Adjust.get()))
    f.close()

    console.insert(tk.END,
                   '##################################################################################################################\n\n')
    console.insert(tk.END, f'Data was successfully saved in {file.get()}\n\n')
    console.see('insert')

########################################################################################################################
# Load function - DIC parameters
########################################################################################################################
def load(menu, captured_status, console, canvas_left, canvas_right, file_var, V, file, capturedFolder, calibFile,
    calib_status, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method,
    Correlation, Criterion, Step, Interpolation, Filtering, Kernel):

    global test_captured, fileNamesLeft, fileNamesRight, calib, Format, Images

    file_load = filedialog.askopenfilename()

    if file_load != '':

        menu.title('iCorrVision-3D Correlation Module '+V+' - '+ntpath.basename(file_load))

        file.set(file_load)

        l = open(file_load,"r")
        w = 2
        lines = l.readlines()
        capturedFolder.set(lines[w].rstrip("\n")); w = w + 2
        calibFile.set(lines[w].rstrip("\n")); w = w + 2
        SubIrS.set(lines[w]); w = w + 2
        SubIbS.set(lines[w]); w = w + 2
        SubIrT.set(lines[w]); w = w + 2
        SubIbT.set(lines[w]); w = w + 2
        Step.set(lines[w]); w = w + 2
        Nx.set(lines[w]); w = w + 2
        Ny.set(lines[w]); w = w + 2
        Interpolation.set(lines[w].rstrip("\n")); w = w + 2
        Opi.set(lines[w]); w = w + 2
        OpiSub.set(lines[w]); w = w + 2
        Correlation.set(lines[w].rstrip("\n")); w = w + 2
        Filtering.set(lines[w].rstrip("\n")); w = w + 2
        Kernel.set(lines[w]); w = w + 2
        Method.set(lines[w].rstrip("\n")); w = w + 2
        Criterion.set(lines[w]); w = w + 2
        Version.set(lines[w].rstrip("\n")); w = w + 2
        TypeCut.set(lines[w].rstrip("\n")); w = w + 2
        NumCut.set(lines[w]); w = w + 2
        Adjust.set(lines[w])

        CapturedImagesFolderName = capturedFolder.get().rsplit('/', 1)[1]
        capturedFolder.set(file_load.rsplit('/', 1)[0] + '/' + CapturedImagesFolderName)
        fileNamesLeft = sorted(glob.glob(capturedFolder.get() + '/Left/*'), key=stringToList)
        fileNamesRight = sorted(glob.glob(capturedFolder.get() + '/Right/*'), key=stringToList)
        Format = '.' + fileNamesLeft[0].rsplit('.', 1)[1]
        Images = len(fileNamesLeft)

        captured_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END,
                       '##################################################################################################################\n\n')
        console.insert(tk.END, f'Image captured folder - {capturedFolder.get()}\n\n')
        console.see('insert')

        # Left image resolution correction:
        fig_left = plt.figure()
        ax = fig_left.gca()
        dxplot = int(cv.imread(fileNamesLeft[0]).shape[1])
        dyplot = int(cv.imread(fileNamesLeft[0]).shape[0])

        ratio_plot = dxplot / dyplot;

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesLeft[0]), zorder=2)
            ax.plot([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                     dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                     0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                             dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                             0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], color='black',
                            zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesLeft[0]), zorder=2)
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                    [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                     +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                     0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                            [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                             +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                             0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        fig_left.canvas.draw()

        image_left = np.frombuffer(fig_left.canvas.tostring_rgb(), dtype=np.uint8)
        w, h = fig_left.canvas.get_width_height()
        image_left = np.flip(image_left.reshape((h, w, 3)), axis=0)

        # Right image resolution correction:
        fig_right = plt.figure()
        ax = fig_right.gca()
        dxplot = int(cv.imread(fileNamesRight[0]).shape[1])
        dyplot = int(cv.imread(fileNamesRight[0]).shape[0])

        ratio_plot = dxplot / dyplot;

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesRight[0]), zorder=2)
            ax.plot([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                     dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                     0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                             dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                             0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], color='black',
                            zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesRight[0]), zorder=2)
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                    [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                     +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                     0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                            [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                             +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                             0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        fig_right.canvas.draw()

        image_right = np.frombuffer(fig_right.canvas.tostring_rgb(), dtype=np.uint8)
        w, h = fig_right.canvas.get_width_height()
        image_right = np.flip(image_right.reshape((h, w, 3)), axis=0)

        plt.cla()
        plt.clf()

        image_left = cv.resize(image_left, (426, 320))
        cv.putText(image_left, 'MASTER L', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
        image_left = ImageTk.PhotoImage(Image.fromarray(image_left))

        image_right = cv.resize(image_right, (426, 320))
        cv.putText(image_right, 'SLAVE R', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
        image_right = ImageTk.PhotoImage(Image.fromarray(image_right))

        canvas_left.image_left = image_left
        canvas_left.configure(image = image_left)

        canvas_right.image_right = image_right
        canvas_right.configure(image = image_right)

        console.insert(tk.END, f'{Images} image pairs were imported with {Format} format\n\n')
        console.see('insert')

        test_captured = True
        file_var.set(True)

        CalibrationFileName = calibFile.get().rsplit('/', 1)[1]
        calibFile.set(file_load.rsplit('/', 1)[0] + '/' + CalibrationFileName)
        calib_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'Calibration file - {calibFile.get()}\n\n')
        console.see('insert')

        with open(calibFile.get()) as f:
            reader = csv.reader(f, delimiter=';')
            data = [(col1, float(col2)) for col1, col2 in reader]
            f.close()

        if data[0][1] == 0:
            K1 = np.zeros((3, 3))
            D1 = np.zeros((1, 5))
            K2 = np.zeros((3, 3))
            D2 = np.zeros((1, 5))
            ROT = np.zeros((3, 3))
            TRANS = np.zeros((1, 3))

            w = 1
            K1[0, 0] = data[w][1];w = w + 1
            K1[1, 1] = data[w][1];w = w + 1
            K1[0, 1] = data[w][1];w = w + 1
            K1[0, 2] = data[w][1];w = w + 1
            K1[1, 2] = data[w][1];w = w + 1
            K1[2, 2] = 1
            D1[0, 0] = data[w][1];w = w + 1
            D1[0, 1] = data[w][1];w = w + 1
            D1[0, 4] = data[w][1];w = w + 1
            D1[0, 2] = data[w][1];w = w + 1
            D1[0, 3] = data[w][1];w = w + 1
            K2[0, 0] = data[w][1];w = w + 1
            K2[1, 1] = data[w][1];w = w + 1
            K2[0, 1] = data[w][1];w = w + 1
            K2[0, 2] = data[w][1];w = w + 1
            K2[1, 2] = data[w][1];w = w + 1
            K2[2, 2] = 1
            D2[0, 0] = data[w][1];w = w + 1
            D2[0, 1] = data[w][1];w = w + 1
            D2[0, 4] = data[w][1];w = w + 1
            D2[0, 2] = data[w][1];w = w + 1
            D2[0, 3] = data[w][1];w = w + 1
            TRANS[0, 0] = data[w][1];w = w + 1
            TRANS[0, 1] = data[w][1];w = w + 1
            TRANS[0, 2] = data[w][1];w = w + 1
            ROT[0, 0] = data[w][1];w = w + 1
            ROT[0, 1] = data[w][1];w = w + 1
            ROT[0, 2] = data[w][1];w = w + 1
            ROT[1, 0] = data[w][1];w = w + 1
            ROT[1, 1] = data[w][1];w = w + 1
            ROT[1, 2] = data[w][1];w = w + 1
            ROT[2, 0] = data[w][1];w = w + 1
            ROT[2, 1] = data[w][1];w = w + 1
            ROT[2, 2] = data[w][1]

        else:
            K1 = np.zeros((3, 3))
            D1 = np.zeros((1, 5))
            K2 = np.zeros((3, 3))
            D2 = np.zeros((1, 5))
            TRANS = np.zeros((1, 3))
            ANGLE = np.zeros(3)

            w = 1
            K1[0, 0] = data[w][1];w = w + 1
            K1[1, 1] = data[w][1];w = w + 1
            K1[0, 1] = data[w][1];w = w + 1
            K1[0, 2] = data[w][1];w = w + 1
            K1[1, 2] = data[w][1];w = w + 1
            K1[2, 2] = 1
            D1[0, 0] = data[w][1];w = w + 1
            D1[0, 1] = data[w][1];w = w + 1
            D1[0, 4] = data[w][1];w = w + 1
            D1[0, 2] = data[w][1];w = w + 1
            D1[0, 3] = data[w][1];w = w + 1
            K2[0, 0] = data[w][1];w = w + 1
            K2[1, 1] = data[w][1];w = w + 1
            K2[0, 1] = data[w][1];w = w + 1
            K2[0, 2] = data[w][1];w = w + 1
            K2[1, 2] = data[w][1];w = w + 1
            K2[2, 2] = 1
            D2[0, 0] = data[w][1];w = w + 1
            D2[0, 1] = data[w][1];w = w + 1
            D2[0, 4] = data[w][1];w = w + 1
            D2[0, 2] = data[w][1];w = w + 1
            D2[0, 3] = data[w][1];w = w + 1
            TRANS[0, 0] = data[w][1];w = w + 1
            TRANS[0, 1] = data[w][1];w = w + 1
            TRANS[0, 2] = data[w][1];w = w + 1
            ANGLE[0] = data[w][1];w = w + 1
            ANGLE[1] = data[w][1];w = w + 1
            ANGLE[2] = data[w][1]

            ROT = Rotation.from_euler('xyz', ANGLE, degrees=True).as_matrix()

        calib = {1: K1, 2: D1, 3: K2, 4: D2, 5: ROT, 6: TRANS}

        del data

        console.insert(tk.END, f'Intrinsic matrix of the master camera (L)\n{calib[1]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Lens distortion coefficients of the master camera (L)\n{calib[2]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Intrinsic matrix of the slave camera (R)\n{calib[3]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Lens distortion coefficients of the slave camera (R)\n{calib[4]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Rotation matrix (R)\n{calib[5]}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Translation vector (T)\n{calib[6]}\n\n')
        console.see('insert')

        console.insert(tk.END, 'Calibration data has been successfully imported\n\n')
        console.see('insert')

        test_calib = True

    else:

        console.insert(tk.END, f'No files were selected \n\n')
        console.see('insert')

########################################################################################################################
# Function to clear data and restore GUI
########################################################################################################################
def clear(menu, CurrentDir, captured_status, console, console_process, progression, progression_bar, canvas_left,
    canvas_right, canvas_text, file_var, V, file, capturedFolder, calibFile, calib_status, SubIrS, SubIbS,
    SubIrT, SubIbT, Nx, Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion,
    Step, Interpolation, Filtering, Kernel):

    file_var.set(False)

    menu.title('iCorrVision-3D Correlation Module '+V)

    console.delete('1.0', END)
    console_process.delete('1.0', END)

    capturedFolder.set(''); captured_status.configure(bg = 'red')
    calibFile.set(''); calib_status.configure(bg = 'red')
    SubIrS.set(0)
    SubIbS.set(0)
    SubIrT.set(0)
    SubIbT.set(0)
    Step.set(0)
    Nx.set(0)
    Ny.set(0)
    Opi.set(0)
    OpiSub.set(1)
    Adjust.set(0.0)
    Criterion.set(0.0)
    NumCut.set(0)
    Version.set('Select')
    TypeCut.set('None')
    Correlation.set('Select')
    Method.set('Select')
    Interpolation.set('Select')
    Filtering.set('Select')
    Kernel.set(0)

    image_black = Image.open(CurrentDir+'\static\ImageBlack.tiff')
    image_black = image_black.resize((426, 320), Image.ANTIALIAS)
    image_black_re = ImageTk.PhotoImage(image_black)
    canvas_right.image_black_re = image_black_re
    canvas_right.configure(image = image_black_re)
    canvas_left.image_black_re = image_black_re
    canvas_left.configure(image = image_black_re)

    console.insert(tk.END,
                   f'#######################################################################################################  {V}\n\n'
                   '                                     **  iCorrVision-3D Correlation Module **                                     \n\n'
                   '##################################################################################################################\n\n')

    console.insert(tk.END,
                   'Please load project or select the image captured folder, calibration file and DIC settings\n\n')
    console.see('insert')

    progression.coords(progression_bar, 0, 0, 0, 25); progression.itemconfig(canvas_text, text='')

########################################################################################################################
# Circular ROI function
########################################################################################################################
def CircularROI_DIC(menu, console, title, img):
    # Module global variables:
    global fileNamesLeft, points, pressed, text, xCenter, yCenter, dxCirc, dyCirc, ptn

    # Set drawing mode to False:
    pressed = False

    text = title

    # Mouse events:
    def click_event_Circular_DIC(event, x, y, flags, param):
        global points, pressed, text, ptn

        # Save previous state on cache:
        cache = img.copy()

        if event == cv.EVENT_LBUTTONDOWN:
            # Clear points:
            ptn = []
            points = []

            # Set drawing mode to True:
            pressed = True

            # First vertices construction:
            points.append((x, y))  # Save the location of first vertices

        elif event == cv.EVENT_MOUSEMOVE:
            if pressed == True:

                xPL = points[-1][0]
                yPL = points[-1][1]

                xPR = x
                yPR = y

                xCenter = int((xPR + xPL) / 2)
                yCenter = int((yPR + yPL) / 2)

                dxCirc = abs(int((xPR - xPL) / 2))
                dyCirc = abs(int((yPR - yPL) / 2))

                cv.ellipse(cache, (xCenter, yCenter), (dxCirc, dyCirc), 0, 0, 360, 255, 2)

                cv.imshow(text, cache)

        elif event == cv.EVENT_LBUTTONUP:

            # Set drawing mode to False:
            pressed = False

            xPL = points[-1][0]
            yPL = points[-1][1]

            xPR = x
            yPR = y

            xCenter = int((xPR + xPL) / 2)
            yCenter = int((yPR + yPL) / 2)

            dxCirc = abs(int((xPR - xPL) / 2))
            dyCirc = abs(int((yPR - yPL) / 2))

            cv.ellipse(cache, (xCenter, yCenter), (dxCirc, dyCirc), 0, 0, 360, (255,0,0), -1)

            alpha = 0.4  # Transparency factor.

            # Following line overlays transparent rectangle over the image
            cache = cv.addWeighted(cache, alpha, img, 1 - alpha, 0)

            t = np.linspace(0, 2 * pi, 100)
            xEl = xCenter + dxCirc * np.cos(t)
            yEl = yCenter + dyCirc * np.sin(t)

            for w in range(0,100):
                ptn.append((int(xEl[w]),int(yEl[w])))

            cv.imshow(text, cache)

    # Routine created to check the captured images:
    try:
        fileNamesLeft
    except NameError:
        console.insert(tk.END, 'No images were found. Make sure the images have been imported!\n\n')
        console.see('insert')
        messagebox.showerror('Error', 'No images were found. Make sure the images have been imported!')
    else:

        cv.imshow(title, img)
        points = []
        ptn = []

        cv.setMouseCallback(title, click_event_Circular_DIC)

        cv.waitKey(0)  # The USER have to press any key to exit the interface (ENTER)
        cv.destroyAllWindows()

    return ptn

########################################################################################################################
# ROI function
########################################################################################################################
def SelectROI_DIC(menu, console, title, img):
    # Module global variables:
    global fileNamesLeft, points, pressed, text

    # Set drawing mode to False:
    pressed = False

    text = title

    # Mouse events:
    def click_event_DIC(event, x, y, flags, param):
        global points, pressed, text

        # Save previous state on cache:
        cache = img_measure.copy()

        if event == cv.EVENT_LBUTTONDOWN:
            # Clear points:
            points = []

            # Set drawing mode to True:
            pressed = True

            # First vertice construction:
            points.append((x, y))  # Save the location of first vertice

        elif event == cv.EVENT_MOUSEMOVE:
            if pressed == True:
                # First and second vertices construction:
                cv.rectangle(cache, points[-1],(x, y), (0, 0, 255), 1, cv.LINE_AA)
                cv.line(cache, (points[-1][0],int((y+points[-1][1])/2)), (x,int((y+points[-1][1])/2)),(255, 0, 0), 1,
                        cv.LINE_AA)
                cv.line(cache, (int((x + points[-1][0]) / 2), points[-1][1]), (int((x + points[-1][0]) / 2), y),
                        (255, 0, 0), 1, cv.LINE_AA)
                cv.rectangle(cache, (0,0), (int(cache.shape[1]),30), (255, 255, 255), -1)
                cv.putText(cache, f'(x = {x}, y = {y}) - ROI SIZE = {x-points[-1][0]} x {y-points[-1][1]}', (10,20),
                           cv.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1,cv.LINE_AA)
                # Display the ruler on cache image:
                cv.imshow(text, cache)

        elif event == cv.EVENT_LBUTTONUP:

            # Set drawing mode to False:
            pressed = False

            # Display the line used to measure Valpixel:
            cv.rectangle(cache, points[-1], (x, y), (0, 0, 255), 2, cv.FILLED)
            cv.rectangle(cache, (0, 0), (int(cache.shape[1]), 30), (255, 255, 255), -1)
            cv.putText(cache, f'(x = {x}, y = {y}) - ROI SIZE = {x - points[-1][0]} x {y - points[-1][1]}', (10, 20),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
            points.append((x, y))
            cv.imshow(text, cache)

    # Routine created to check the captured images:
    try:
        fileNamesLeft
    except NameError:
        console.insert(tk.END, 'No images were found. Make sure the images have been imported!\n\n')
        console.see('insert')
        messagebox.showerror('Error', 'No images were found. Make sure the images have been imported!')
    else:

        dxfigure = int(img.shape[1])
        dyfigure = int(img.shape[0])

        screen_height = menu.winfo_screenheight() - 100

        # Change size of displayed image:
        if dyfigure > screen_height:
            ratio = screen_height / dyfigure
            img_measure = cv.resize(img, (int(screen_height * dxfigure / dyfigure), screen_height))
            cv.line(img_measure, (0, int(dyfigure / 2)), (dxfigure, int(dyfigure / 2)), (255, 255, 255), 1,
                    cv.LINE_AA)
            cv.line(img_measure, (int(dxfigure / 2), 0), (int(dxfigure / 2), dyfigure), (255, 255, 255), 1,
                    cv.LINE_AA)
            cv.imshow(title, img_measure)
            points = []
            cv.setMouseCallback(title, click_event_DIC)

        else:
            img_measure = img
            cv.line(img_measure, (0, int(dyfigure / 2)), (dxfigure, int(dyfigure / 2)), (255, 255, 255), 1,
                    cv.LINE_AA)
            cv.line(img_measure, (int(dxfigure / 2), 0), (int(dxfigure / 2), dyfigure), (255, 255, 255), 1,
                    cv.LINE_AA)
            cv.imshow(title, img_measure)
            points = []
            cv.setMouseCallback(title, click_event_DIC)

        cv.waitKey(0)  # Press any key to exit the interface (ENTER)
        cv.destroyAllWindows()

        ptn = np.zeros((2, 2))

        # Points location correction due to image correction:
        if dyfigure > screen_height:
            for i in [0, 1]:
                for j in [0, 1]:
                    ptn[i][j] = points[i][j] / ratio

        else:
            ptn = points

    xinitline = ptn[0][0]
    yinitline = ptn[0][1]
    dxline = ptn[1][0]-ptn[0][0]
    dyline = ptn[1][1]-ptn[0][1]

    return xinitline,yinitline,dxline,dyline

########################################################################################################################
# Function to check the contrast according to the contrast factor
########################################################################################################################
def verify(Adjust, canvas_left, canvas_right, console):
    global fileNamesLeft, fileNamesRight, test_constrast

    console.insert(tk.END,
                   '##################################################################################################################\n\n')
    console.see('insert')

    try:
        fileNamesLeft, fileNamesRight
    except NameError:
        console.insert(tk.END, 'Import the captured image pairs before running the contrast adjustment test!\n\n')
        console.see('insert')
        messagebox.showerror('Error','Import the captured image pairs before running the contrast adjustment test!')
    else:

        adjust = cv.createCLAHE(clipLimit=Adjust.get(), tileGridSize=(8,8))

        # Left image resolution correction:
        fig_left = plt.figure()
        ax = fig_left.gca()
        dxplot = int(cv.imread(fileNamesLeft[0]).shape[1])
        dyplot = int(cv.imread(fileNamesLeft[0]).shape[0])

        ratio_plot = dxplot / dyplot;

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesLeft[0],0), zorder=2)
            ax.plot([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                     dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                     0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                             dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                             0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], color='black',
                            zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesLeft[0],0), zorder=2)
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                    [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                     +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                     0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                            [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                             +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                             0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        fig_left.canvas.draw()

        image_left = np.frombuffer(fig_left.canvas.tostring_rgb(), dtype=np.uint8)
        w, h = fig_left.canvas.get_width_height()
        image_left = np.flip(image_left.reshape((h, w, 3)), axis=0)

        # Right image resolution correction:
        fig_right = plt.figure()
        ax = fig_right.gca()
        dxplot = int(cv.imread(fileNamesRight[0]).shape[1])
        dyplot = int(cv.imread(fileNamesRight[0]).shape[0])

        ratio_plot = dxplot / dyplot;

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesRight[0],0), zorder=2)
            ax.plot([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                     dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                     0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between([0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                             dxplotdark - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
                             0 - dxplotdark / 2 + dxplot / 2], [0, dyplotdark, dyplotdark, 0, 0], color='black',
                            zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesRight[0],0), zorder=2)
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                    [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                     +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                     0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                            [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                             +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                             0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        fig_right.canvas.draw()

        image_right = np.frombuffer(fig_right.canvas.tostring_rgb(), dtype=np.uint8)
        w, h = fig_right.canvas.get_width_height()
        image_right = np.flip(image_right.reshape((h, w, 3)), axis=0)

        plt.cla()
        plt.clf()

        image_left = cv.cvtColor(image_left, cv.COLOR_RGB2GRAY)
        image_left = adjust.apply(cv.resize(image_left, (426, 320)))
        image_left = cv.cvtColor(image_left,cv.COLOR_GRAY2RGB)
        cv.putText(image_left,'MASTER L',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
        image_left = ImageTk.PhotoImage (Image.fromarray (image_left))
        canvas_left.image_left = image_left
        canvas_left.configure(image = image_left)

        image_right = cv.cvtColor(image_right, cv.COLOR_RGB2GRAY)
        image_right = adjust.apply(cv.resize(image_right, (426, 320)))
        image_right = cv.cvtColor(image_right,cv.COLOR_GRAY2RGB)
        cv.putText(image_right,'SLAVE R',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
        image_right = ImageTk.PhotoImage (Image.fromarray (image_right))
        canvas_right.image_right = image_right
        canvas_right.configure(image = image_right)

        console.insert(tk.END, f'All images will be adjusted according to the given contrast factor of {Adjust.get()}\n\n')
        console.see('insert')

        test_constrast = True

########################################################################################################################
# Function to close the software
########################################################################################################################
def close(menu):
    global t2
    ans = messagebox.askquestion('Close','Are you sure you want to exit iCorrVision-3D Correlation module?',icon ='question')
    if ans == 'yes':

        menu.destroy()
        menu.quit()

########################################################################################################################
# Abort function
########################################################################################################################
def abort(abort_param):
    abort_param.set(True)

########################################################################################################################
# 3D reconstruction function
########################################################################################################################
def ReconstructionWCS(xL, yL, xR, yR, calib):

    # Left camera parameters (master):
    IntrinsicL = calib[1]

    fLx = IntrinsicL[0,0]
    fLy = IntrinsicL[1,1]
    skL = IntrinsicL[0,1]
    cLx = IntrinsicL[0,2]
    cLy = IntrinsicL[1,2]

    # Right camera parameters (slave):
    IntrinsicR = calib[3]

    fRx = IntrinsicR[0,0]
    fRy = IntrinsicR[1,1]
    skR = IntrinsicR[0,1]
    cRx = IntrinsicR[0,2]
    cRy = IntrinsicR[1,2]

    # Relation between L and R cameras:
    Rc = calib[5];
    tc = calib[6];

    # M matrix:
    M = np.zeros((4,3))
    M[0,0] = fLx;
    M[0,1] = skL;
    M[0,2] = cLx - xL;
    M[1,0] = 0.0;
    M[1,1] = fLy;
    M[1,2] = cLy - yL;
    M[2,0] = Rc[0,0]*fRx + Rc[1,0]*skR + Rc[2,0]*(cRx - xR);
    M[2,1] = Rc[0,1]*fRx + Rc[1,1]*skR + Rc[2,1]*(cRx - xR);
    M[2,2] = Rc[0,2]*fRx + Rc[1,2]*skR + Rc[2,2]*(cRx - xR);
    M[3,0] = Rc[1,0]*fRy + Rc[2,0]*(cRy - yR);
    M[3,1] = Rc[1,1]*fRy + Rc[2,1]*(cRy - yR);
    M[3,2] = Rc[1,2]*fRy + Rc[2,2]*(cRy - yR);

    # MLPI matrix:
    MLPI = np.matmul(M.transpose(),M);
    MLPII = np.matmul(np.linalg.inv(MLPI),M.transpose());

    # b vector:
    b = np.zeros((4))
    b[0] = 0;
    b[1] = 0;
    b[2] = -(tc[0,0]*fRx + tc[0,1]*skR + tc[0,2]*(cRx - xR));
    b[3] = -(tc[0,1]*fRy + tc[0,2]*(cRy - yR));

    # 3D reconstruction - WORLD COORDINATE SYSTEM (WCS):
    WCS = np.matmul(MLPII,b.transpose());
    Xw = WCS[0]; Yw = WCS[1]; Zw = WCS[2];

    return Xw, Yw, Zw

########################################################################################################################
# 2D Digital Image Correlation function V1 - Stereo Correlation
########################################################################################################################
def Corr2D_Stereo_V1(Image, SubIr, SubIb, x0_mem, x0_shape, y0_mem, y0_shape, x1_mem, x1_shape, y1_mem, y1_shape, Iun,
    Id, Method, Criterion,i0,i1,j0,j1):
    global process_x0_mem, process_x0_shape, process_y0_mem, process_y0_shape
    global process_x1_mem, process_x1_shape, process_y1_mem, process_y1_shape

    process_x0_mem = x0_mem
    process_x0_shape = x0_shape
    process_y0_mem = y0_mem
    process_y0_shape = y0_shape
    process_x1_mem = x1_mem
    process_x1_shape = x1_shape
    process_y1_mem = y1_mem
    process_y1_shape = y1_shape

    x0 = np.frombuffer(process_x0_mem, dtype=np.float64).reshape(process_x0_shape)
    y0 = np.frombuffer(process_y0_mem, dtype=np.float64).reshape(process_y0_shape)
    x1 = np.frombuffer(process_x1_mem, dtype=np.float64).reshape(process_x1_shape)
    y1 = np.frombuffer(process_y1_mem, dtype=np.float64).reshape(process_y1_shape)

    for i in range(i0,i1):
        for j in range(j0,j1):
            # Test nan values:
            if np.isnan(x0[Image][i][j]):
                # If it exists, node ij assumes value nan:
                x1[Image][i][j] = float('nan'); y1[Image][i][j] = float('nan');
            else:
                # Estimate the first node position for the reference and search images:
                xrmin = int(x0[Image][i][j] - (SubIr)/2)
                yrmin = int(y0[Image][i][j] - (SubIr)/2)
                xbmin = int(x0[Image][i][j] - (SubIb)/2)
                if xbmin < 0:
                    xbmin = 0
                    SubIb_x = x0[Image][i][j]*2
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb_x - SubIr) / 2
                    testexp=True
                else:
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb - SubIr) / 2
                    testexp=False

                ybmin = int(y0[Image][i][j] - (SubIb)/2)
                if ybmin < 0:
                    ybmin = 0
                    SubIb_y = y0[Image][i][j] * 2

                    ypeak_ac = (SubIb_y - SubIr) / 2
                    testeyp = True
                else:
                    ypeak_ac = (SubIb - SubIr) / 2
                    testeyp = False

                # Crop reference and search images according to SubIr and SubIb values:
                Ir = Iun[yrmin:yrmin + SubIr, xrmin:xrmin + SubIr]
                Ib = Id[ybmin:ybmin + SubIb, xbmin:xbmin + SubIb]

                try:
                    # Correlation:
                    c = cv.matchTemplate(Ib, Ir, Method)

                    # Search for the maximum coefficient of correlation and its position:
                    _, maxVal, _, maxc = cv.minMaxLoc(c)

                    # If the maximum coefficient of correlation is lower than the correlation criterion, the node ij assumes the
                    # value nan, indicating the loss of correlation:
                    if maxVal < Criterion:

                        ui = float('nan')
                        vi = float('nan')

                    else:

                        xc = np.linspace(maxc[0] - 2, maxc[0] + 2, 5)
                        yc = np.linspace(maxc[1] - 2, maxc[1] + 2, 5)

                        cc = c[maxc[1] - 2:maxc[1] + 3, maxc[0] - 2:maxc[0] + 3]

                        xcint = xc; ycint = yc;

                        f = interp2d(xc, yc, cc, kind='cubic')

                        del cc

                        ccinterp = f(xcint, ycint)

                        maxc_interp = np.unravel_index(ccinterp.argmax(), ccinterp.shape)

                        xpeak = xcint[maxc_interp[0]];
                        ypeak = ycint[maxc_interp[1]]

                        # Displacement calculation:
                        ui = xpeak - xpeak_ac
                        vi = ypeak - ypeak_ac

                except:
                    ui = float('nan')
                    vi = float('nan')

                x1[Image][i][j] = x0[Image][i][j] + ui
                y1[Image][i][j] = y0[Image][i][j] + vi

########################################################################################################################
# 2D Digital Image Correlation function V1 - Temporal Correlation L
########################################################################################################################
def Corr2D_Temporal_L_V1(Image0, Image1, SubIr, SubIb, xL_mem, xL_shape, yL_mem, yL_shape, uL_mem, uL_shape, vL_mem,
    vL_shape, Iun, Id, Type, Method, Criterion, i0, i1, j0, j1):
    global process_x0_mem, process_x0_shape, process_y0_mem, process_y0_shape
    global process_u0_mem, process_u0_shape, process_v0_mem, process_v0_shape

    process_x0_mem = xL_mem
    process_x0_shape = xL_shape
    process_y0_mem = yL_mem
    process_y0_shape = yL_shape
    process_u0_mem = uL_mem
    process_u0_shape = uL_shape
    process_v0_mem = vL_mem
    process_v0_shape = vL_shape

    x0 = np.frombuffer(process_x0_mem, dtype=np.float64).reshape(process_x0_shape)
    y0 = np.frombuffer(process_y0_mem, dtype=np.float64).reshape(process_y0_shape)
    u0 = np.frombuffer(process_u0_mem, dtype=np.float64).reshape(process_u0_shape)
    v0 = np.frombuffer(process_v0_mem, dtype=np.float64).reshape(process_v0_shape)

    for i in range(i0, i1):
        for j in range(j0, j1):
            # Test nan values:
            if np.isnan(x0[Image0][i][j]):
                # If it exists, node ij assumes value nan:
                x0[Image1][i][j] = float('nan'); y0[Image1][i][j] = float('nan'); u0[Image1][i][j] = float('nan'); v0[Image1][i][j] = float('nan')
            else:
                # Estimate the first node position for the reference and search images:
                xrmin = int(x0[Image0][i][j] - (SubIr)/2)
                yrmin = int(y0[Image0][i][j] - (SubIr)/2)
                xbmin = int(x0[Image0][i][j] - (SubIb)/2)
                if xbmin < 0:
                    xbmin = 0
                    SubIb_x = x0[Image0][i][j]*2
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb_x - SubIr) / 2
                    testexp=True
                else:
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb - SubIr) / 2
                    testexp=False

                ybmin = int(y0[Image0][i][j] - (SubIb)/2)
                if ybmin < 0:
                    ybmin = 0
                    SubIb_y = y0[Image0][i][j] * 2

                    ypeak_ac = (SubIb_y - SubIr) / 2
                    testeyp = True
                else:
                    ypeak_ac = (SubIb - SubIr) / 2
                    testeyp = False

                # Crop reference and search images according to SubIr and SubIb values:
                Ir = Iun[yrmin:yrmin + SubIr, xrmin:xrmin + SubIr]
                Ib = Id[ybmin:ybmin + SubIb, xbmin:xbmin + SubIb]

                try:
                    # Correlation:
                    c = cv.matchTemplate(Ib, Ir, Method)

                    # Search for the maximum coefficient of correlation and its position:
                    _, maxVal, _, maxc = cv.minMaxLoc(c)

                    # If the maximum coefficient of correlation is lower than the correlation criterion, the node ij assumes the
                    # value nan, indicating the loss of correlation:
                    if maxVal < Criterion:

                        ui = float('nan')
                        vi = float('nan')

                    else:

                        xc = np.linspace(maxc[0] - 2, maxc[0] + 2, 5)
                        yc = np.linspace(maxc[1] - 2, maxc[1] + 2, 5)

                        cc = c[maxc[1] - 2:maxc[1] + 3, maxc[0] - 2:maxc[0] + 3]

                        xcint = xc; ycint = yc;

                        f = interp2d(xc, yc, cc, kind='cubic')

                        del cc

                        ccinterp = f(xcint, ycint)

                        maxc_interp = np.unravel_index(ccinterp.argmax(), ccinterp.shape)

                        xpeak = xcint[maxc_interp[0]];
                        ypeak = ycint[maxc_interp[1]]

                        # Displacement calculation:
                        ui = xpeak - xpeak_ac
                        vi = ypeak - ypeak_ac

                except:
                    ui = float('nan')
                    vi = float('nan')

                if Type == 'Lagrangian':

                    x0[Image1][i][j] = x0[Image0][i][j] + ui
                    y0[Image1][i][j] = y0[Image0][i][j] + vi
                    u0[Image1][i][j] = ui;
                    v0[Image1][i][j] = vi;

                else:

                    x0[Image1][i][j] = x0[Image0][i][j]
                    y0[Image1][i][j] = y0[Image0][i][j]
                    u0[Image1][i][j] = ui;
                    v0[Image1][i][j] = vi;

########################################################################################################################
# 2D Digital Image Correlation function V1 - Temporal Correlation R
########################################################################################################################
def Corr2D_Temporal_R_V1(Image0, Image1, SubIr, SubIb, xR_mem, xR_shape, yR_mem, yR_shape, uR_mem, uR_shape, vR_mem,
    vR_shape, Iun, Id, Type, Method, Criterion, i0, i1, j0, j1):
    global process_x1_mem, process_x1_shape, process_y1_mem, process_y1_shape
    global process_u1_mem, process_u1_shape, process_v1_mem, process_v1_shape

    process_x1_mem = xR_mem
    process_x1_shape = xR_shape
    process_y1_mem = yR_mem
    process_y1_shape = yR_shape
    process_u1_mem = uR_mem
    process_u1_shape = uR_shape
    process_v1_mem = vR_mem
    process_v1_shape = vR_shape

    x1 = np.frombuffer(process_x1_mem, dtype=np.float64).reshape(process_x1_shape)
    y1 = np.frombuffer(process_y1_mem, dtype=np.float64).reshape(process_y1_shape)
    u1 = np.frombuffer(process_u1_mem, dtype=np.float64).reshape(process_u1_shape)
    v1 = np.frombuffer(process_v1_mem, dtype=np.float64).reshape(process_v1_shape)

    for i in range(i0, i1):
        for j in range(j0, j1):
            # Test nan values:
            if np.isnan(x1[Image0][i][j]):
                # If it exists, node ij assumes value nan:
                x1[Image1][i][j] = float('nan');
                y1[Image1][i][j] = float('nan');
                u1[Image1][i][j] = float('nan');
                v1[Image1][i][j] = float('nan')
            else:
                # Estimate the first node position for the reference and search images:
                xrmin = int(x1[Image0][i][j] - (SubIr) / 2)
                yrmin = int(y1[Image0][i][j] - (SubIr) / 2)
                xbmin = int(x1[Image0][i][j] - (SubIb) / 2)
                if xbmin < 0:
                    xbmin = 0
                    SubIb_x = x1[Image0][i][j] * 2
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb_x - SubIr) / 2
                    testexp = True
                else:
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb - SubIr) / 2
                    testexp = False

                ybmin = int(y1[Image0][i][j] - (SubIb) / 2)
                if ybmin < 0:
                    ybmin = 0
                    SubIb_y = y1[Image0][i][j] * 2

                    ypeak_ac = (SubIb_y - SubIr) / 2
                    testeyp = True
                else:
                    ypeak_ac = (SubIb - SubIr) / 2
                    testeyp = False

                # Crop reference and search images according to SubIr and SubIb values:
                Ir = Iun[yrmin:yrmin + SubIr, xrmin:xrmin + SubIr]
                Ib = Id[ybmin:ybmin + SubIb, xbmin:xbmin + SubIb]

                try:
                    # Correlation:
                    c = cv.matchTemplate(Ib, Ir, Method)

                    # Search for the maximum coefficient of correlation and its position:
                    _, maxVal, _, maxc = cv.minMaxLoc(c)

                    # If the maximum coefficient of correlation is lower than the correlation criterion, the node ij assumes the
                    # value nan, indicating the loss of correlation:
                    if maxVal < Criterion:

                        ui = float('nan')
                        vi = float('nan')

                    else:

                        xc = np.linspace(maxc[0] - 2, maxc[0] + 2, 5)
                        yc = np.linspace(maxc[1] - 2, maxc[1] + 2, 5)

                        cc = c[maxc[1] - 2:maxc[1] + 3, maxc[0] - 2:maxc[0] + 3]

                        xcint = xc;
                        ycint = yc;

                        f = interp2d(xc, yc, cc, kind='cubic')

                        del cc

                        ccinterp = f(xcint, ycint)

                        maxc_interp = np.unravel_index(ccinterp.argmax(), ccinterp.shape)

                        xpeak = xcint[maxc_interp[0]];
                        ypeak = ycint[maxc_interp[1]]

                        # Displacement calculation:
                        ui = xpeak - xpeak_ac
                        vi = ypeak - ypeak_ac

                except:
                    ui = float('nan')
                    vi = float('nan')

                if Type == 'Lagrangian':

                    x1[Image1][i][j] = x1[Image0][i][j] + ui
                    y1[Image1][i][j] = y1[Image0][i][j] + vi
                    u1[Image1][i][j] = ui;
                    v1[Image1][i][j] = vi;

                else:

                    x1[Image1][i][j] = x1[Image0][i][j]
                    y1[Image1][i][j] = y1[Image0][i][j]
                    u1[Image1][i][j] = ui;
                    v1[Image1][i][j] = vi;

########################################################################################################################
# 2D Digital Image Correlation function V2 - Stereo Correlation
########################################################################################################################
def Corr2D_Stereo_V2(Image, SubIr, SubIb, OpiSub, x0_mem, x0_shape, y0_mem, y0_shape, x1_mem, x1_shape, y1_mem, y1_shape,
    Iun, Id, Method, Criterion,i0,i1,j0,j1):
    global process_x0_mem, process_x0_shape, process_y0_mem, process_y0_shape
    global process_x1_mem, process_x1_shape, process_y1_mem, process_y1_shape

    process_x0_mem = x0_mem
    process_x0_shape = x0_shape
    process_y0_mem = y0_mem
    process_y0_shape = y0_shape
    process_x1_mem = x1_mem
    process_x1_shape = x1_shape
    process_y1_mem = y1_mem
    process_y1_shape = y1_shape

    x0 = np.frombuffer(process_x0_mem, dtype=np.float64).reshape(process_x0_shape)
    y0 = np.frombuffer(process_y0_mem, dtype=np.float64).reshape(process_y0_shape)
    x1 = np.frombuffer(process_x1_mem, dtype=np.float64).reshape(process_x1_shape)
    y1 = np.frombuffer(process_y1_mem, dtype=np.float64).reshape(process_y1_shape)

    for i in range(i0, i1):
        for j in range(j0, j1):
            # Test nan values:
            if np.isnan(x0[Image][i][j]):
                # If it exists, node ij assumes value nan:
                x1[Image][i][j] = float('nan');
                y1[Image][i][j] = float('nan');
            else:
                # Estimate the first node position for the reference and search images:
                xrmin = int(x0[Image][i][j] - (SubIr) / 2)
                yrmin = int(y0[Image][i][j] - (SubIr) / 2)
                xbmin = int(x0[Image][i][j] - (SubIb) / 2)
                if xbmin < 0:
                    xbmin = 0
                    SubIb_x = x0[Image][i][j] * 2
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb_x - SubIr) / 2
                    testexp = True
                else:
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb - SubIr) / 2
                    testexp = False

                ybmin = int(y0[Image][i][j] - (SubIb) / 2)
                if ybmin < 0:
                    ybmin = 0
                    SubIb_y = y0[Image][i][j] * 2

                    ypeak_ac = (SubIb_y - SubIr) / 2
                    testeyp = True
                else:
                    ypeak_ac = (SubIb - SubIr) / 2
                    testeyp = False

                # Crop reference and search images according to SubIr and SubIb values:
                Ir = Iun[yrmin:yrmin + SubIr, xrmin:xrmin + SubIr]
                Ib = Id[ybmin:ybmin + SubIb, xbmin:xbmin + SubIb]

                try:
                    # Correlation:
                    c = cv.matchTemplate(Ib, Ir, Method)

                    # Arrange the correlation matrix into vector shape:
                    pp = np.arange(0, c.shape[0])

                    # Search for the maximum coefficient of correlation and its position:
                    _, maxVal, _, maxc = cv.minMaxLoc(c)

                    # If the maximum coefficient of correlation is lower than the correlation criterion, the node ij assumes the
                    # value nan, indicating the loss of correlation:
                    if maxVal < Criterion:

                        ui = float('nan')
                        vi = float('nan')

                    else:

                        # Position of the correlation peak:
                        [ypeak_cc, xpeak_cc] = np.unravel_index(c.argmax(), c.shape)
                        ypeak_c = pp[ypeak_cc]
                        xpeak_c = pp[xpeak_cc]

                        h = 2;
                        # Correlation matrix crop:
                        pc = c[ypeak_c - h:ypeak_c + h + 1, xpeak_c - h: xpeak_c + h + 1]

                        # Matrix 5x5 containing the maximum value:
                        xc = np.linspace(xpeak_c - h, xpeak_c + h, 5)
                        yc = np.linspace(ypeak_c - h, ypeak_c + h, 5)

                        # Matrix containing the maximum value (interpolation):
                        if (5 * OpiSub % 2) == 0:
                            factor = 5 * OpiSub + 1
                        else:
                            factor = 5 * OpiSub

                        xci = np.linspace(xpeak_c - h, xpeak_c + h, factor)
                        yci = np.linspace(ypeak_c - h, ypeak_c + h, factor)

                        # Performs the interpolation over a 2D domain using bicubic spline:
                        f = interp2d(yc, xc, pc, kind='cubic')

                        del c, pc

                        ccinterp = f(yci, xci)

                        # Search for the maximum interpolated coefficient of correlation and its position:
                        _, maxVal_interp, _, maxc_interp = cv.minMaxLoc(ccinterp)

                        # Interpolated position of the correlation peak:
                        xpeak = xci[maxc_interp[0]];
                        ypeak = yci[maxc_interp[1]]

                        # Displacement calculation:
                        ui = xpeak - xpeak_ac
                        vi = ypeak - ypeak_ac

                except:
                    ui = float('nan')
                    vi = float('nan')

                x1[Image][i][j] = x0[Image][i][j] + ui
                y1[Image][i][j] = y0[Image][i][j] + vi

########################################################################################################################
# 2D Digital Image Correlation function V2 - Temporal Correlation L
########################################################################################################################
def Corr2D_Temporal_L_V2(Image0, Image1, SubIr, SubIb, OpiSub, xL_mem, xL_shape, yL_mem, yL_shape, uL_mem, uL_shape,
    vL_mem, vL_shape, Iun, Id, Type, Method, Criterion,i0,i1,j0,j1):
    global process_x0_mem, process_x0_shape, process_y0_mem, process_y0_shape
    global process_u0_mem, process_u0_shape, process_v0_mem, process_v0_shape

    process_x0_mem = xL_mem
    process_x0_shape = xL_shape
    process_y0_mem = yL_mem
    process_y0_shape = yL_shape
    process_u0_mem = uL_mem
    process_u0_shape = uL_shape
    process_v0_mem = vL_mem
    process_v0_shape = vL_shape

    x0 = np.frombuffer(process_x0_mem, dtype=np.float64).reshape(process_x0_shape)
    y0 = np.frombuffer(process_y0_mem, dtype=np.float64).reshape(process_y0_shape)
    u0 = np.frombuffer(process_u0_mem, dtype=np.float64).reshape(process_u0_shape)
    v0 = np.frombuffer(process_v0_mem, dtype=np.float64).reshape(process_v0_shape)

    for i in range(i0, i1):
        for j in range(j0, j1):
            # Test nan values:
            if np.isnan(x0[Image0][i][j]):
                # If it exists, node ij assumes value nan:
                x0[Image1][i][j] = float('nan');
                y0[Image1][i][j] = float('nan');
                u0[Image1][i][j] = float('nan');
                v0[Image1][i][j] = float('nan')
            else:
                # Estimate the first node position for the reference and search images:
                xrmin = int(x0[Image0][i][j] - (SubIr) / 2)
                yrmin = int(y0[Image0][i][j] - (SubIr) / 2)
                xbmin = int(x0[Image0][i][j] - (SubIb) / 2)
                if xbmin < 0:
                    xbmin = 0
                    SubIb_x = x0[Image0][i][j] * 2
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb_x - SubIr) / 2
                    testexp = True
                else:
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb - SubIr) / 2
                    testexp = False

                ybmin = int(y0[Image0][i][j] - (SubIb) / 2)
                if ybmin < 0:
                    ybmin = 0
                    SubIb_y = y0[Image0][i][j] * 2

                    ypeak_ac = (SubIb_y - SubIr) / 2
                    testeyp = True
                else:
                    ypeak_ac = (SubIb - SubIr) / 2
                    testeyp = False

                # Crop reference and search images according to SubIr and SubIb values:
                Ir = Iun[yrmin:yrmin + SubIr, xrmin:xrmin + SubIr]
                Ib = Id[ybmin:ybmin + SubIb, xbmin:xbmin + SubIb]

                try:
                    # Correlation:
                    c = cv.matchTemplate(Ib, Ir, Method)

                    # Arrange the correlation matrix into vector shape:
                    pp = np.arange(0, c.shape[0])

                    # Search for the maximum coefficient of correlation and its position:
                    _, maxVal, _, maxc = cv.minMaxLoc(c)

                    # If the maximum coefficient of correlation is lower than the correlation criterion, the node ij assumes the
                    # value nan, indicating the loss of correlation:
                    if maxVal < Criterion:

                        ui = float('nan')
                        vi = float('nan')

                    else:

                        # Position of the correlation peak:
                        [ypeak_cc, xpeak_cc] = np.unravel_index(c.argmax(), c.shape)
                        ypeak_c = pp[ypeak_cc]
                        xpeak_c = pp[xpeak_cc]

                        h = 2;
                        # Correlation matrix crop:
                        pc = c[ypeak_c - h:ypeak_c + h + 1, xpeak_c - h: xpeak_c + h + 1]

                        # Matrix 5x5 containing the maximum value:
                        xc = np.linspace(xpeak_c - h, xpeak_c + h, 5)
                        yc = np.linspace(ypeak_c - h, ypeak_c + h, 5)

                        # Matrix containing the maximum value (interpolation):
                        if (5 * OpiSub % 2) == 0:
                            factor = 5 * OpiSub + 1
                        else:
                            factor = 5 * OpiSub

                        xci = np.linspace(xpeak_c - h, xpeak_c + h, factor)
                        yci = np.linspace(ypeak_c - h, ypeak_c + h, factor)

                        # Performs the interpolation over a 2D domain using bicubic spline:
                        f = interp2d(yc, xc, pc, kind='cubic')

                        del c, pc

                        ccinterp = f(yci, xci)

                        # Search for the maximum interpolated coefficient of correlation and its position:
                        _, maxVal_interp, _, maxc_interp = cv.minMaxLoc(ccinterp)

                        # Interpolated position of the correlation peak:
                        xpeak = xci[maxc_interp[0]];
                        ypeak = yci[maxc_interp[1]]

                        # Displacement calculation:
                        ui = xpeak - xpeak_ac
                        vi = ypeak - ypeak_ac

                except:
                    ui = float('nan')
                    vi = float('nan')

                if Type == 'Lagrangian':

                    x0[Image1][i][j] = x0[Image0][i][j] + ui
                    y0[Image1][i][j] = y0[Image0][i][j] + vi
                    u0[Image1][i][j] = ui;
                    v0[Image1][i][j] = vi;

                else:

                    x0[Image1][i][j] = x0[Image0][i][j]
                    y0[Image1][i][j] = y0[Image0][i][j]
                    u0[Image1][i][j] = ui;
                    v0[Image1][i][j] = vi;

########################################################################################################################
# 2D Digital Image Correlation function V2 - Temporal Correlation L
########################################################################################################################
def Corr2D_Temporal_R_V2(Image0, Image1, SubIr, SubIb, OpiSub, xR_mem, xR_shape, yR_mem, yR_shape, uR_mem, uR_shape,
    vR_mem, vR_shape, Iun, Id, Type, Method, Criterion,i0,i1,j0,j1):
    global process_x1_mem, process_x1_shape, process_y1_mem, process_y1_shape
    global process_u1_mem, process_u1_shape, process_v1_mem, process_v1_shape

    process_x1_mem = xR_mem
    process_x1_shape = xR_shape
    process_y1_mem = yR_mem
    process_y1_shape = yR_shape
    process_u1_mem = uR_mem
    process_u1_shape = uR_shape
    process_v1_mem = vR_mem
    process_v1_shape = vR_shape

    x1 = np.frombuffer(process_x1_mem, dtype=np.float64).reshape(process_x1_shape)
    y1 = np.frombuffer(process_y1_mem, dtype=np.float64).reshape(process_y1_shape)
    u1 = np.frombuffer(process_u1_mem, dtype=np.float64).reshape(process_u1_shape)
    v1 = np.frombuffer(process_v1_mem, dtype=np.float64).reshape(process_v1_shape)

    for i in range(i0, i1):
        for j in range(j0, j1):
            # Test nan values:
            if np.isnan(x1[Image0][i][j]):
                # If it exists, node ij assumes value nan:
                x1[Image1][i][j] = float('nan');
                y1[Image1][i][j] = float('nan');
                u1[Image1][i][j] = float('nan');
                v1[Image1][i][j] = float('nan')
            else:
                # Estimate the first node position for the reference and search images:
                xrmin = int(x1[Image0][i][j] - (SubIr) / 2)
                yrmin = int(y1[Image0][i][j] - (SubIr) / 2)
                xbmin = int(x1[Image0][i][j] - (SubIb) / 2)
                if xbmin < 0:
                    xbmin = 0
                    SubIb_x = x1[Image0][i][j] * 2
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb_x - SubIr) / 2
                    testexp = True
                else:
                    # Position of the correlation matrix centroid:
                    xpeak_ac = (SubIb - SubIr) / 2
                    testexp = False

                ybmin = int(y1[Image0][i][j] - (SubIb) / 2)
                if ybmin < 0:
                    ybmin = 0
                    SubIb_y = y1[Image0][i][j] * 2

                    ypeak_ac = (SubIb_y - SubIr) / 2
                    testeyp = True
                else:
                    ypeak_ac = (SubIb - SubIr) / 2
                    testeyp = False

                # Crop reference and search images according to SubIr and SubIb values:
                Ir = Iun[yrmin:yrmin + SubIr, xrmin:xrmin + SubIr]
                Ib = Id[ybmin:ybmin + SubIb, xbmin:xbmin + SubIb]

                try:
                    # Correlation:
                    c = cv.matchTemplate(Ib, Ir, Method)

                    # Arrange the correlation matrix into vector shape:
                    pp = np.arange(0, c.shape[0])

                    # Search for the maximum coefficient of correlation and its position:
                    _, maxVal, _, maxc = cv.minMaxLoc(c)

                    # If the maximum coefficient of correlation is lower than the correlation criterion, the node ij assumes the
                    # value nan, indicating the loss of correlation:
                    if maxVal < Criterion:

                        ui = float('nan')
                        vi = float('nan')

                    else:

                        # Position of the correlation peak:
                        [ypeak_cc, xpeak_cc] = np.unravel_index(c.argmax(), c.shape)
                        ypeak_c = pp[ypeak_cc]
                        xpeak_c = pp[xpeak_cc]

                        h = 2;
                        # Correlation matrix crop:
                        pc = c[ypeak_c - h:ypeak_c + h + 1, xpeak_c - h: xpeak_c + h + 1]

                        # Matrix 5x5 containing the maximum value:
                        xc = np.linspace(xpeak_c - h, xpeak_c + h, 5)
                        yc = np.linspace(ypeak_c - h, ypeak_c + h, 5)

                        # Matrix containing the maximum value (interpolation):
                        if (5 * OpiSub % 2) == 0:
                            factor = 5 * OpiSub + 1
                        else:
                            factor = 5 * OpiSub

                        xci = np.linspace(xpeak_c - h, xpeak_c + h, factor)
                        yci = np.linspace(ypeak_c - h, ypeak_c + h, factor)

                        # Performs the interpolation over a 2D domain using bicubic spline:
                        f = interp2d(yc, xc, pc, kind='cubic')

                        del c, pc

                        ccinterp = f(yci, xci)

                        # Search for the maximum interpolated coefficient of correlation and its position:
                        _, maxVal_interp, _, maxc_interp = cv.minMaxLoc(ccinterp)

                        # Interpolated position of the correlation peak:
                        xpeak = xci[maxc_interp[0]];
                        ypeak = yci[maxc_interp[1]]

                        # Displacement calculation:
                        ui = xpeak - xpeak_ac
                        vi = ypeak - ypeak_ac

                except:
                    ui = float('nan')
                    vi = float('nan')

                if Type == 'Lagrangian':

                    x1[Image1][i][j] = x1[Image0][i][j] + ui
                    y1[Image1][i][j] = y1[Image0][i][j] + vi
                    u1[Image1][i][j] = ui;
                    v1[Image1][i][j] = vi;

                else:

                    x1[Image1][i][j] = x1[Image0][i][j]
                    y1[Image1][i][j] = y1[Image0][i][j]
                    u1[Image1][i][j] = ui;
                    v1[Image1][i][j] = vi;

########################################################################################################################
# Function to load the ROI and subset points construction
########################################################################################################################
def SelectionLoad(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx,
    Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, progression, progression_bar, canvas_left, canvas_right, canvas_text,
    Method, Correlation, Criterion, Step, file_var_ROI, file_ROI, Interpolation, Filtering, Kernel,ResultsName):

    global xriL, yriL, uriL, vriL, xriL_mem, yriL_mem, uriL_mem, vriL_mem, fileNamesSelectionLeft
    global fileNamesSelectionRight, selectionPathLeft, selectionPathRight, resultsPath, fileNamesLeft
    global fileNamesRight, Format, Images, calib

    if Interpolation.get() == 'After':
        Opi.set(1)
        console.insert(tk.END,
                       f'The interpolation factor was changed to 1 according to the interpolation strategy (after correlation)!\n\n')
        console.see('insert')

    file_load_mesh = filedialog.askopenfilename()

    file_ROI.set(file_load_mesh)

    l = open(file_load_mesh, "r")
    w = 2
    lines = l.readlines()
    selectionPath = lines[w].rstrip("\n"); w = w + 2

    save(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
            Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
            Filtering, Kernel)

    selectionPath = capturedFolder.get().rsplit('/', 1)[0] + '/Image_Selection'
    selectionPathLeft = selectionPath + '/Left'
    selectionPathRight = selectionPath + '/Right'

    if not os.path.exists(selectionPath):
        os.makedirs(selectionPath)
        os.makedirs(selectionPathLeft)
        os.makedirs(selectionPathRight)
        console.insert(tk.END, f'The Image_Selection folder was created\n\n')
        console.see('insert')
    else:
        console.insert(tk.END, 'The Image_Selection folder is already in the main directory\n\n')
        console.see('insert')

    for file in os.listdir(selectionPathLeft):
        if file.endswith(Format):
            os.remove(os.path.join(selectionPathLeft, file))

    for file in os.listdir(selectionPathRight):
        if file.endswith(Format):
            os.remove(os.path.join(selectionPathRight, file))

    resultsPath = capturedFolder.get().rsplit('/', 1)[0] + f'/{ResultsName.get()}'
    if not os.path.exists(resultsPath):
        os.makedirs(resultsPath)
        console.insert(tk.END, f'The {ResultsName.get()} folder was created\n\n')
        console.see('insert')
    else:
        console.insert(tk.END, f'The {ResultsName.get()} folder is already in the main directory\n\n')
        console.see('insert')

    for files in os.listdir(resultsPath):
        if files.endswith(".dat"):
            os.remove(os.path.join(resultsPath, files))

    if Adjust.get() == 0.0:
        adjust = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8))
    else:
        adjust = cv.createCLAHE(clipLimit=Adjust.get(), tileGridSize=(8, 8))

    xinitline = int(lines[w]); w = w + 1
    yinitline = int(lines[w]); w = w + 1
    dxline = int(lines[w]); w = w + 1
    dyline = int(lines[w]); w = w + 2

    for k in range(1, Images + 1):
        green_length = int(933 * ((k) / Images))
        progression.coords(progression_bar, 0, 0, green_length, 25);
        progression.itemconfig(canvas_text, text=f'{k} of {Images} - {100 * (k) / Images:.2f}%')

        cv.imwrite(selectionPathLeft + f'\\Image{k}' + Format, adjust.apply(cv.undistort(cv.imread(fileNamesLeft[k-1],0), calib[1], calib[2])[int(yinitline):int(yinitline + dyline),
            int(xinitline):int(xinitline + dxline)]))
        cv.imwrite(selectionPathRight + f'\\Image{k}' + Format, adjust.apply(cv.undistort(cv.imread(fileNamesRight[k-1],0), calib[3], calib[4])[int(yinitline):int(yinitline + dyline),
            int(xinitline):int(xinitline + dxline)]))

    fileNamesSelectionLeft = sorted(glob.glob(selectionPathLeft + '/*'), key=stringToList)
    fileNamesSelectionRight = sorted(glob.glob(selectionPathRight + '/*'), key=stringToList)

    console.insert(tk.END, f'{Images} images were cropped and adjusted\n\n')
    console.see('insert')

    xinitline = int(lines[w]); w = w + 1
    yinitline = int(lines[w]); w = w + 1
    dxline = int(lines[w]); w = w + 1
    dyline = int(lines[w]); w = w + 2

    console.insert(tk.END, f'ROI construction was successfully loaded in {file_ROI.get()}\n\n')
    console.see('insert')

    if Nx.get() == 0 and Ny.get() == 0:
        Nx.set(int(abs(dxline) / Step.get()))
        Ny.set(int(abs(dyline) / Step.get()))

    xriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    xriL = np.frombuffer(xriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
    yriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    yriL = np.frombuffer(yriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
    uriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    uriL = np.frombuffer(uriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
    vriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    vriL = np.frombuffer(vriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)

    for i in range(0, Ny.get() + 1):
        for j in range(0, Nx.get() + 1):
            xriL[0, i, j] = xinitline * Opi.get() + ((j) * dxline * Opi.get()) / (Nx.get())
            yriL[0, i, j] = yinitline * Opi.get() + ((i) * dyline * Opi.get()) / (Ny.get())

    if NumCut.get() != 0:
        if 'Rectangular' in TypeCut.get():
            for i in range(0, NumCut.get()):
                console.insert(tk.END, f'Select the rectangular cut region # {str(i + 1)} and press enter key\n\n')
                console.see('insert')
                image = cv.imread(fileNamesSelectionLeft[0])
                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][int((Nx.get() + 1) / 2)]) or np.isnan(
                                xriL[0][i + 1][int((Nx.get() + 1) / 2)]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get()),
                                                    int(yriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get())), (
                                            int(xriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get()),
                                            int(yriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get())), (255, 0, 0), 3)
                        if np.isnan(xriL[0][int((Ny.get() + 1) / 2)][j]) or np.isnan(
                                xriL[0][int((Ny.get() + 1) / 2)][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get()),
                                                    int(yriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get())), (
                                            int(xriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get()),
                                            int(yriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get())), (255, 0, 0), 3)

                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i][j + 1] / Opi.get()), int(yriL[0][i][j + 1] / Opi.get())),
                                            (0, 0, 255), 2)

                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get() + 1):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i + 1][j]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i + 1][j] / Opi.get()), int(yriL[0][i + 1][j] / Opi.get())),
                                            (0, 0, 255), 2)

                dxfigure = int(image.shape[1])
                dyfigure = int(image.shape[0])

                screen_width = menu.winfo_screenwidth() - 100
                screen_height = menu.winfo_screenheight() - 100

                # Change size of displayed image:
                if dyfigure > screen_height:
                    ratio = screen_height / dyfigure
                    image_figure = cv.resize(image,
                                             (int(screen_height * dxfigure / dyfigure), screen_height))
                    # image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                    xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                         'Select the rectangular cut region',
                                                                         image_figure)

                    xinitline = xinitline / ratio
                    yinitline = yinitline / ratio
                    dxline = dxline / ratio
                    dyline = dyline / ratio
                else:
                    xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                         'Select the rectangular cut region', image)

                cv.destroyAllWindows()

                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get() + 1):

                        if xinitline <= xriL[0][i][j] / Opi.get() <= xinitline + dxline and yinitline <= yriL[0][i][
                            j] / Opi.get() <= yinitline + dyline:
                            xriL[0][i][j] = float('nan')
                            yriL[0][i][j] = float('nan')

        if 'Circular inside' in TypeCut.get():
            for i in range(0, NumCut.get()):
                console.insert(tk.END, f'Select the circular cutting region # {str(i + 1)} and press enter key\n\n')
                console.see('insert')

                image = cv.imread(fileNamesSelectionLeft[0])
                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][int((Nx.get() + 1) / 2)]) or np.isnan(
                                xriL[0][i + 1][int((Nx.get() + 1) / 2)]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get()),
                                                    int(yriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get())), (
                                            int(xriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get()),
                                            int(yriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get())), (255, 0, 0), 3)
                        if np.isnan(xriL[0][int((Ny.get() + 1) / 2)][j]) or np.isnan(
                                xriL[0][int((Ny.get() + 1) / 2)][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get()),
                                                    int(yriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get())), (
                                            int(xriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get()),
                                            int(yriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get())), (255, 0, 0), 3)

                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i][j + 1] / Opi.get()), int(yriL[0][i][j + 1] / Opi.get())),
                                            (0, 0, 255), 2)

                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get() + 1):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i + 1][j]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i + 1][j] / Opi.get()), int(yriL[0][i + 1][j] / Opi.get())),
                                            (0, 0, 255), 2)

                dxfigure = int(image.shape[1])
                dyfigure = int(image.shape[0])

                screen_width = menu.winfo_screenwidth() - 100
                screen_height = menu.winfo_screenheight() - 100

                # Change size of displayed image:
                if dyfigure > screen_height:
                    ratio = screen_height / dyfigure
                    image_figure = cv.resize(image,
                                             (int(screen_height * dxfigure / dyfigure), screen_height))
                    # image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                    pointsCut = CircularROI_DIC(menu, console, 'Select the circular cut region', image_figure)

                    for w in range(0, len(pointsCut)):
                        pointsCut[w] = [x / ratio for x in pointsCut[w]]

                else:
                    pointsCut = CircularROI_DIC(menu, console, 'Select the circular cut region', image)

                cv.destroyAllWindows()

                polygon = Polygon(pointsCut)
                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get() + 1):
                        point = Point(xriL[0][i][j] / Opi.get(), yriL[0][i][j] / Opi.get())
                        if polygon.contains(point):
                            xriL[0][i][j] = float('nan')
                            yriL[0][i][j] = float('nan')
                            uriL[0][i][j] = float('nan')
                            vriL[0][i][j] = float('nan')

        if 'Circular outside' in TypeCut.get():
            for i in range(0, NumCut.get()):
                console.insert(tk.END, f'Select the circular cutting region # {str(i + 1)} and press enter key\n\n')
                console.see('insert')

                image = cv.imread(fileNamesSelectionLeft[0])
                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][int((Nx.get() + 1) / 2)]) or np.isnan(
                                xriL[0][i + 1][int((Nx.get() + 1) / 2)]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get()),
                                                    int(yriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get())), (
                                            int(xriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get()),
                                            int(yriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get())), (255, 0, 0), 3)
                        if np.isnan(xriL[0][int((Ny.get() + 1) / 2)][j]) or np.isnan(
                                xriL[0][int((Ny.get() + 1) / 2)][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get()),
                                                    int(yriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get())), (
                                            int(xriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get()),
                                            int(yriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get())), (255, 0, 0), 3)

                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i][j + 1] / Opi.get()), int(yriL[0][i][j + 1] / Opi.get())),
                                            (0, 0, 255), 2)

                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get() + 1):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i + 1][j]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i + 1][j] / Opi.get()), int(yriL[0][i + 1][j] / Opi.get())),
                                            (0, 0, 255), 2)

                dxfigure = int(image.shape[1])
                dyfigure = int(image.shape[0])

                screen_width = menu.winfo_screenwidth() - 100
                screen_height = menu.winfo_screenheight() - 100

                # Change size of displayed image:
                if dyfigure > screen_height:
                    ratio = screen_height / dyfigure
                    image_figure = cv.resize(image,
                                             (int(screen_height * dxfigure / dyfigure), screen_height))
                    # image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                    pointsCut = CircularROI_DIC(menu, console, 'Select the circular cut region', image_figure)

                    for w in range(0, len(pointsCut)):
                        pointsCut[w] = [x / ratio for x in pointsCut[w]]

                else:
                    pointsCut = CircularROI_DIC(menu, console, 'Select the circular cut region', image)

                cv.destroyAllWindows()

                polygon = Polygon(pointsCut)
                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get() + 1):
                        point = Point(xriL[0][i][j] / Opi.get(), yriL[0][i][j] / Opi.get())
                        if polygon.contains(point):
                            pass
                        else:
                            xriL[0][i][j] = float('nan')
                            yriL[0][i][j] = float('nan')
                            uriL[0][i][j] = float('nan')
                            vriL[0][i][j] = float('nan')

        if 'Free' in TypeCut.get():
            for i in range(0, NumCut.get()):
                console.insert(tk.END, f'Select the freehand cutting region # {str(i + 1)} and press enter key\n\n')
                console.see('insert')

                image = cv.imread(fileNamesSelectionLeft[0])
                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][int((Nx.get() + 1) / 2)]) or np.isnan(
                                xriL[0][i + 1][int((Nx.get() + 1) / 2)]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get()),
                                                    int(yriL[0][i][int((Nx.get() + 1) / 2)] / Opi.get())), (
                                            int(xriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get()),
                                            int(yriL[0][i + 1][int((Nx.get() + 1) / 2)] / Opi.get())), (255, 0, 0), 3)
                        if np.isnan(xriL[0][int((Ny.get() + 1) / 2)][j]) or np.isnan(
                                xriL[0][int((Ny.get() + 1) / 2)][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get()),
                                                    int(yriL[0][int((Ny.get() + 1) / 2)][j] / Opi.get())), (
                                            int(xriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get()),
                                            int(yriL[0][int((Ny.get() + 1) / 2)][j + 1] / Opi.get())), (255, 0, 0), 3)

                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get()):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j + 1]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i][j + 1] / Opi.get()), int(yriL[0][i][j + 1] / Opi.get())),
                                            (0, 0, 255), 2)

                for i in range(0, Ny.get()):
                    for j in range(0, Nx.get() + 1):
                        if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i + 1][j]):
                            pass
                        else:
                            image = cv.line(image, (int(xriL[0][i][j] / Opi.get()), int(yriL[0][i][j] / Opi.get())),
                                            (int(xriL[0][i + 1][j] / Opi.get()), int(yriL[0][i + 1][j] / Opi.get())),
                                            (0, 0, 255), 2)

                dxfigure = int(image.shape[1])
                dyfigure = int(image.shape[0])

                screen_width = menu.winfo_screenwidth() - 100
                screen_height = menu.winfo_screenheight() - 100

                # Change size of displayed image:
                if dyfigure > screen_height:
                    ratio = screen_height / dyfigure
                    image_figure = cv.resize(image,
                                             (int(screen_height * dxfigure / dyfigure), screen_height))
                    # image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                    pointsCut = freehandCut('Select the freehand cutting region', image_figure)

                    for w in range(0, len(pointsCut)):
                        pointsCut[w] = [x / ratio for x in pointsCut[w]]

                else:
                    pointsCut = freehandCut('Select the freehand cutting region', image)

                cv.destroyAllWindows()

                polygon = Polygon(pointsCut)
                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get() + 1):
                        point = Point(xriL[0][i][j] / Opi.get(), yriL[0][i][j] / Opi.get())
                        if polygon.contains(point):
                            xriL[0][i][j] = float('nan')
                            yriL[0][i][j] = float('nan')
                            uriL[0][i][j] = float('nan')
                            vriL[0][i][j] = float('nan')

    # Left mesh update figure:
    figL = plt.figure()
    ax = figL.gca()
    dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
    dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

    ratio_plot = dxplot / dyplot;

    if ratio_plot <= 1.33333333:

        dxplotdark = dyplot * 1.33333333
        dyplotdark = dyplot
        ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
        ax.plot(np.transpose(xriL[0][:][:] / Opi.get()), np.transpose(yriL[0][:][:] / Opi.get()), color='red',
                linewidth=1, zorder=3)
        ax.plot(xriL[0][:][:] / Opi.get(), yriL[0][:][:] / Opi.get(), color='red', linewidth=1, zorder=3)
        winSub = False
        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                if ~np.isnan(xriL[0][i][j]):

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIrS.get() / 2, xriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIrS.get() / 2, xriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIrS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIrS.get() / 2, yriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIrS.get() / 2, yriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIrS.get() / 2],
                        color='#00FF00', linewidth=1, zorder=3)  # SubIr window

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIbS.get() / 2, xriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIbS.get() / 2, xriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIbS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIbS.get() / 2, yriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIbS.get() / 2, yriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIbS.get() / 2],
                        color='blue', linewidth=1, zorder=3)  # SubIb window

                    winSub = True
                    break
                else:
                    continue

            if winSub: break
        ax.plot(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
        ax.fill_between(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
        plt.ylim(0, dyplotdark)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    else:
        dxplotdark = dxplot
        dyplotdark = dxplot / 1.33333333
        ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
        ax.plot(np.transpose(xriL[0][:][:] / Opi.get()), np.transpose(yriL[0][:][:] / Opi.get()), color='red',
                linewidth=1, zorder=3)
        ax.plot(xriL[0][:][:] / Opi.get(), yriL[0][:][:] / Opi.get(), color='red', linewidth=1, zorder=3)
        winSub = False
        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                if ~np.isnan(xriL[0][i][j]):

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIrS.get() / 2, xriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIrS.get() / 2, xriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIrS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIrS.get() / 2, yriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIrS.get() / 2, yriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIrS.get() / 2],
                        color='#00FF00', linewidth=1, zorder=3)  # SubIr window

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIbS.get() / 2, xriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIbS.get() / 2, xriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIbS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIbS.get() / 2, yriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIbS.get() / 2, yriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIbS.get() / 2],
                        color='blue', linewidth=1, zorder=3)  # SubIb window

                    winSub = True
                    break
                else:
                    continue

            if winSub: break
        ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                 +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                 0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
        ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                        [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                         +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                         0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(0, dxplotdark)
        plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    figL.canvas.draw()

    imageL = np.frombuffer(figL.canvas.tostring_rgb(), dtype=np.uint8)
    wL, hL = figL.canvas.get_width_height()
    imageL = np.flip(imageL.reshape((hL, wL, 3)), axis=0)

    plt.cla()
    plt.clf()

    # Right mesh update figure:
    figR = plt.figure()
    ax = figR.gca()
    dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
    dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

    if ratio_plot <= 1.33333333:

        dxplotdark = dyplot * 1.33333333
        dyplotdark = dyplot
        ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
        ax.plot(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
        ax.fill_between(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
        plt.ylim(0, dyplotdark)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    else:
        dxplotdark = dxplot
        dyplotdark = dxplot / 1.33333333
        ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
        ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                 +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                 0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
        ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                        [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                         +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                         0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(0, dxplotdark)
        plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    figR.canvas.draw()

    imageR = np.frombuffer(figR.canvas.tostring_rgb(), dtype=np.uint8)
    wR, hR = figR.canvas.get_width_height()
    imageR = np.flip(imageR.reshape((hR, wR, 3)), axis=0)

    plt.cla()
    plt.clf()

    image_left = cv.resize(imageL, (426, 320))
    cv.putText(image_left, f'MASTER L - {1}', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
    cv.putText(image_left, f'CORRELATION MESH - {np.count_nonzero(~np.isnan(xriL[0][:][:]))} nodes', (5, 40),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
    cv.putText(image_left, 'REFERENCE SUBSET', (5, 60), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
    cv.putText(image_left, 'SEARCH SUBSET', (5, 80), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
    image_left = ImageTk.PhotoImage(Image.fromarray(image_left))

    canvas_left.image_left = image_left
    canvas_left.configure(image=image_left)

    image_right = cv.resize(imageR, (426, 320))
    cv.putText(image_right, f'SLAVE R - {1}', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
    image_right = ImageTk.PhotoImage(Image.fromarray(image_right))

    canvas_right.image_right = image_right
    canvas_right.configure(image=image_right)

    console.insert(tk.END, 'Start the correlation process\n\n')
    console.see('insert')

    messagebox.showinfo('Information', 'Press start to initialize the stereo correlation!')

########################################################################################################################
# Save subset points
########################################################################################################################
def SaveSubsets(console):
    global xriL, yriL, uriL, vriL

    console.insert(tk.END,
                   '##################################################################################################################\n\n')
    console.insert(tk.END, 'Select the folder to save the position of subsets - .csv format\n\n')
    console.see('insert')

    mesh_folder = filedialog.askdirectory()

    np.savetxt(f'{mesh_folder}\\x_left.csv', xriL[:][:][0], delimiter='\t')
    np.savetxt(f'{mesh_folder}\\y_left.csv', yriL[:][:][0], delimiter='\t')
    np.savetxt(f'{mesh_folder}\\u_left.csv', uriL[:][:][0], delimiter='\t')
    np.savetxt(f'{mesh_folder}\\v_left.csv', vriL[:][:][0], delimiter='\t')

    messagebox.showinfo('Information', 'The position of subsets has been successfully saved!')

########################################################################################################################
# Load subset points
########################################################################################################################
def LoadSubsets(console, canvas_left, canvas_right, capturedFolder, Nx, Ny, Interpolation, Opi, ResultsName, SubIrS,
    SubIbS):
    global xriL, yriL, uriL, vriL, xriL_mem, yriL_mem, uriL_mem, vriL_mem, fileNamesSelectionLeft
    global fileNamesSelectionRight, selectionPathLeft, selectionPathRight, resultsPath, Format, Images

    console.insert(tk.END,
                   '##################################################################################################################\n\n')
    console.see('insert')

    if Interpolation.get() == 'After':
        Opi.set(1)
        console.insert(tk.END,f'The interpolation factor was changed to 1 according to the interpolation preference (after correlation)!\n\n')
        console.see('insert')

    selectionPath = capturedFolder.get().rsplit('/', 1)[0] + '/Image_Selection'
    selectionPathLeft = selectionPath + '/Left'
    selectionPathRight = selectionPath + '/Right'

    fileNamesSelectionLeft = sorted(glob.glob(selectionPathLeft + '/*'), key=stringToList)
    fileNamesSelectionRight = sorted(glob.glob(selectionPathRight + '/*'), key=stringToList)

    resultsPath = capturedFolder.get().rsplit('/', 1)[0] + f'/{ResultsName.get()}'
    if not os.path.exists(resultsPath):
        os.makedirs(resultsPath)
        console.insert(tk.END, f'The {ResultsName.get()} folder was created\n\n')
        console.see('insert')
    else:
        console.insert(tk.END, f'The {ResultsName.get()} folder is already in the main directory\n\n')
        console.see('insert')

    for files in os.listdir(resultsPath):
        if files.endswith(".dat"):
            os.remove(os.path.join(resultsPath, files))

    mesh_folder = filedialog.askdirectory()

    subset_test = genfromtxt(f'{mesh_folder}\\x_left.csv', delimiter='\t')

    ans = messagebox.askquestion('Subset construction', 'The file was generated by iCorrVision-3D software?',
                                 icon='question')
    if ans == 'no':
        Ny.set(subset_test.shape[0]-1)
        Nx.set(subset_test.shape[1]-2)

        xriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        xriL = np.frombuffer(xriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        yriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        yriL = np.frombuffer(yriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        uriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        uriL = np.frombuffer(uriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        vriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        vriL = np.frombuffer(vriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)

        xriL[:][:][0] = genfromtxt(f'{mesh_folder}\\x_left.csv', delimiter='\t')[0:Ny.get()+1,0:Nx.get() + 1]
        yriL[:][:][0] = genfromtxt(f'{mesh_folder}\\y_left.csv', delimiter='\t')[0:Ny.get()+1,0:Nx.get() + 1]
        uriL[:][:][0] = genfromtxt(f'{mesh_folder}\\u_left.csv', delimiter='\t')[0:Ny.get()+1,0:Nx.get() + 1]
        vriL[:][:][0] = genfromtxt(f'{mesh_folder}\\v_left.csv', delimiter='\t')[0:Ny.get()+1,0:Nx.get() + 1]

        xriL[:][:][0] = xriL[:][:][0] * Opi.get()
        yriL[:][:][0] = yriL[:][:][0] * Opi.get()
        uriL[:][:][0] = uriL[:][:][0] * Opi.get()
        vriL[:][:][0] = vriL[:][:][0] * Opi.get()

    else:
        Ny.set(subset_test.shape[0] - 1)
        Nx.set(subset_test.shape[1] - 1)

        xriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        xriL = np.frombuffer(xriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        yriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        yriL = np.frombuffer(yriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        uriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        uriL = np.frombuffer(uriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        vriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        vriL = np.frombuffer(vriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)

        xriL[:][:][0] = genfromtxt(f'{mesh_folder}\\x_left.csv', delimiter='\t')[0:Ny.get() + 1, 0:Nx.get() + 1]
        yriL[:][:][0] = genfromtxt(f'{mesh_folder}\\y_left.csv', delimiter='\t')[0:Ny.get() + 1, 0:Nx.get() + 1]
        uriL[:][:][0] = genfromtxt(f'{mesh_folder}\\u_left.csv', delimiter='\t')[0:Ny.get() + 1, 0:Nx.get() + 1]
        vriL[:][:][0] = genfromtxt(f'{mesh_folder}\\v_left.csv', delimiter='\t')[0:Ny.get() + 1, 0:Nx.get() + 1]

    # Left mesh update figure:
    figL = plt.figure()
    ax = figL.gca()
    dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
    dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

    ratio_plot = dxplot / dyplot;

    if ratio_plot <= 1.33333333:

        dxplotdark = dyplot * 1.33333333
        dyplotdark = dyplot
        ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
        ax.plot(np.transpose(xriL[0][:][:] / Opi.get()), np.transpose(yriL[0][:][:] / Opi.get()), color='red',
                linewidth=1, zorder=3)
        ax.plot(xriL[0][:][:] / Opi.get(), yriL[0][:][:] / Opi.get(), color='red', linewidth=1, zorder=3)
        winSub = False
        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                if ~np.isnan(xriL[0][i][j]):

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIrS.get() / 2, xriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIrS.get() / 2, xriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIrS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIrS.get() / 2, yriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIrS.get() / 2, yriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIrS.get() / 2],
                        color='#00FF00', linewidth=1, zorder=3)  # SubIr window

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIbS.get() / 2, xriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIbS.get() / 2, xriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIbS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIbS.get() / 2, yriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIbS.get() / 2, yriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIbS.get() / 2],
                        color='blue', linewidth=1, zorder=3)  # SubIb window

                    winSub = True
                    break
                else:
                    continue

            if winSub: break
        ax.plot(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
        ax.fill_between(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
        plt.ylim(0, dyplotdark)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    else:
        dxplotdark = dxplot
        dyplotdark = dxplot / 1.33333333
        ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
        ax.plot(np.transpose(xriL[0][:][:] / Opi.get()), np.transpose(yriL[0][:][:] / Opi.get()), color='red',
                linewidth=1, zorder=3)
        ax.plot(xriL[0][:][:] / Opi.get(), yriL[0][:][:] / Opi.get(), color='red', linewidth=1, zorder=3)
        winSub = False
        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                if ~np.isnan(xriL[0][i][j]):

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIrS.get() / 2, xriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIrS.get() / 2, xriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIrS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIrS.get() / 2, yriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIrS.get() / 2, yriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIrS.get() / 2],
                        color='#00FF00', linewidth=1, zorder=3)  # SubIr window

                    ax.plot(
                        [xriL[0][i][j] / Opi.get() - SubIbS.get() / 2, xriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() + SubIbS.get() / 2, xriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         xriL[0][i][j] / Opi.get() - SubIbS.get() / 2],
                        [yriL[0][i][j] / Opi.get() + SubIbS.get() / 2, yriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() - SubIbS.get() / 2, yriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                         yriL[0][i][j] / Opi.get() + SubIbS.get() / 2],
                        color='blue', linewidth=1, zorder=3)  # SubIb window

                    winSub = True
                    break
                else:
                    continue

            if winSub: break
        ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                 +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                 0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
        ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                        [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                         +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                         0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(0, dxplotdark)
        plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    figL.canvas.draw()

    imageL = np.frombuffer(figL.canvas.tostring_rgb(), dtype=np.uint8)
    wL, hL = figL.canvas.get_width_height()
    imageL = np.flip(imageL.reshape((hL, wL, 3)), axis=0)

    plt.cla()
    plt.clf()

    # Right mesh update figure:
    figR = plt.figure()
    ax = figR.gca()
    dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
    dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

    if ratio_plot <= 1.33333333:

        dxplotdark = dyplot * 1.33333333
        dyplotdark = dyplot
        ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
        ax.plot(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
        ax.fill_between(
            [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2,
             dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
            [0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
        plt.ylim(0, dyplotdark)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    else:
        dxplotdark = dxplot
        dyplotdark = dxplot / 1.33333333
        ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
        ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                 +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                 0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
        ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                        [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                         +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                         0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(0, dxplotdark)
        plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    figR.canvas.draw()

    imageR = np.frombuffer(figR.canvas.tostring_rgb(), dtype=np.uint8)
    wR, hR = figR.canvas.get_width_height()
    imageR = np.flip(imageR.reshape((hR, wR, 3)), axis=0)

    plt.cla()
    plt.clf()

    image_left = cv.resize(imageL, (426, 320))
    cv.putText(image_left, f'MASTER L - {1}', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
    cv.putText(image_left, f'CORRELATION MESH - {np.count_nonzero(~np.isnan(xriL[0][:][:]))} nodes', (5, 40),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
    cv.putText(image_left, 'REFERENCE SUBSET', (5, 60), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
    cv.putText(image_left, 'SEARCH SUBSET', (5, 80), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
    image_left = ImageTk.PhotoImage(Image.fromarray(image_left))

    canvas_left.image_left = image_left
    canvas_left.configure(image=image_left)

    image_right = cv.resize(imageR, (426, 320))
    cv.putText(image_right, f'SLAVE R - {1}', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
    image_right = ImageTk.PhotoImage(Image.fromarray(image_right))

    canvas_right.image_right = image_right
    canvas_right.configure(image=image_right)

    console.insert(tk.END, 'Start the correlation process\n\n')
    console.see('insert')

    messagebox.showinfo('Information', 'Press start to initialize the stereo correlation!')

########################################################################################################################
# Function to select the ROI and subset points construction
########################################################################################################################
def SelectionImage(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx,
    Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, progression, progression_bar, canvas_left, canvas_right,
    canvas_text, Method, Correlation, Criterion, Step, file_var_ROI, file_ROI, Interpolation, Filtering, Kernel,
    ResultsName):

    global xriL, yriL, uriL, vriL, xriL_mem, yriL_mem, uriL_mem, vriL_mem, fileNamesSelectionLeft
    global fileNamesSelectionRight, selectionPathLeft, selectionPathRight, resultsPath, fileNamesLeft, fileNamesRight
    global Format, Images, calib

    try:
        fileNamesLeft, fileNamesRight
    except NameError:
        messagebox.showerror('Error','Please load project or select the image captured folder, calibration file and DIC settings before starting the selection process!')
    else:

        if Interpolation.get() == 'After':
            Opi.set(1)
            console.insert(tk.END, f'The interpolation factor was changed to 1 according to the interpolation preference (after correlation)!\n\n')
            console.see('insert')

        save(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
             Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
             Filtering, Kernel)

        # Creation of the Image_Selection folder:
        selectionPath = capturedFolder.get().rsplit('/', 1)[0]+'/Image_Selection'
        selectionPathLeft = selectionPath+'/Left'
        selectionPathRight = selectionPath+'/Right'
        if not os.path.exists(selectionPath):
            os.makedirs(selectionPath)
            os.makedirs(selectionPathLeft)
            os.makedirs(selectionPathRight)
            console.insert(tk.END, f'The Image_Selection folder was created\n\n')
            console.see('insert')
        else:
            console.insert(tk.END, 'The Image_Selection folder is already in the main directory\n\n')
            console.see('insert')

        for file in os.listdir(selectionPathLeft):
            if file.endswith(Format):
                os.remove(os.path.join(selectionPathLeft, file))

        for file in os.listdir(selectionPathRight):
            if file.endswith(Format):
                os.remove(os.path.join(selectionPathRight, file))

        # Creation of the Results_Correlation folder:
        resultsPath = capturedFolder.get().rsplit('/', 1)[0] + f'/{ResultsName.get()}'
        if not os.path.exists(resultsPath):
            os.makedirs(resultsPath)
            console.insert(tk.END, f'The {ResultsName.get()} folder was created\n\n')
            console.see('insert')
        else:
            console.insert(tk.END, f'The {ResultsName.get()} folder is already in the main directory\n\n')
            console.see('insert')

        for file in os.listdir(resultsPath):
            if file.endswith(".dat"):
                os.remove(os.path.join(resultsPath, file))

        # Save ROI log:
        file_var_ROI.set(True)

        console.insert(tk.END, 'Select a .dat file to save the region of interest (ROI)\n\n')
        console.see('insert')

        file_ROI.set(filedialog.asksaveasfilename())

        f = open(file_ROI.get(), "w+")

        f.write('iCorrVision-3D Correlation Module - ROI - ' + str(
            datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")))
        f.write('\nImage selection folder:\n')
        f.write(str(selectionPath.rstrip("\n")))

        # ROI selection:
        console.insert(tk.END, 'Select the region of interest (ROI) and press enter key\n\n')
        console.see('insert')

        if Adjust.get() == 0.0:
            adjust = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8,8))
        else:
            adjust = cv.createCLAHE(clipLimit=Adjust.get(), tileGridSize=(8,8))

        UndistortedImage = cv.undistort(cv.imread(fileNamesLeft[0]), calib[1], calib[2])

        dxfigure = int(UndistortedImage.shape[1])
        dyfigure = int(UndistortedImage.shape[0])

        screen_width = menu.winfo_screenwidth()-100
        screen_height = menu.winfo_screenheight()-100

        # Change size of displayed image:
        if dyfigure > screen_height:
            ratio = screen_height/dyfigure
            image_figure = adjust.apply(cv.resize(cv.undistort(cv.imread(fileNamesLeft[0],0), calib[1], calib[2]), (int(screen_height*dxfigure/dyfigure), screen_height)))
            image_figure = cv.cvtColor(image_figure,cv.COLOR_GRAY2RGB)
            xinitline,yinitline,dxline,dyline = SelectROI_DIC(menu, console,'Select the region of interest (ROI)',image_figure)
            xinitline=xinitline/ratio
            yinitline=yinitline/ratio
            dxline=dxline/ratio
            dyline=dyline/ratio
        else:
            image_figure = adjust.apply(cv.undistort(cv.imread(fileNamesLeft[0],0), calib[1], calib[2]))
            image_figure = cv.cvtColor(image_figure,cv.COLOR_GRAY2RGB)
            xinitline,yinitline,dxline,dyline = SelectROI_DIC(menu, console,'Select the region of interest (ROI)',image_figure)

        cv.destroyAllWindows()

        f.write('\nROI:\n')
        f.write(str(int(xinitline)) + '\n')
        f.write(str(int(yinitline)) + '\n')
        f.write(str(int(dxline)) + '\n')
        f.write(str(int(dyline)))

        for k in range(1,Images+1):
            green_length = int(933*((k)/Images))
            progression.coords(progression_bar, 0, 0, green_length, 25); progression.itemconfig(canvas_text, text=f'{k} of {Images} - {100*(k)/Images:.2f}%')

            cv.imwrite(selectionPathLeft+f'\\Image{k}'+Format,  adjust.apply(cv.undistort(cv.imread(fileNamesLeft[k-1],0), calib[1], calib[2])[int(yinitline):int(yinitline+dyline), int(xinitline):int(xinitline+dxline)]))
            cv.imwrite(selectionPathRight+f'\\Image{k}'+Format,  adjust.apply(cv.undistort(cv.imread(fileNamesRight[k-1],0), calib[3], calib[4])[int(yinitline):int(yinitline+dyline), int(xinitline):int(xinitline+dxline)]))

        fileNamesSelectionLeft = sorted(glob.glob(selectionPathLeft+'/*'),key=stringToList)
        fileNamesSelectionRight = sorted(glob.glob(selectionPathRight+'/*'),key=stringToList)

        console.insert(tk.END, f'{Images} image pairs were cropped and adjusted\n\n')
        console.insert(tk.END, 'Select the region for the subset construction and press enter key\n\n')
        console.see('insert')

        dxfigure = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
        dyfigure = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

        screen_width = menu.winfo_screenwidth() - 100
        screen_height = menu.winfo_screenheight() - 100

        # Change size of displayed image:
        if dyfigure > screen_height:
            ratio = screen_height / dyfigure
            if Version.get() == 'Eulerian':
                image_figure = cv.resize(cv.imread(fileNamesSelectionLeft[-1], 0),
                                         (int(screen_height * dxfigure / dyfigure), screen_height))
                image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                     'Select the region for the subset construction on last captured image (Eulerian)',
                                                                     image_figure)
            else:
                image_figure = cv.resize(cv.imread(fileNamesSelectionLeft[0], 0),
                                         (int(screen_height * dxfigure / dyfigure), screen_height))
                image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                     'Select the region for the subset construction on first captured image (Lagrangian)',
                                                                     image_figure)
            xinitline = xinitline / ratio
            yinitline = yinitline / ratio
            dxline = dxline / ratio
            dyline = dyline / ratio
        else:
            if Version.get() == 'Eulerian':
                xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                     'Select the region for the subset construction on last captured image (Eulerian)',
                                                                     cv.imread(fileNamesSelectionLeft[-1]))
            else:
                xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                     'Select the region for the subset construction on first captured image (Lagrangian)',
                                                                     cv.imread(fileNamesSelectionLeft[0]))

        cv.destroyAllWindows()

        f.write('\nRegion for the subset construction:\n')
        f.write(str(int(xinitline)) + '\n')
        f.write(str(int(yinitline)) + '\n')
        f.write(str(int(dxline)) + '\n')
        f.write(str(int(dyline)))
        f.close()

        console.insert(tk.END, f'The ROI and subset construction was successfully saved in {file_ROI.get()}\n\n')
        console.see('insert')

        if Nx.get() == 0 and Ny.get() == 0:
            Nx.set(int(abs(dxline) / Step.get()))
            Ny.set(int(abs(dyline) / Step.get()))

        xriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        xriL = np.frombuffer(xriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        yriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        yriL = np.frombuffer(yriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        uriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        uriL = np.frombuffer(uriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
        vriL_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
        vriL = np.frombuffer(vriL_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)

        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                xriL[0, i, j] = xinitline * Opi.get() + ((j) * dxline * Opi.get()) / (Nx.get())
                yriL[0, i, j] = yinitline * Opi.get() + ((i) * dyline * Opi.get()) / (Ny.get())

        if NumCut.get() != 0:
            if 'Rectangular' in TypeCut.get():
                for i in range(0,NumCut.get()):
                    console.insert(tk.END, f'Select the rectangular cut region # {str(i+1)} and press enter key\n\n')
                    console.see('insert')
                    image = cv.imread(fileNamesSelectionLeft[0])
                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][int((Nx.get()+1)/2)]) or np.isnan(xriL[0][i+1][int((Nx.get()+1)/2)]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i][int((Nx.get()+1)/2)]/Opi.get())),(int(xriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get())),(255, 0, 0),2)
                            if np.isnan(xriL[0][int((Ny.get()+1)/2)][j]) or np.isnan(xriL[0][int((Ny.get()+1)/2)][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][int((Ny.get()+1)/2)][j]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j]/Opi.get())),(int(xriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get())),(255, 0, 0),2)


                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i][j+1]/Opi.get()),int(yriL[0][i][j+1]/Opi.get())),(0, 0, 255),1)

                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()+1):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i+1][j]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i+1][j]/Opi.get()),int(yriL[0][i+1][j]/Opi.get())),(0, 0, 255),1)


                    dxfigure = int(image.shape[1])
                    dyfigure = int(image.shape[0])

                    screen_width = menu.winfo_screenwidth() - 100
                    screen_height = menu.winfo_screenheight() - 100

                    # Change size of displayed image:
                    if dyfigure > screen_height:
                        ratio = screen_height / dyfigure
                        image_figure = cv.resize(image,
                                                 (int(screen_height * dxfigure / dyfigure), screen_height))
                        #image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                        xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                             'Select the rectangular cut region',
                                                                             image_figure)

                        xinitline = xinitline / ratio
                        yinitline = yinitline / ratio
                        dxline = dxline / ratio
                        dyline = dyline / ratio
                    else:
                        xinitline, yinitline, dxline, dyline = SelectROI_DIC(menu, console,
                                                                             'Select the rectangular cut region', image)

                    cv.destroyAllWindows()

                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()+1):

                            if xinitline <= xriL[0][i][j]/Opi.get() <= xinitline+dxline and yinitline <= yriL[0][i][j]/Opi.get() <= yinitline+dyline:
                                xriL[0][i][j] = float('nan')
                                yriL[0][i][j] = float('nan')
                                uriL[0][i][j] = float('nan')
                                vriL[0][i][j] = float('nan')

            if 'Circular inside' in TypeCut.get():
                for i in range(0,NumCut.get()):
                    console.insert(tk.END, f'Select the circular cutting region # {str(i+1)} and press enter key\n\n')
                    console.see('insert')

                    image = cv.imread(fileNamesSelectionLeft[0])
                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][int((Nx.get()+1)/2)]) or np.isnan(xriL[0][i+1][int((Nx.get()+1)/2)]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i][int((Nx.get()+1)/2)]/Opi.get())),(int(xriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get())),(255, 0, 0),3)
                            if np.isnan(xriL[0][int((Ny.get()+1)/2)][j]) or np.isnan(xriL[0][int((Ny.get()+1)/2)][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][int((Ny.get()+1)/2)][j]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j]/Opi.get())),(int(xriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get())),(255, 0, 0),3)

                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i][j+1]/Opi.get()),int(yriL[0][i][j+1]/Opi.get())),(0, 0, 255),2)

                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()+1):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i+1][j]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i+1][j]/Opi.get()),int(yriL[0][i+1][j]/Opi.get())),(0, 0, 255),2)

                    dxfigure = int(image.shape[1])
                    dyfigure = int(image.shape[0])

                    screen_width = menu.winfo_screenwidth() - 100
                    screen_height = menu.winfo_screenheight() - 100

                    # Change size of displayed image:
                    if dyfigure > screen_height:
                        ratio = screen_height / dyfigure
                        image_figure = cv.resize(image,
                                                 (int(screen_height * dxfigure / dyfigure), screen_height))
                        #image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                        pointsCut = CircularROI_DIC(menu, console,'Select the circular cut region',image_figure)

                        for w in range(0,len(pointsCut)):
                            pointsCut[w] = [x/ratio for x in pointsCut[w]]

                    else:
                        pointsCut = CircularROI_DIC(menu, console,'Select the circular cut region', image)

                    cv.destroyAllWindows()

                    polygon = Polygon(pointsCut)
                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()+1):
                            point = Point(xriL[0][i][j]/Opi.get(),yriL[0][i][j]/Opi.get())
                            if polygon.contains(point):
                                xriL[0][i][j] = float('nan')
                                yriL[0][i][j] = float('nan')
                                uriL[0][i][j] = float('nan')
                                vriL[0][i][j] = float('nan')

            if 'Circular outside' in TypeCut.get():
                for i in range(0,NumCut.get()):
                    console.insert(tk.END, f'Select the circular cutting region # {str(i+1)} and press enter key\n\n')
                    console.see('insert')

                    image = cv.imread(fileNamesSelectionLeft[0])
                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][int((Nx.get()+1)/2)]) or np.isnan(xriL[0][i+1][int((Nx.get()+1)/2)]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i][int((Nx.get()+1)/2)]/Opi.get())),(int(xriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get())),(255, 0, 0),3)
                            if np.isnan(xriL[0][int((Ny.get()+1)/2)][j]) or np.isnan(xriL[0][int((Ny.get()+1)/2)][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][int((Ny.get()+1)/2)][j]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j]/Opi.get())),(int(xriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get())),(255, 0, 0),3)

                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i][j+1]/Opi.get()),int(yriL[0][i][j+1]/Opi.get())),(0, 0, 255),2)

                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()+1):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i+1][j]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i+1][j]/Opi.get()),int(yriL[0][i+1][j]/Opi.get())),(0, 0, 255),2)

                    dxfigure = int(image.shape[1])
                    dyfigure = int(image.shape[0])

                    screen_width = menu.winfo_screenwidth() - 100
                    screen_height = menu.winfo_screenheight() - 100

                    # Change size of displayed image:
                    if dyfigure > screen_height:
                        ratio = screen_height / dyfigure
                        image_figure = cv.resize(image,
                                                 (int(screen_height * dxfigure / dyfigure), screen_height))
                        #image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                        pointsCut = CircularROI_DIC(menu, console,'Select the circular cut region',image_figure)

                        for w in range(0,len(pointsCut)):
                            pointsCut[w] = [x/ratio for x in pointsCut[w]]

                    else:
                        pointsCut = CircularROI_DIC(menu, console,'Select the circular cut region', image)

                    cv.destroyAllWindows()

                    polygon = Polygon(pointsCut)
                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()+1):
                            point = Point(xriL[0][i][j]/Opi.get(),yriL[0][i][j]/Opi.get())
                            if polygon.contains(point):
                                pass
                            else:
                                xriL[0][i][j] = float('nan')
                                yriL[0][i][j] = float('nan')
                                uriL[0][i][j] = float('nan')
                                vriL[0][i][j] = float('nan')

            if 'Free' in TypeCut.get():
                for i in range(0,NumCut.get()):
                    console.insert(tk.END, f'Select the freehand cutting region # {str(i+1)} and press enter key\n\n')
                    console.see('insert')

                    image = cv.imread(fileNamesSelectionLeft[0])
                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][int((Nx.get()+1)/2)]) or np.isnan(xriL[0][i+1][int((Nx.get()+1)/2)]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i][int((Nx.get()+1)/2)]/Opi.get())),(int(xriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get()),int(yriL[0][i+1][int((Nx.get()+1)/2)]/Opi.get())),(255, 0, 0),2)
                            if np.isnan(xriL[0][int((Ny.get()+1)/2)][j]) or np.isnan(xriL[0][int((Ny.get()+1)/2)][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][int((Ny.get()+1)/2)][j]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j]/Opi.get())),(int(xriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get()),int(yriL[0][int((Ny.get()+1)/2)][j+1]/Opi.get())),(255, 0, 0),2)


                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i][j+1]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i][j+1]/Opi.get()),int(yriL[0][i][j+1]/Opi.get())),(0, 0, 255),1)

                    for i in range(0, Ny.get()):
                        for j in range(0, Nx.get()+1):
                            if np.isnan(xriL[0][i][j]) or np.isnan(xriL[0][i+1][j]):
                                pass
                            else:
                                image = cv.line(image,(int(xriL[0][i][j]/Opi.get()),int(yriL[0][i][j]/Opi.get())),(int(xriL[0][i+1][j]/Opi.get()),int(yriL[0][i+1][j]/Opi.get())),(0, 0, 255),1)

                    dxfigure = int(image.shape[1])
                    dyfigure = int(image.shape[0])

                    screen_width = menu.winfo_screenwidth() - 100
                    screen_height = menu.winfo_screenheight() - 100

                    # Change size of displayed image:
                    if dyfigure > screen_height:
                        ratio = screen_height / dyfigure
                        image_figure = cv.resize(image,
                                                 (int(screen_height * dxfigure / dyfigure), screen_height))
                        #image_figure = cv.cvtColor(image_figure, cv.COLOR_GRAY2RGB)
                        pointsCut = freehandCut('Select the freehand cutting region', image_figure)

                        for w in range(0,len(pointsCut)):
                            pointsCut[w] = [x/ratio for x in pointsCut[w]]

                    else:
                        pointsCut = freehandCut('Select the freehand cutting region', image)

                    cv.destroyAllWindows()

                    polygon = Polygon(pointsCut)
                    for i in range(0, Ny.get()+1):
                        for j in range(0, Nx.get()+1):
                            point = Point(xriL[0][i][j]/Opi.get(),yriL[0][i][j]/Opi.get())
                            if polygon.contains(point):
                                xriL[0][i][j] = float('nan')
                                yriL[0][i][j] = float('nan')
                                uriL[0][i][j] = float('nan')
                                vriL[0][i][j] = float('nan')

        # Left mesh update figure:
        figL = plt.figure()
        ax = figL.gca()
        dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
        dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

        ratio_plot = dxplot / dyplot;

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
            ax.plot(np.transpose(xriL[0][:][:] / Opi.get()), np.transpose(yriL[0][:][:] / Opi.get()), color='red',
                    linewidth=1, zorder=3)
            ax.plot(xriL[0][:][:] / Opi.get(), yriL[0][:][:] / Opi.get(), color='red', linewidth=1, zorder=3)
            winSub = False
            for i in range(0, Ny.get() + 1):
                for j in range(0, Nx.get() + 1):
                    if ~np.isnan(xriL[0][i][j]):

                        ax.plot(
                            [xriL[0][i][j] / Opi.get() - SubIrS.get() / 2, xriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                             xriL[0][i][j] / Opi.get() + SubIrS.get() / 2, xriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                             xriL[0][i][j] / Opi.get() - SubIrS.get() / 2],
                            [yriL[0][i][j] / Opi.get() + SubIrS.get() / 2, yriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                             yriL[0][i][j] / Opi.get() - SubIrS.get() / 2, yriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                             yriL[0][i][j] / Opi.get() + SubIrS.get() / 2],
                            color='#00FF00', linewidth=1, zorder=3)  # SubIr window

                        ax.plot(
                            [xriL[0][i][j] / Opi.get() - SubIbS.get() / 2, xriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                             xriL[0][i][j] / Opi.get() + SubIbS.get() / 2, xriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                             xriL[0][i][j] / Opi.get() - SubIbS.get() / 2],
                            [yriL[0][i][j] / Opi.get() + SubIbS.get() / 2, yriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                             yriL[0][i][j] / Opi.get() - SubIbS.get() / 2, yriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                             yriL[0][i][j] / Opi.get() + SubIbS.get() / 2],
                            color='blue', linewidth=1, zorder=3)  # SubIb window

                        winSub = True
                        break
                    else:
                        continue

                if winSub: break
            ax.plot(
                [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
                [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between(
                [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
                [0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
            ax.plot(np.transpose(xriL[0][:][:] / Opi.get()), np.transpose(yriL[0][:][:] / Opi.get()), color='red',
                    linewidth=1, zorder=3)
            ax.plot(xriL[0][:][:] / Opi.get(), yriL[0][:][:] / Opi.get(), color='red', linewidth=1, zorder=3)
            winSub = False
            for i in range(0, Ny.get() + 1):
                for j in range(0, Nx.get() + 1):
                    if ~np.isnan(xriL[0][i][j]):

                        ax.plot(
                            [xriL[0][i][j] / Opi.get() - SubIrS.get() / 2, xriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                             xriL[0][i][j] / Opi.get() + SubIrS.get() / 2, xriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                             xriL[0][i][j] / Opi.get() - SubIrS.get() / 2],
                            [yriL[0][i][j] / Opi.get() + SubIrS.get() / 2, yriL[0][i][j] / Opi.get() + SubIrS.get() / 2,
                             yriL[0][i][j] / Opi.get() - SubIrS.get() / 2, yriL[0][i][j] / Opi.get() - SubIrS.get() / 2,
                             yriL[0][i][j] / Opi.get() + SubIrS.get() / 2],
                            color='#00FF00', linewidth=1, zorder=3)  # SubIr window

                        ax.plot(
                            [xriL[0][i][j] / Opi.get() - SubIbS.get() / 2, xriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                             xriL[0][i][j] / Opi.get() + SubIbS.get() / 2, xriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                             xriL[0][i][j] / Opi.get() - SubIbS.get() / 2],
                            [yriL[0][i][j] / Opi.get() + SubIbS.get() / 2, yriL[0][i][j] / Opi.get() + SubIbS.get() / 2,
                             yriL[0][i][j] / Opi.get() - SubIbS.get() / 2, yriL[0][i][j] / Opi.get() - SubIbS.get() / 2,
                             yriL[0][i][j] / Opi.get() + SubIbS.get() / 2],
                            color='blue', linewidth=1, zorder=3)  # SubIb window

                        winSub = True
                        break
                    else:
                        continue

                if winSub: break
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                    [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                     +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                     0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                            [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                             +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                             0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        figL.canvas.draw()

        imageL = np.frombuffer(figL.canvas.tostring_rgb(), dtype=np.uint8)
        wL, hL = figL.canvas.get_width_height()
        imageL = np.flip(imageL.reshape((hL, wL, 3)), axis=0)

        plt.cla()
        plt.clf()

        # Right mesh update figure:
        figR = plt.figure()
        ax = figR.gca()
        dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
        dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

        if ratio_plot <= 1.33333333:

            dxplotdark = dyplot * 1.33333333
            dyplotdark = dyplot
            ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
            ax.plot(
                [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
                [0, dyplotdark, dyplotdark, 0, 0], 'black', zorder=1)
            ax.fill_between(
                [0 - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2,
                 dxplotdark - dxplotdark / 2 + dxplot / 2, 0 - dxplotdark / 2 + dxplot / 2],
                [0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(-dxplotdark / 2 + dxplot / 2, dxplotdark - dxplotdark / 2 + dxplot / 2)
            plt.ylim(0, dyplotdark)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        else:
            dxplotdark = dxplot
            dyplotdark = dxplot / 1.33333333
            ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
            ax.plot([0, 0, dxplotdark, dxplotdark, 0],
                    [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                     +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                     0 - dyplotdark / 2 + dyplot / 2], 'black', zorder=1)
            ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],
                            [0 - dyplotdark / 2 + dyplot / 2, +dyplotdark - dyplotdark / 2 + dyplot / 2,
                             +dyplotdark - dyplotdark / 2 + dyplot / 2, 0 - dyplotdark / 2 + dyplot / 2,
                             0 - dyplotdark / 2 + dyplot / 2], color='black', zorder=1)
            ax.axis('off')
            plt.xlim(0, dxplotdark)
            plt.ylim(-dyplotdark / 2 + dyplot / 2, dyplotdark - dyplotdark / 2 + dyplot / 2)
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        figR.canvas.draw()

        imageR = np.frombuffer(figR.canvas.tostring_rgb(), dtype=np.uint8)
        wR, hR = figR.canvas.get_width_height()
        imageR = np.flip(imageR.reshape((hR, wR, 3)), axis=0)

        plt.cla()
        plt.clf()

        image_left = cv.resize(imageL, (426, 320))
        cv.putText(image_left, f'MASTER L - {1}', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
        cv.putText(image_left, f'CORRELATION MESH - {np.count_nonzero(~np.isnan(xriL[0][:][:]))} nodes', (5, 40),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
        cv.putText(image_left, 'REFERENCE SUBSET', (5, 60), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
        cv.putText(image_left, 'SEARCH SUBSET', (5, 80), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
        image_left = ImageTk.PhotoImage(Image.fromarray(image_left))

        canvas_left.image_left = image_left
        canvas_left.configure(image=image_left)

        image_right = cv.resize(imageR, (426, 320))
        cv.putText(image_right, f'SLAVE R - {1}', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
        image_right = ImageTk.PhotoImage(Image.fromarray(image_right))

        canvas_right.image_right = image_right
        canvas_right.configure(image=image_right)

        console.insert(tk.END, 'Start the correlation process\n\n')
        console.see('insert')

        messagebox.showinfo('Information', 'Press start to initialize the stereo correlation!')

########################################################################################################################
# Initialize function
########################################################################################################################
def initialize(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
    Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
    Filtering, Kernel, ResultsName, process_btn, abort_param, progression, progression_bar, canvas_left, canvas_right,
    canvas_text, console_process, method_corr_dict,Cores):

    global fileNamesLeft, fileNamesRight, calib, t2

    try:
        fileNamesLeft, fileNamesRight, calib, xriL
    except NameError:
        messagebox.showerror('Error','Please load project or select the image captured folder, calibration file and DIC settings before starting the correlation process!')
    else:

        if SubIrS.get() >= SubIbS.get() or SubIrT.get() >= SubIbT.get():
            messagebox.showerror('Error','The search subset size must be larger than the reference subset size. Please change the input data!')
        else:
            save(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
                 Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
                 Filtering, Kernel)

            process_btn.configure(text='Abort',fg='#cc0000',command = lambda: abort(abort_param))

            t2 = Thread(target=Corr3D, args=(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
               Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
               Filtering, Kernel, ResultsName, process_btn, abort_param, progression, progression_bar, canvas_left, canvas_right,
               canvas_text, console_process, method_corr_dict,Cores))
            t2.setDaemon(True)
            t2.start()

########################################################################################################################
# Time function
########################################################################################################################
def second2dhms(sec):
    day = sec // (24 * 3600)
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    minutes = sec // 60
    sec %= 60
    seconds = sec

    return '%02d - %02d:%02d:%02d' % (day, hour, minutes, seconds)

########################################################################################################################
# 3D DIC main
########################################################################################################################
def Corr3D(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
    Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
    Filtering, Kernel, ResultsName, process_btn, abort_param, progression, progression_bar, canvas_left, canvas_right,
    canvas_text, console_process, method_corr_dict,Cores):

    global fileNamesSelectionLeft, fileNamesSelectionRight, selectionPathLeft, selectionPathRight, resultsPath
    global fileNamesLeft, fileNamesRight, Format, Images, calib
    global xriL_mem, yriL_mem, uriL_mem, vriL_mem, xriR_mem, yriR_mem, uriR_mem, vriR_mem

    abort_param.set(False)

    if Interpolation.get() == 'After':
        Opi.set(1)
        console.insert(tk.END,
                       f'The interpolation factor was changed to 1 according to the interpolation preference (after correlation)!\n\n')
        console.see('insert')

    resultsPath = capturedFolder.get().rsplit('/', 1)[0] + f'/{ResultsName.get()}'
    if not os.path.exists(resultsPath):
        os.makedirs(resultsPath)
        console.insert(tk.END, f'The {ResultsName.get()} folder was created\n\n')
        console.see('insert')
    else:
        console.insert(tk.END, f'The {ResultsName.get()} folder is already in the main directory\n\n')
        console.see('insert')

    for files in os.listdir(resultsPath):
        if files.endswith(".dat"):
            os.remove(os.path.join(resultsPath, files))

    # R variables - parallel computing:
    xriR_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    xriR = np.frombuffer(xriR_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
    yriR_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    yriR = np.frombuffer(yriR_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
    uriR_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    uriR = np.frombuffer(uriR_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)
    vriR_mem = RawArray(ctypes.c_double, (Images + 1) * (Ny.get() + 1) * (Nx.get() + 1))
    vriR = np.frombuffer(vriR_mem, dtype=np.float64).reshape(Images + 1, Ny.get() + 1, Nx.get() + 1)

    time_iter = np.zeros(Images+1)

    # Correlation functions:
    method_var = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR', 'cv.TM_CCORR_NORMED']
    matchTemplate_method = eval(f'{method_var[method_corr_dict.get(Method.get())]}')

    # Output files:
    filexWCS='xmWCS{:02d}.dat'; fileyWCS='ymWCS{:02d}.dat'; filezWCS='zmWCS{:02d}.dat'; fileuWCS='umWCS{:02d}.dat'; filevWCS='vmWCS{:02d}.dat'; filewWCS='wmWCS{:02d}.dat'
    filexSPCS = 'xmSPCS{:02d}.dat'; fileySPCS = 'ymSPCS{:02d}.dat'; filezSPCS = 'zmSPCS{:02d}.dat'; fileuSPCS = 'umSPCS{:02d}.dat'; filevSPCS = 'vmSPCS{:02d}.dat'; filewSPCS = 'wmSPCS{:02d}.dat'
    filexL = 'xmL{:02d}.dat'; fileyL = 'ymL{:02d}.dat'; filexR = 'xmR{:02d}.dat'; fileyR = 'ymR{:02d}.dat';

    SubIrStereo = SubIrS.get()*Opi.get()
    SubIbStereo = SubIbS.get()*Opi.get()
    SubIrTemporal = SubIrT.get()*Opi.get()
    SubIbTemporal = SubIbT.get()*Opi.get()

    # Divide the subset points in groups to perform the parallel computing:
    cores_x = int(Cores.get() / 2 + 1)
    cores_y = int(Cores.get() / (cores_x - 1) + 1)

    ii = np.linspace(0, Ny.get() + 1, num=cores_y, dtype="int")
    i1 = ii[1:]
    i0 = ii[0:cores_y - 1];
    i0[0] = 0

    jj = np.linspace(0, Nx.get() + 1, num=cores_x, dtype="int")
    j1 = jj[1:]
    j0 = jj[0:cores_x - 1];
    j0[0] = 0

    i0_list = np.repeat(i0, cores_x - 1)
    i1_list = np.repeat(i1, cores_x - 1)

    j0_list = np.tile(j0, cores_y - 1)
    j1_list = np.tile(j1, cores_y - 1)

    console.insert(tk.END, 'The process has started\n\n')

    start_process = time.time()

    start = time.time()

    progression.coords(progression_bar, 0, 0, 0, 25); progression.itemconfig(canvas_text, text='')

    console.insert(tk.END, '############################################# Correlation parameters #############################################\n\n')
    console.insert(tk.END, f'Interpolation type ........................................................................... {Interpolation.get()}\n')
    console.insert(tk.END, f'Image interpolation factor ................................................................... {Opi.get()}\n')
    console.insert(tk.END, f'Subpixel after correlation ................................................................... {OpiSub.get()}\n')
    console.insert(tk.END, f'Contrast adjust .............................................................................. {Adjust.get()}\n')
    console.insert(tk.END, f'Search subset size for stereo correlation (SSS S) ............................................ {SubIbS.get()}\n')
    console.insert(tk.END, f'Reference subset size for stereo correlation (RSS S) ......................................... {SubIrS.get()}\n')
    console.insert(tk.END, f'Search subset size for temporal correlation (SSS T) .......................................... {SubIbT.get()}\n')
    console.insert(tk.END, f'Reference subset size for temporal correlation (RSS T) ....................................... {SubIrT.get()}\n')
    console.insert(tk.END, f'Subset step (ST) ............................................................................. {Step.get()}\n')
    console.insert(tk.END, f'Number of steps in x direction ............................................................... {Nx.get()}\n')
    console.insert(tk.END, f'Number of steps in y direction ............................................................... {Ny.get()}\n')
    console.insert(tk.END, f'Selected description ......................................................................... {Version.get()}\n')
    console.insert(tk.END, f'Correlation type ............................................................................. {Correlation.get()}\n')
    console.insert(tk.END, f'Correlation function ......................................................................... {method_var[method_corr_dict.get(Method.get())]}\n')
    console.insert(tk.END, f'Correlation criterion ........................................................................ {Criterion.get()}\n')
    console.insert(tk.END, f'Filtering .................................................................................... {Filtering.get()}\n')
    console.insert(tk.END, f'Kernel size for filtering .................................................................... {Kernel.get()}\n')
    console.insert(tk.END, f'Calculation points ........................................................................... {np.count_nonzero(~np.isnan(xriL[0][:][:]))}\n')
    console.insert(tk.END, f'Number of processors ......................................................................... {Cores.get()}\n\n')
    console.insert(tk.END, '##################################################################################################################\n\n')
    console.see('insert')

    console.insert(tk.END, 'Stereo correlation ')
    console.see('insert')

    # Reference stereo pair:
    I0 = cv.cvtColor(cv.imread(fileNamesSelectionLeft[0]), cv.COLOR_BGR2GRAY)
    I1 = cv.cvtColor(cv.imread(fileNamesSelectionRight[0]), cv.COLOR_BGR2GRAY)

    IrefL = cv.resize(I0, (int(I0.shape[1] * Opi.get()), int(I0.shape[0] * Opi.get())), interpolation=cv.INTER_CUBIC)
    IrefR = cv.resize(I1, (int(I1.shape[1] * Opi.get()), int(I1.shape[0] * Opi.get())), interpolation=cv.INTER_CUBIC)

    if Interpolation.get() == 'Before':
        process_list = []
        for i in range(Cores.get()):
            process_list.append(mp.Process(target=Corr2D_Stereo_V1, args=(0, SubIrStereo, SubIbStereo,
                                          xriL_mem, xriL.shape, yriL_mem, yriL.shape, xriR_mem, xriR.shape, yriR_mem, yriR.shape,
                                                                          IrefL, IrefR, matchTemplate_method,
                                          Criterion.get(), i0_list[i],i1_list[i],j0_list[i],j1_list[i])))
            try:
                process_list[i].start()
            except:
                messagebox.showerror('Error RAM',
                                     'The correlation runs out of memory RAM! Please reduce the number of designated processors or reduce the kb interpolation factor.')

                menu.destroy()
                menu.quit()

        for i in range(Cores.get()):
            process_list[i].join()

    else:
        process_list = []
        for i in range(Cores.get()):
            process_list.append(mp.Process(target=Corr2D_Stereo_V2, args=(0, SubIrStereo, SubIbStereo, OpiSub.get(),
                                                                          xriL_mem, xriL.shape, yriL_mem, yriL.shape,
                                                                          xriR_mem, xriR.shape, yriR_mem, yriR.shape,
                                                                          IrefL, IrefR, matchTemplate_method,
                                                                          Criterion.get(), i0_list[i], i1_list[i],
                                                                          j0_list[i], j1_list[i])))

            try:
                process_list[i].start()
            except:
                messagebox.showerror('Error RAM',
                                     'The correlation runs out of memory RAM! Please reduce the number of designated processors or reduce the kb interpolation factor.')

                menu.destroy()
                menu.quit()

        for i in range(Cores.get()):
            process_list[i].join()

    console.insert(tk.END, '- Done\n')
    console.insert(tk.END, 'Creation of variables ')
    console.see('insert')

    xmL = xriL[0][:][:]/Opi.get(); ymL = yriL[0][:][:]/Opi.get()
    xmR = xriR[0][:][:]/Opi.get(); ymR = yriR[0][:][:]/Opi.get()

    Xw = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))
    Yw = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))
    Zw = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))

    Xcp = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))
    Ycp = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))
    Zcp = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))

    Xcp_int = np.zeros((Images + 1, Ny.get() + 1, Nx.get() + 1))
    Ycp_int = np.zeros((Images + 1, Ny.get() + 1, Nx.get() + 1))
    Zcp_int = np.zeros((Images + 1, Ny.get() + 1, Nx.get() + 1))

    Uw = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))
    Vw = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))
    Ww = np.zeros((Images+1, Ny.get()+1, Nx.get()+1))

    Ucp = np.zeros((Images + 1, Ny.get() + 1, Nx.get() + 1))
    Vcp = np.zeros((Images + 1, Ny.get() + 1, Nx.get() + 1))
    Wcp = np.zeros((Images + 1, Ny.get() + 1, Nx.get() + 1))

    console.insert(tk.END, '- Done\n')
    console.insert(tk.END, '3D reconstruction of stereo correlation in the world coordinate system (WCS - Left Camera) ')
    console.see('insert')

    for i in range(0, Ny.get()+1):
        for j in range(0, Nx.get()+1):
            if np.isnan(xmL[i][j]):
                Xw[0][i][j] = float('nan'); Yw[0][i][j] = float('nan'); Zw[0][i][j] = float('nan');
                Uw[0][i][j] = float('nan'); Vw[0][i][j] = float('nan'); Ww[0][i][j] = float('nan');
            else:
                Xw[0][i][j], Yw[0][i][j], Zw[0][i][j] = ReconstructionWCS(xmL[i][j], ymL[i][j], xmR[i][j], ymR[i][j], calib)
                Uw[0][i][j] = 0.0; Vw[0][i][j] = 0.0; Ww[0][i][j] = 0.0;

    console.insert(tk.END, '- Done\n')
    console.insert(tk.END, 'Saving files ')
    console.see('insert')

    xm = Xw[0][:][:].copy()
    ym = Yw[0][:][:].copy()
    zm = Zw[0][:][:].copy()
    um = Uw[0][:][:].copy()
    vm = Vw[0][:][:].copy()
    wm = Ww[0][:][:].copy()

    if Filtering.get() == 'Gaussian':
        test_blur = cv.GaussianBlur(um.copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)

        # Determination of valid mask area:
        valid_mask_blur = np.isnan(test_blur)

        # Add nan values according to displacement data:
        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                if valid_mask_blur[i][j]:
                    xm[i][j] = float('nan')
                    ym[i][j] = float('nan')
                    zm[i][j] = float('nan')
                    um[i][j] = float('nan')
                    vm[i][j] = float('nan')
                    wm[i][j] = float('nan')

    np.savetxt(f'{resultsPath}/{filexWCS.format(1)}', xm, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{fileyWCS.format(1)}', ym, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filexL.format(1)}', xmL, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{fileyL.format(1)}', ymL, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filexR.format(1)}', xmR, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{fileyR.format(1)}', ymR, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filezWCS.format(1)}', zm, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{fileuWCS.format(1)}', um, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filevWCS.format(1)}', vm, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filewWCS.format(1)}', wm, fmt='%.10e')

    del xm, ym, zm, um, vm, wm

    console.insert(tk.END, '- Done\n')
    console.insert(tk.END, 'Rotation matrix (R) and translation vector (T) estimation for referential transformation ')
    console.see('insert')

    # Determination of the valid mask
    valid_mask = ~np.isnan(Xw[0][:][:])
    coords = np.array(np.nonzero(valid_mask)).T

    mask = np.zeros((Ny.get() + 1, Nx.get() + 1))
    mask_teste = False
    for i in range(0, Ny.get() + 1):
        for j in range(0, Nx.get() + 1):
            if valid_mask[i][j]:
                mask[i][j] = 0
            else:
                mask[i][j] = 1
                mask_teste = True

    if mask_teste:
        Maskinterp = cv.resize(mask, dsize=(Nx.get() + 1, Ny.get() + 1), interpolation=cv.INTER_LINEAR)

        values = Xw[0][:][:][valid_mask]
        it = interpolate.LinearNDInterpolator(coords, values, fill_value=0)
        filledx = it(list(np.ndindex(Xw[0][:][:].shape))).reshape(Xw[0][:][:].shape)

        values = Yw[0][:][:][valid_mask]
        it = interpolate.LinearNDInterpolator(coords, values, fill_value=0)
        filledy = it(list(np.ndindex(Yw[0][:][:].shape))).reshape(Yw[0][:][:].shape)

        values = Zw[0][:][:][valid_mask]
        it = interpolate.LinearNDInterpolator(coords, values, fill_value=0)
        filledz = it(list(np.ndindex(Zw[0][:][:].shape))).reshape(Zw[0][:][:].shape)

        xo = filledx[round(Ny.get() / 2)][:]

        yo = filledy.T[:][round(Nx.get() / 2)]

        cx = np.linspace(xo[0], xo[Nx.get()], Nx.get() + 1)
        cy = np.linspace(yo[0], yo[Ny.get()], Ny.get() + 1)

        fx = interp2d(xo, yo, filledx, kind='linear')

        fy = interp2d(xo, yo, filledy, kind='linear')

        fz = interp2d(xo, yo, filledz, kind='linear')

        Xcp_int[0][:][:] = fx(cx, cy)

        Ycp_int[0][:][:] = fy(cx, cy)

        Zcp_int[0][:][:] = fz(cx, cy)

        T = [Xcp_int[0][round(Ny.get() / 2)][round(Nx.get() / 2)], Ycp_int[0][round(Ny.get() / 2)][round(Nx.get() / 2)],
             Zcp_int[0][round(Ny.get() / 2)][round(Nx.get() / 2)]]

        # Unit vectors:
        ex = (np.subtract([Xcp_int[0][int(Ny.get() / 2)][-1], Ycp_int[0][int(Ny.get() / 2)][-1],Zcp_int[0][int(Ny.get() / 2)][-1]],
             [Xcp_int[0][int(Ny.get() / 2)][0], Ycp_int[0][int(Ny.get() / 2)][0],Zcp_int[0][int(Ny.get() / 2)][0]])) / np.linalg.norm(np.subtract(
            [Xcp_int[0][int(Ny.get() / 2)][-1], Ycp_int[0][int(Ny.get() / 2)][-1], Zcp_int[0][int(Ny.get() / 2)][-1]],
            [Xcp_int[0][int(Ny.get() / 2)][0], Ycp_int[0][int(Ny.get() / 2)][0],Zcp_int[0][int(Ny.get() / 2)][0]]));

        ey = (np.subtract([Xcp_int[0][-1][int(Nx.get() / 2)], Ycp_int[0][-1][int(Nx.get() / 2)],Zcp_int[0][-1][int(Nx.get() / 2)]],
              [Xcp_int[0][0][int(Nx.get() / 2)], Ycp_int[0][0][int(Nx.get() / 2)],Zcp_int[0][0][int(Nx.get() / 2)]]))/ np.linalg.norm(np.subtract(
            [Xcp_int[0][-1][int(Nx.get() / 2)], Ycp_int[0][-1][int(Nx.get() / 2)], Zcp_int[0][-1][int(Nx.get() / 2)]],
        [Xcp_int[0][0][int(Nx.get() / 2)], Ycp_int[0][0][int(Nx.get() / 2)], Zcp_int[0][0][int(Nx.get() / 2)]]));

        ez = np.cross(ex, [i * -1 for i in ey]);

        # Rotation matrix:
        R = [[ex[0], ey[0], ez[0]],
             [ex[1], ey[1], ez[1]],
             [ex[2], ey[2], ez[2]]]

        RINV = np.linalg.inv(R)

        console.insert(tk.END, '- Done\n')
        console.insert(tk.END, '3D reconstruction of stereo correlation in the specimen coordinate system (SPCS) ')
        console.see('insert')

        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                if Maskinterp[i][j] == 0:
                    Xcp[0][i][j] = np.matmul(RINV[0][:], [Xw[0][i][j] - T[0], Yw[0][i][j] - T[1], Zw[0][i][j] - T[2]]);
                    Ycp[0][i][j] = np.matmul(RINV[1][:], [Xw[0][i][j] - T[0], Yw[0][i][j] - T[1], Zw[0][i][j] - T[2]]);
                    Zcp[0][i][j] = np.matmul(RINV[2][:], [Xw[0][i][j] - T[0], Yw[0][i][j] - T[1], Zw[0][i][j] - T[2]]);
                else:
                    Xcp[0][i][j] = 'nan'
                    Ycp[0][i][j] = 'nan'
                    Zcp[0][i][j] = 'nan'

    else:

        T = [Xw[0][round(Ny.get() / 2)][round(Nx.get() / 2)], Yw[0][round(Ny.get() / 2)][round(Nx.get() / 2)],
             Zw[0][round(Ny.get() / 2)][round(Nx.get() / 2)]]

        # Unit vectors:
        def mid(list):
            middle = int(len(list) / 2)
            return middle

        ex = np.subtract([Xw[0][mid(Xw[0][:][0])][-1], Yw[0][mid(Yw[0][:][0])][-1], Zw[0][mid(Zw[0][:][0])][-1]],
                         [Xw[0][mid(Xw[0][:][0])][0], Yw[0][mid(Yw[0][:][0])][0], Zw[0][mid(Zw[0][:][0])][0]]) / np.linalg.norm(
            np.subtract([Xw[0][mid(Xw[0][:][0])][-1], Yw[0][mid(Yw[0][:][0])][-1], Zw[0][mid(Zw[0][:][0])][-1]],
                        [Xw[0][mid(Xw[0][:][0])][0], Yw[0][mid(Yw[0][:][0])][0], Zw[0][mid(Zw[0][:][0])][0]]));

        ey = np.subtract([Xw[0][-1][mid(Xw[0][0][:])], Yw[0][-1][mid(Yw[0][0][:])], Zw[0][-1][mid(Zw[0][0][:])]],
                         [Xw[0][0][mid(Xw[0][0][:])], Yw[0][0][mid(Yw[0][0][:])], Zw[0][0][mid(Zw[0][0][:])]]) / np.linalg.norm(
            np.subtract([Xw[0][-1][mid(Xw[0][0][:])], Yw[0][-1][mid(Yw[0][0][:])], Zw[0][-1][mid(Zw[0][0][:])]],
                        [Xw[0][0][mid(Xw[0][0][:])], Yw[0][0][mid(Yw[0][0][:])], Zw[0][0][mid(Zw[0][0][:])]]));

        ez = np.cross(ex, [i * -1 for i in ey]);

        R = [[ex[0], ey[0], ez[0]],
             [ex[1], ey[1], ez[1]],
             [ex[2], ey[2], ez[2]]]

        RINV = np.linalg.inv(R)

        console.insert(tk.END, '- Done\n')
        console.insert(tk.END, '3D reconstruction of stereo correlation in the specimen coordinate system (SPCS) ')
        console.see('insert')

        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                Xcp[0][i][j] = np.matmul(RINV[0][:], [Xw[0][i][j] - T[0], Yw[0][i][j] - T[1], Zw[0][i][j] - T[2]]);
                Ycp[0][i][j] = np.matmul(RINV[1][:], [Xw[0][i][j] - T[0], Yw[0][i][j] - T[1], Zw[0][i][j] - T[2]]);
                Zcp[0][i][j] = np.matmul(RINV[2][:], [Xw[0][i][j] - T[0], Yw[0][i][j] - T[1], Zw[0][i][j] - T[2]]);

    console.insert(tk.END, '- Done\n')
    console.insert(tk.END, 'Saving files ')
    console.see('insert')

    xm = Xcp[0][:][:].copy()
    ym = Ycp[0][:][:].copy()
    zm = Zcp[0][:][:].copy()
    um = Uw[0][:][:].copy()
    vm = Vw[0][:][:].copy()
    wm = Ww[0][:][:].copy()

    if Filtering.get() == 'Gaussian':
        test_blur = cv.GaussianBlur(um.copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)

        # Determination of valid mask area:
        valid_mask_blur = np.isnan(test_blur)

        # Add nan values according to displacement data:
        for i in range(0, Ny.get() + 1):
            for j in range(0, Nx.get() + 1):
                if valid_mask_blur[i][j]:
                    xm[i][j] = float('nan')
                    ym[i][j] = float('nan')
                    zm[i][j] = float('nan')
                    um[i][j] = float('nan')
                    vm[i][j] = float('nan')
                    wm[i][j] = float('nan')

    np.savetxt(f'{resultsPath}/{filexSPCS.format(1)}', xm, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{fileySPCS.format(1)}', ym, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filezSPCS.format(1)}', zm, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{fileuSPCS.format(1)}', um, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filevSPCS.format(1)}', vm, fmt='%.10e')
    np.savetxt(f'{resultsPath}/{filewSPCS.format(1)}', wm, fmt='%.10e')

    del xm, ym, zm, um, vm, wm

    np.savetxt(f'{resultsPath}/Rotation.dat', RINV, fmt='%.10e')
    np.savetxt(f'{resultsPath}/Translation.dat', T, fmt='%.10e')

    console.insert(tk.END, '- Done\n')
    console.see('insert')

    # Left mesh update figure:
    figL = plt.figure()
    ax = figL.gca()
    dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
    dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

    ratio_plot = dxplot/dyplot;

    if ratio_plot <= 1.33333333:

        dxplotdark = dyplot*1.33333333
        dyplotdark = dyplot
        ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
        ax.plot(np.transpose(xriL[0][:][:]/Opi.get()), np.transpose(yriL[0][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
        ax.plot(xriL[0][:][:]/Opi.get(), yriL[0][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
        ax.plot([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0],'black', zorder=1)
        ax.fill_between([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(-dxplotdark/2+dxplot/2,dxplotdark-dxplotdark/2+dxplot/2)
        plt.ylim(0,dyplotdark)
        plt.subplots_adjust(0,0,1,1,0,0)

    else:
        dxplotdark = dxplot
        dyplotdark = dxplot/1.33333333
        ax.imshow(cv.imread(fileNamesSelectionLeft[0]), zorder=2)
        ax.plot(np.transpose(xriL[0][:][:]/Opi.get()), np.transpose(yriL[0][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
        ax.plot(xriL[0][:][:]/Opi.get(), yriL[0][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
        ax.plot([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2],'black', zorder=1)
        ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(0,dxplotdark)
        plt.ylim(-dyplotdark/2+dyplot/2,dyplotdark-dyplotdark/2+dyplot/2)
        plt.subplots_adjust(0,0,1,1,0,0)

    figL.canvas.draw()

    imageL = np.frombuffer(figL.canvas.tostring_rgb(), dtype=np.uint8)
    wL, hL = figL.canvas.get_width_height()
    imageL = np.flip(imageL.reshape((hL, wL, 3)),axis=0)

    plt.cla()
    plt.clf()

    # Right mesh update figure:
    figR = plt.figure()
    ax = figR.gca()
    dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
    dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

    if ratio_plot <= 1.33333333:

        dxplotdark = dyplot*1.33333333
        dyplotdark = dyplot
        ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
        ax.plot(np.transpose(xriR[0][:][:]/Opi.get()), np.transpose(yriR[0][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
        ax.plot(xriR[0][:][:]/Opi.get(), yriR[0][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
        ax.plot([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0],'black', zorder=1)
        ax.fill_between([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(-dxplotdark/2+dxplot/2,dxplotdark-dxplotdark/2+dxplot/2)
        plt.ylim(0,dyplotdark)
        plt.subplots_adjust(0,0,1,1,0,0)

    else:
        dxplotdark = dxplot
        dyplotdark = dxplot/1.33333333
        ax.imshow(cv.imread(fileNamesSelectionRight[0]), zorder=2)
        ax.plot(np.transpose(xriR[0][:][:]/Opi.get()), np.transpose(yriR[0][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
        ax.plot(xriR[0][:][:]/Opi.get(), yriR[0][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
        ax.plot([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2],'black', zorder=1)
        ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2], color='black', zorder=1)
        ax.axis('off')
        plt.xlim(0,dxplotdark)
        plt.ylim(-dyplotdark/2+dyplot/2,dyplotdark-dyplotdark/2+dyplot/2)
        plt.subplots_adjust(0,0,1,1,0,0)

    figR.canvas.draw()

    imageR = np.frombuffer(figR.canvas.tostring_rgb(), dtype=np.uint8)
    wR, hR = figR.canvas.get_width_height()
    imageR = np.flip(imageR.reshape((hR, wR, 3)),axis=0)

    plt.cla()
    plt.clf()

    image_left = cv.resize(imageL, (426, 320))
    cv.putText(image_left,f'MASTER L - {1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
    image_left = ImageTk.PhotoImage (Image.fromarray (image_left))

    canvas_left.image_left = image_left
    canvas_left.configure(image = image_left)

    image_right = cv.resize(imageR, (426, 320))
    cv.putText(image_right,f'SLAVE R - {1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
    image_right = ImageTk.PhotoImage (Image.fromarray (image_right))

    canvas_right.image_right = image_right
    canvas_right.configure(image = image_right)

    console.insert(tk.END, f'Stereo correlation - Finished\n\n')
    console.insert(tk.END, '##################################################################################################################\n\n')
    console.see('insert')

    end = time.time()

    stereotime = end - start

    time_stereo = second2dhms(stereotime)
    time_start = time.strftime('%m/%d/%y - %H:%M:%S', time.localtime(start_process))

    console_process.delete('1.0', END)
    console_process.insert(tk.END, f'       Process {1} of {Images} \n\n')

    console_process.insert(tk.END, f'Start ... {time_start}\n')
    console_process.insert(tk.END, f'Current ....... {time_stereo}\n')
    console_process.insert(tk.END, f'Remaining ....... Calculating\n\n')

    console_process.insert(tk.END, f'End ............. Calculating\n')
    console.see('insert')

    green_length = int(933*((1)/Images))
    progression.coords(progression_bar, 0, 0, green_length, 25); progression.itemconfig(canvas_text, text=f'{1} de {Images} - {100*(1)/Images:.2f}%')

    time_total = []

    # Number of processors for each process:
    if Cores.get() == 2:

        CoresTemp = int(Cores.get()/2)

        i0_list = [0]
        i1_list = [Ny.get()+1]

        j0_list = [0]
        j1_list = [Nx.get()+1]

    else:
        CoresTemp = int(Cores.get()/2)

        cores_x = int(CoresTemp / 2 + 1)
        cores_y = int(CoresTemp / (cores_x - 1) + 1)

        ii = np.linspace(0, Ny.get() + 1, num=cores_y, dtype="int")
        i1 = ii[1:]
        i0 = ii[0:cores_y - 1];
        i0[0] = 0

        jj = np.linspace(0, Nx.get() + 1, num=cores_x, dtype="int")
        j1 = jj[1:]
        j0 = jj[0:cores_x - 1];
        j0[0] = 0

        i0_list = np.repeat(i0, cores_x - 1)
        i1_list = np.repeat(i1, cores_x - 1)

        j0_list = np.tile(j0, cores_y - 1)
        j1_list = np.tile(j1, cores_y - 1)

    if_error = False
    temporal_Corr = False

    for k in range(1, Images):

        temporal_Corr = True

        start = time.time()

        if abort_param.get():
            process_btn.configure(text='Start',fg ='#282C34', command=lambda: initialize(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
           Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
           Filtering, Kernel, ResultsName, process_btn, abort_param, progression, progression_bar, canvas_left, canvas_right,
           canvas_text, console_process, method_corr_dict,Cores))
            console.insert(tk.END, '\nCorrelation process aborted . . .\n\n')
            console.see('insert')
            abort_param.set(False)
            return
        else:

            console.insert(tk.END, f'Temporal correlation of pair number {k} of {Images} ')
            console.see('insert')

            I0L = cv.cvtColor(cv.imread(fileNamesSelectionLeft[k-1]), cv.COLOR_BGR2GRAY)
            I1L = cv.cvtColor(cv.imread(fileNamesSelectionLeft[k]), cv.COLOR_BGR2GRAY)

            I0R = cv.cvtColor(cv.imread(fileNamesSelectionRight[k - 1]), cv.COLOR_BGR2GRAY)
            I1R = cv.cvtColor(cv.imread(fileNamesSelectionRight[k]), cv.COLOR_BGR2GRAY)

            IunL = cv.resize(I0L, (int(I0L.shape[1] * Opi.get()), int(I0L.shape[0] * Opi.get())),
                             interpolation=cv.INTER_CUBIC)
            IdL = cv.resize(I1L, (int(I1L.shape[1] * Opi.get()), int(I1L.shape[0] * Opi.get())),
                            interpolation=cv.INTER_CUBIC)
            IunR = cv.resize(I0R, (int(I0R.shape[1] * Opi.get()), int(I0R.shape[0] * Opi.get())),
                             interpolation=cv.INTER_CUBIC)
            IdR = cv.resize(I1R, (int(I1R.shape[1] * Opi.get()), int(I1R.shape[0] * Opi.get())),
                            interpolation=cv.INTER_CUBIC)

            if Interpolation.get() == 'Before':
                if Correlation.get() == 'Incremental':
                    process_list = []
                    for i in range(CoresTemp):
                        process_list.append(mp.Process(target=Corr2D_Temporal_L_V1, args=(k-1, k, SubIrTemporal, SubIbTemporal,
                                                                                      xriL_mem, xriL.shape,
                                                                                      yriL_mem, yriL.shape,
                                                                                      uriL_mem, uriL.shape,
                                                                                      vriL_mem, vriL.shape,
                                                                                      IunL, IdL,
                                                                                      Version.get(),
                                                                                      matchTemplate_method,
                                                                                      Criterion.get(), i0_list[i],
                                                                                      i1_list[i], j0_list[i],
                                                                                      j1_list[i])))
                        process_list.append(mp.Process(target=Corr2D_Temporal_R_V1, args=(k-1, k, SubIrTemporal, SubIbTemporal,
                                                                                      xriR_mem, xriR.shape,
                                                                                      yriR_mem, yriR.shape,
                                                                                      uriR_mem, uriR.shape,
                                                                                      vriR_mem, vriR.shape,
                                                                                      IunR, IdR,
                                                                                      Version.get(),
                                                                                      matchTemplate_method,
                                                                                      Criterion.get(), i0_list[i],
                                                                                      i1_list[i], j0_list[i],
                                                                                      j1_list[i])))
                    try:
                        for i in range(Cores.get()):
                            process_list[i].start()
                    except:
                        messagebox.showerror('Error RAM',
                                             'The correlation runs out of memory RAM! Please reduce the number of designated processors or reduce the kb interpolation factor.')

                        menu.destroy()
                        menu.quit()

                    for i in range(Cores.get()):
                        process_list[i].join()

                else:
                    process_list = []
                    for i in range(CoresTemp):
                        process_list.append(
                            mp.Process(target=Corr2D_Temporal_L_V1, args=(0, k, SubIrTemporal, SubIbTemporal,
                                                                          xriL_mem, xriL.shape,
                                                                          yriL_mem, yriL.shape,
                                                                          uriL_mem, uriL.shape,
                                                                          vriL_mem, vriL.shape,
                                                                          IrefL, IdL,
                                                                          Version.get(),
                                                                          matchTemplate_method,
                                                                          Criterion.get(), i0_list[i],
                                                                          i1_list[i], j0_list[i],
                                                                          j1_list[i])))
                        process_list.append(
                            mp.Process(target=Corr2D_Temporal_R_V1, args=(0, k, SubIrTemporal, SubIbTemporal,
                                                                          xriR_mem, xriR.shape,
                                                                          yriR_mem, yriR.shape,
                                                                          uriR_mem, uriR.shape,
                                                                          vriR_mem, vriR.shape,
                                                                          IrefR, IdR,
                                                                          Version.get(),
                                                                          matchTemplate_method,
                                                                          Criterion.get(), i0_list[i],
                                                                          i1_list[i], j0_list[i],
                                                                          j1_list[i])))
                    try:
                        for i in range(Cores.get()):
                            process_list[i].start()
                    except:
                        messagebox.showerror('Error RAM',
                                             'The correlation runs out of memory RAM! Please reduce the number of designated processors or reduce the kb interpolation factor.')

                        menu.destroy()
                        menu.quit()

                    for i in range(Cores.get()):
                        process_list[i].join()
            else:
                if Correlation.get() == 'Incremental':
                    process_list = []
                    for i in range(CoresTemp):
                        process_list.append(
                            mp.Process(target=Corr2D_Temporal_L_V2, args=(k - 1, k, SubIrTemporal, SubIbTemporal, OpiSub.get(),
                                                                          xriL_mem, xriL.shape,
                                                                          yriL_mem, yriL.shape,
                                                                          uriL_mem, uriL.shape,
                                                                          vriL_mem, vriL.shape,
                                                                          IunL, IdL,
                                                                          Version.get(),
                                                                          matchTemplate_method,
                                                                          Criterion.get(), i0_list[i],
                                                                          i1_list[i], j0_list[i],
                                                                          j1_list[i])))
                        process_list.append(
                            mp.Process(target=Corr2D_Temporal_R_V2, args=(k - 1, k, SubIrTemporal, SubIbTemporal, OpiSub.get(),
                                                                          xriR_mem, xriR.shape,
                                                                          yriR_mem, yriR.shape,
                                                                          uriR_mem, uriR.shape,
                                                                          vriR_mem, vriR.shape,
                                                                          IunR, IdR,
                                                                          Version.get(),
                                                                          matchTemplate_method,
                                                                          Criterion.get(), i0_list[i],
                                                                          i1_list[i], j0_list[i],
                                                                          j1_list[i])))
                    try:
                        for i in range(Cores.get()):
                            process_list[i].start()
                    except:
                        messagebox.showerror('Error RAM',
                                            'The correlation runs out of memory RAM! Please reduce the number of designated processors or reduce the kb interpolation factor.')

                        menu.destroy()
                        menu.quit()

                    for i in range(Cores.get()):
                        process_list[i].join()

                else:
                    process_list = []
                    for i in range(CoresTemp):
                        process_list.append(
                            mp.Process(target=Corr2D_Temporal_L_V2, args=(0, k, SubIrTemporal, SubIbTemporal,  OpiSub.get(),
                                                                          xriL_mem, xriL.shape,
                                                                          yriL_mem, yriL.shape,
                                                                          uriL_mem, uriL.shape,
                                                                          vriL_mem, vriL.shape,
                                                                          IrefL, IdL,
                                                                          Version.get(),
                                                                          matchTemplate_method,
                                                                          Criterion.get(), i0_list[i],
                                                                          i1_list[i], j0_list[i],
                                                                          j1_list[i])))
                        process_list.append(
                            mp.Process(target=Corr2D_Temporal_R_V2, args=(0, k, SubIrTemporal, SubIbTemporal,  OpiSub.get(),
                                                                          xriR_mem, xriR.shape,
                                                                          yriR_mem, yriR.shape,
                                                                          uriR_mem, uriR.shape,
                                                                          vriR_mem, vriR.shape,
                                                                          IrefR, IdR,
                                                                          Version.get(),
                                                                          matchTemplate_method,
                                                                          Criterion.get(), i0_list[i],
                                                                          i1_list[i], j0_list[i],
                                                                          j1_list[i])))
                    try:
                        for i in range(Cores.get()):
                            process_list[i].start()
                    except:
                        messagebox.showerror('Error RAM',
                                             'The correlation runs out of memory RAM! Please reduce the number of designated processors or reduce the kb interpolation factor.')

                        menu.destroy()
                        menu.quit()

                    for i in range(Cores.get()):
                        process_list[i].join()

            console.insert(tk.END, '- Done\n')
            console.insert(tk.END, f'3D reconstruction of pair number {k} ')
            console.see('insert')

            xmL = xriL[k][:][:].copy() / Opi.get();
            ymL = yriL[k][:][:].copy() / Opi.get()
            xmR = xriR[k][:][:].copy() / Opi.get();
            ymR = yriR[k][:][:].copy() / Opi.get()
            umL = uriL[k][:][:].copy() / Opi.get();
            vmL = vriL[k][:][:].copy() / Opi.get()
            umR = uriR[k][:][:].copy() / Opi.get();
            vmR = vriR[k][:][:].copy() / Opi.get()

            if Version.get() == 'Lagrangian':

                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get() + 1):
                        if np.isnan(Xw[0][i][j]):
                            Xw[k][i][j] = float('nan');
                            Yw[k][i][j] = float('nan');
                            Zw[k][i][j] = float('nan');
                            Uw[k][i][j] = float('nan');
                            Vw[k][i][j] = float('nan');
                            Ww[k][i][j] = float('nan');
                            Xcp[k][i][j] = float('nan');
                            Ycp[k][i][j] = float('nan');
                            Zcp[k][i][j] = float('nan');
                            Ucp[k][i][j] = float('nan');
                            Vcp[k][i][j] = float('nan');
                            Wcp[k][i][j] = float('nan');
                        else:

                            Xw[k][i][j], Yw[k][i][j], Zw[k][i][j] = ReconstructionWCS(xmL[i][j], ymL[i][j], xmR[i][j], ymR[i][j], calib)

                            Xcp[k][i][j] = np.matmul(RINV[0][:], [Xw[k][i][j] - T[0], Yw[k][i][j] - T[1], Zw[k][i][j] - T[2]]);
                            Ycp[k][i][j] = np.matmul(RINV[1][:], [Xw[k][i][j] - T[0], Yw[k][i][j] - T[1], Zw[k][i][j] - T[2]]);
                            Zcp[k][i][j] = np.matmul(RINV[2][:], [Xw[k][i][j] - T[0], Yw[k][i][j] - T[1], Zw[k][i][j] - T[2]]);

                            if Correlation.get() == 'Incremental':

                                Uw[k][i][j] = Xw[k][i][j] - Xw[k - 1][i][j];
                                Vw[k][i][j] = Yw[k][i][j] - Yw[k - 1][i][j];
                                Ww[k][i][j] = Zw[k][i][j] - Zw[k - 1][i][j];

                                Ucp[k][i][j] = Xcp[k][i][j] - Xcp[k - 1][i][j];
                                Vcp[k][i][j] = Ycp[k][i][j] - Ycp[k - 1][i][j];
                                Wcp[k][i][j] = Zcp[k][i][j] - Zcp[k - 1][i][j];
                            else:
                                Uw[k][i][j] = Xw[k][i][j] - Xw[0][i][j];
                                Vw[k][i][j] = Yw[k][i][j] - Yw[0][i][j];
                                Ww[k][i][j] = Zw[k][i][j] - Zw[0][i][j];

                                Ucp[k][i][j] = Xcp[k][i][j] - Xcp[0][i][j];
                                Vcp[k][i][j] = Ycp[k][i][j] - Ycp[0][i][j];
                                Wcp[k][i][j] = Zcp[k][i][j] - Zcp[0][i][j];

            else:

                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get() + 1):
                        if np.isnan(Xw[0][i][j]):
                            Xw[k][i][j] = float('nan');
                            Yw[k][i][j] = float('nan');
                            Zw[k][i][j] = float('nan');
                            Uw[k][i][j] = float('nan');
                            Vw[k][i][j] = float('nan');
                            Ww[k][i][j] = float('nan');
                            Xcp[k][i][j] = float('nan');
                            Ycp[k][i][j] = float('nan');
                            Zcp[k][i][j] = float('nan');
                            Ucp[k][i][j] = float('nan');
                            Vcp[k][i][j] = float('nan');
                            Wcp[k][i][j] = float('nan');
                        else:
                            Xw[k][i][j], Yw[k][i][j], Zw[k][i][j] = ReconstructionWCS(xmL[i][j] + umL[i][j],
                                                                                      ymL[i][j] + vmL[i][j],
                                                                                      xmR[i][j] + umR[i][j],
                                                                                      ymR[i][j] + vmR[i][j], calib)

                            Xcp[k][i][j] = np.matmul(RINV[0][:], [Xw[k][i][j] - T[0], Yw[k][i][j] - T[1], Zw[k][i][j] - T[2]]);
                            Ycp[k][i][j] = np.matmul(RINV[1][:], [Xw[k][i][j] - T[0], Yw[k][i][j] - T[1], Zw[k][i][j] - T[2]]);
                            Zcp[k][i][j] = np.matmul(RINV[2][:], [Xw[k][i][j] - T[0], Yw[k][i][j] - T[1], Zw[k][i][j] - T[2]]);

                            if Correlation.get() == 'Incremental':

                                Uw[k][i][j] = Xw[k][i][j] - Xw[k - 1][i][j];
                                Vw[k][i][j] = Yw[k][i][j] - Yw[k - 1][i][j];
                                Ww[k][i][j] = Zw[k][i][j] - Zw[k - 1][i][j];

                                Ucp[k][i][j] = Xcp[k][i][j] - Xcp[k - 1][i][j];
                                Vcp[k][i][j] = Ycp[k][i][j] - Ycp[k - 1][i][j];
                                Wcp[k][i][j] = Zcp[k][i][j] - Zcp[k - 1][i][j];

                            else:

                                Uw[k][i][j] = Xw[k][i][j] - Xw[0][i][j];
                                Vw[k][i][j] = Yw[k][i][j] - Yw[0][i][j];
                                Ww[k][i][j] = Zw[k][i][j] - Zw[0][i][j];

                                Ucp[k][i][j] = Xcp[k][i][j] - Xcp[0][i][j];
                                Vcp[k][i][j] = Ycp[k][i][j] - Ycp[0][i][j];
                                Wcp[k][i][j] = Zcp[k][i][j] - Zcp[0][i][j];

                            Xw[k][i][j] = Xw[0][i][j];
                            Yw[k][i][j] = Yw[0][i][j];
                            Zw[k][i][j] = Zw[0][i][j];

                            Xcp[k][i][j] = Xcp[0][i][j];
                            Ycp[k][i][j] = Ycp[0][i][j];
                            Zcp[k][i][j] = Zcp[0][i][j];

            console.insert(tk.END, '- Done\n')
            console.insert(tk.END, 'Saving files ')
            console.see('insert')

            xmWCS = Xw[k][:][:].copy()
            ymWCS = Yw[k][:][:].copy()
            zmWCS = Zw[k][:][:].copy()
            xmSPCS = Xcp[k][:][:].copy()
            ymSPCS = Ycp[k][:][:].copy()
            zmSPCS = Zcp[k][:][:].copy()

            # Displacement filtering:
            if Filtering.get() == 'Gaussian':

                # Gaussian smoothing:
                umWCS = cv.GaussianBlur(Uw[k][:][:].copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)
                vmWCS = cv.GaussianBlur(Vw[k][:][:].copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)
                wmWCS = cv.GaussianBlur(Ww[k][:][:].copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)
                umSPCS = cv.GaussianBlur(Ucp[k][:][:].copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)
                vmSPCS = cv.GaussianBlur(Vcp[k][:][:].copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)
                wmSPCS = cv.GaussianBlur(Wcp[k][:][:].copy(), (Kernel.get(), Kernel.get()), cv.BORDER_DEFAULT)

                # Determination of valid mask area:
                valid_mask_gaussian = np.isnan(umWCS)

                # Add nan values according to displacement data:
                for i in range(0, Ny.get() + 1):
                    for j in range(0, Nx.get() + 1):
                        if valid_mask_gaussian[i][j]:
                            xmWCS[i][j] = 'nan'
                            ymWCS[i][j] = 'nan'
                            zmWCS[i][j] = 'nan'
                            xmSPCS[i][j] = 'nan'
                            ymSPCS[i][j] = 'nan'
                            zmSPCS[i][j] = 'nan'
                            xmL[i][j] = 'nan'
                            ymL[i][j] = 'nan'
                            xmR[i][j] = 'nan'
                            ymR[i][j] = 'nan'

                del valid_mask_gaussian

            else:
                umWCS = Uw[k][:][:].copy()
                vmWCS = Vw[k][:][:].copy()
                wmWCS = Ww[k][:][:].copy()
                umSPCS = Ucp[k][:][:].copy()
                vmSPCS = Vcp[k][:][:].copy()
                wmSPCS = Wcp[k][:][:].copy()
                xmWCS = Xw[k][:][:].copy()
                ymWCS = Yw[k][:][:].copy()
                zmWCS = Zw[k][:][:].copy()
                xmSPCS = Xcp[k][:][:].copy()
                ymSPCS = Ycp[k][:][:].copy()
                zmSPCS = Zcp[k][:][:].copy()

            np.savetxt(f'{resultsPath}/{filexL.format(k + 1)}', xmL, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{fileyL.format(k + 1)}', ymL, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filexR.format(k + 1)}', xmR, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{fileyR.format(k + 1)}', ymR, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filexWCS.format(k+1)}', xmWCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{fileyWCS.format(k+1)}', ymWCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filezWCS.format(k+1)}', zmWCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{fileuWCS.format(k+1)}', umWCS,  fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filevWCS.format(k+1)}', vmWCS,  fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filewWCS.format(k+1)}', wmWCS,  fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filexSPCS.format(k + 1)}', xmSPCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{fileySPCS.format(k + 1)}', ymSPCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filezSPCS.format(k + 1)}', zmSPCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{fileuSPCS.format(k + 1)}', umSPCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filevSPCS.format(k + 1)}', vmSPCS, fmt='%.10e')
            np.savetxt(f'{resultsPath}/{filewSPCS.format(k + 1)}', wmSPCS, fmt='%.10e')

            del xmL, ymL, xmR, ymR, xmWCS, ymWCS, zmWCS, umWCS, vmWCS, wmWCS, xmSPCS, ymSPCS, zmSPCS, umSPCS, vmSPCS, wmSPCS

            # Left mesh update figure:
            figL = plt.figure()
            ax = figL.gca()
            dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
            dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])

            if ratio_plot <= 1.33333333:

                dxplotdark = dyplot*1.33333333
                dyplotdark = dyplot
                ax.imshow(cv.imread(fileNamesSelectionLeft[k]), zorder=2)
                ax.plot(np.transpose(xriL[k][:][:]/Opi.get()), np.transpose(yriL[k][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
                ax.plot(xriL[k][:][:]/Opi.get(), yriL[k][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
                ax.plot([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0],'black', zorder=1)
                ax.fill_between([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
                ax.axis('off')
                plt.xlim(-dxplotdark/2+dxplot/2,dxplotdark-dxplotdark/2+dxplot/2)
                plt.ylim(0,dyplotdark)
                plt.subplots_adjust(0,0,1,1,0,0)

            else:
                dxplotdark = dxplot
                dyplotdark = dxplot/1.33333333
                ax.imshow(cv.imread(fileNamesSelectionLeft[k]), zorder=2)
                ax.plot(np.transpose(xriL[k][:][:]/Opi.get()), np.transpose(yriL[k][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
                ax.plot(xriL[k][:][:]/Opi.get(), yriL[k][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
                ax.plot([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2],'black', zorder=1)
                ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2], color='black', zorder=1)
                ax.axis('off')
                plt.xlim(0,dxplotdark)
                plt.ylim(-dyplotdark/2+dyplot/2,dyplotdark-dyplotdark/2+dyplot/2)
                plt.subplots_adjust(0,0,1,1,0,0)

            figL.canvas.draw()

            imageL = np.frombuffer(figL.canvas.tostring_rgb(), dtype=np.uint8)
            wL, hL = figL.canvas.get_width_height()
            imageL = np.flip(imageL.reshape((hL, wL, 3)),axis=0)

            plt.cla()
            plt.clf()

            # Right mesh update figure:
            figR = plt.figure()
            ax = figR.gca()
            dxplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[1])
            dyplot = int(cv.imread(fileNamesSelectionLeft[0]).shape[0])
            if ratio_plot <= 1.33333333:

                dxplotdark = dyplot*1.33333333
                dyplotdark = dyplot
                ax.imshow(cv.imread(fileNamesSelectionRight[k]), zorder=2)
                ax.plot(np.transpose(xriR[k][:][:]/Opi.get()), np.transpose(yriR[k][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
                ax.plot(xriR[k][:][:]/Opi.get(), yriR[k][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
                ax.plot([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0],'black', zorder=1)
                ax.fill_between([0-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, dxplotdark-dxplotdark/2+dxplot/2, 0-dxplotdark/2+dxplot/2],[0, dyplotdark, dyplotdark, 0, 0], color='black', zorder=1)
                ax.axis('off')
                plt.xlim(-dxplotdark/2+dxplot/2,dxplotdark-dxplotdark/2+dxplot/2)
                plt.ylim(0,dyplotdark)
                plt.subplots_adjust(0,0,1,1,0,0)

            else:
                dxplotdark = dxplot
                dyplotdark = dxplot/1.33333333
                ax.imshow(cv.imread(fileNamesSelectionRight[k]), zorder=2)
                ax.plot(np.transpose(xriR[k][:][:]/Opi.get()), np.transpose(yriR[k][:][:]/Opi.get()), color= 'red', linewidth=1, zorder=3)
                ax.plot(xriR[k][:][:]/Opi.get(), yriR[k][:][:]/Opi.get(), color= 'red', linewidth=1, zorder=3)
                ax.plot([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2],'black', zorder=1)
                ax.fill_between([0, 0, dxplotdark, dxplotdark, 0],[0-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, +dyplotdark-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2, 0-dyplotdark/2+dyplot/2], color='black', zorder=1)
                ax.axis('off')
                plt.xlim(0,dxplotdark)
                plt.ylim(-dyplotdark/2+dyplot/2,dyplotdark-dyplotdark/2+dyplot/2)
                plt.subplots_adjust(0,0,1,1,0,0)

            figR.canvas.draw()

            imageR = np.frombuffer(figR.canvas.tostring_rgb(), dtype=np.uint8)
            wR, hR = figR.canvas.get_width_height()
            imageR = np.flip(imageR.reshape((hR, wR, 3)),axis=0)

            plt.cla()
            plt.clf()

            image_left = cv.resize(imageL, (426, 320))
            cv.putText(image_left,f'MASTER L - {k+1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
            image_left = ImageTk.PhotoImage (Image.fromarray (image_left))

            canvas_left.image_left = image_left
            canvas_left.configure(image = image_left)

            image_right = cv.resize(imageR, (426, 320))
            cv.putText(image_right,f'SLAVE R - {k+1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
            image_right = ImageTk.PhotoImage (Image.fromarray (image_right))

            canvas_right.image_right = image_right
            canvas_right.configure(image = image_right)

            green_length = int(933*((k+1)/Images))
            progression.coords(progression_bar, 0, 0, green_length, 25); progression.itemconfig(canvas_text, text=f'{k+1} of {Images} - {100*(k+1)/Images:.2f}%')

            plt.close('all')

            console.insert(tk.END, '- Done\n\n')

            console.insert(tk.END, '##################################################################################################################\n\n')

            end = time.time()
            time_iter[k] = end-start
            time_total = time_total + time_iter[k]

            time_current = second2dhms(time_iter[k])
            time_remaining = second2dhms((Images-k-1)*time_iter[1])
            time_start = time.strftime('%m/%d/%y - %H:%M:%S', time.localtime(start_process))
            time_end = time.strftime('%m/%d/%y - %H:%M:%S', time.localtime(start_process+stereotime+(Images-1)*time_iter[1]))

            console_process.delete('1.0', END)
            console_process.insert(tk.END, f'       Process {k+1} of {Images} \n\n')

            console_process.insert(tk.END, f'Start ... {time_start}\n')
            console_process.insert(tk.END, f'Current ....... {time_current}\n')
            console_process.insert(tk.END, f'Remaining ..... {time_remaining}\n\n')

            console_process.insert(tk.END, f'End ..... {time_end}\n')
            console.see('insert')

    if temporal_Corr:
        if if_error:
            console.insert(tk.END, 'Temporal correlation - Finished with errors\n')
            console.insert(tk.END,
                           f'The correlation process was aborted in {str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))}\n\n')
            console.see('insert')
        else:
            console.insert(tk.END, 'Temporal correlation - Finished\n')
            console.insert(tk.END, f'The correlation process was successfully completed in {str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))}\n\n')
            console.see('insert')

    process_btn.configure(text='Start',fg ='#282C34', command=lambda: initialize(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny,
           Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation,
           Filtering, Kernel, ResultsName, process_btn, abort_param, progression, progression_bar, canvas_left, canvas_right,
           canvas_text, console_process, method_corr_dict,Cores))

    abort_param.set(False)

    messagebox.showinfo('Finished','The correlation process has been successfully completed! Use the iCorrVision Post-processing Module for visualization!')