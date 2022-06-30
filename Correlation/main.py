########################################################################################################################
# iCorrVision-3D Correlation Module GUI                                                                                #
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
    iCorrVision-3D Correlation Module GUI
    Copyright (C) 2022 iCorrVision team

    This file is part of the iCorrVision-3D software.

    The iCorrVision-3D Correlation Module GUI is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The iCorrVision-3D Correlation Module GUI is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

V = 'v1.04.22' # Version

import multiprocessing as mp
import os
########################################################################################################################
# Modules
########################################################################################################################
import tkinter as tk
import tkinter.scrolledtext as st
from threading import Thread
from tkinter import *
from tkinter import ttk

import numpy as np
from PIL import Image, ImageTk

import modules as module

########################################################################################################################
# Graphical interface - tkinter
########################################################################################################################
if __name__ == '__main__':

    # Pyinstaller fix
    mp.freeze_support()

    # Current directory:
    CurrentDir = os.path.dirname(os.path.realpath(__file__))

    # GUI interface:
    menu = tk.Tk()

    # GUI title:
    menu.title('iCorrVision-3D Correlation Module ' + V)

    # Logo:
    LOGO_DIC3D_Win = os.path.join('static', 'DIC3D.ico')
    LOGO_DIC3D_linux = os.path.join('@static', 'DIC3D.xbm')

    # Win and Linux:
    if os.name=="nt":
        menu.wm_iconbitmap(LOGO_DIC3D_Win)
    else:
        menu.wm_iconbitmap(LOGO_DIC3D_linux)

    # GUI style:
    s = ttk.Style()
    s.theme_use('alt')
    s.configure(style='TCombobox', fieldbackground='#ccd9e1')
    s.configure(style='TSpinbox', fieldbackground='#ccd9e1', arrowsize=13)

    # Global variables:
    global ResultsName; ResultsName = StringVar(menu); ResultsName.set('Results_Correlation')
    global abort_param; abort_param = BooleanVar(menu); abort_param.set(False)
    global file_var; file_var = BooleanVar(menu); file_var.set(False)
    global file_var_ROI; file_var_ROI = BooleanVar(menu); file_var_ROI.set(False)
    global file; file = StringVar(menu); file.set('')
    global file_ROI; file_ROI = StringVar(menu); file_ROI.set('')
    global capturedFolder; capturedFolder = StringVar(menu)
    global calibFile; calibFile = StringVar(menu)
    global SubIrS; SubIrS = IntVar(menu)
    global SubIbS; SubIbS = IntVar(menu)
    global SubIrT; SubIrT = IntVar(menu)
    global SubIbT; SubIbT = IntVar(menu)
    global Nx; Nx = IntVar(menu)
    global Ny; Ny = IntVar(menu)
    global Opi; Opi = IntVar(menu)
    global Adjust; Adjust = DoubleVar(menu)
    global NumCut; NumCut = IntVar(menu)
    global TypeCut; TypeCut = StringVar(menu)
    global Version; Version = StringVar(menu)
    global Interpolation; Interpolation = StringVar(menu);
    global OpiSub; OpiSub = IntVar(menu)
    global Filtering; Filtering = StringVar(menu);
    global Method; Method = StringVar(menu);
    global Criterion; Criterion = DoubleVar(menu);
    global Kernel; Kernel = IntVar(menu);
    global Correlation; Correlation = StringVar(menu);
    global Step; Step = IntVar(menu);
    global Cores; Cores = IntVar(menu);

    # GUI size:
    app_width = 1419
    app_height = 665

    # Screen configuration:
    screen_width = menu.winfo_screenwidth()
    screen_height = menu.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)

    menu.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

    menu.configure(background='#99b3c3')
    menu.resizable(width=False, height=False)

    canvas_window = Canvas(menu, bg='#99b3c3', height=app_height - 4, width=app_width - 4)
    canvas_window.place(x=0, y=0)

    selectionFolder = StringVar(menu)
    saveFolder = StringVar(menu)

    # Grid configuration:
    xinit = 20; yinit = 20; dyinit = 50; dxinit = 168

    # iCorrVision-3D Correlation logo:
    image_logo = Image.open(os.path.join(CurrentDir, 'static', 'iCorrVision-3D Correlation.png'))
    image_logo = image_logo.resize((int(756/4), int(144/4)), Image.ANTIALIAS)
    image_logo_re = ImageTk.PhotoImage(image_logo)

    canvas_logo = tk.Label(menu, width=200, height=50, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                           image=image_logo_re);
    canvas_logo.place(x=xinit + 5, y=yinit + 10)

    # Interface to select the captured images folder (must contain Left and Right folders):
    captured_btn = tk.Button(menu, text='Captured images', width=19, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.captured_folder(capturedFolder, captured_status, console, canvas_left, 
        canvas_right))
    captured_btn.place(x=xinit, y=yinit + dyinit * 2)
    captured_status = Entry(menu, bg='red') # Default status is red
    captured_status.place(x=xinit + 142, y=yinit + dyinit * 2 - 1, width=8, height=27)

    # Open user guide pdf:
    tk.Button(menu, text='User guide', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
              fg='#282C34', command=lambda: module.openguide(CurrentDir)).place(x=xinit + dxinit + 181, y=yinit + dyinit -20, width=135, height=25)

    # Interface to select the calibration file generated by iCorrVision-3D Calibration Module:
    calib_btn = tk.Button(menu, text='Calibration file', width=19, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.calib_file(console, calibFile, calib_status))
    calib_btn.place(x=xinit, y=yinit + dyinit*3)
    calib_status = Entry(menu, bg='red') # Default status is red
    calib_status.place(x=xinit + 142, y=yinit + dyinit*3 - 1, width=8, height=27)

    # Interface to select the number of processors (cores):
    Label(menu, text='Number of processors:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + 
        dxinit + 181, y=yinit + dyinit * 2-23)
    spinbox = ttk.Spinbox(menu, from_= 2, to= mp.cpu_count(), increment=2,textvariable=Cores, font=('Heveltica', 10),style='TSpinbox')
    spinbox.place(x=xinit + dxinit + 181, y=yinit + dyinit * 2, width=135, height=26)
    spinbox.set(mp.cpu_count())

    # Output folder name. Default name -> Results_Correlation
    Label(menu, text='Output folder name:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x = xinit + dxinit - 1, y = yinit + dyinit * 2 - 23)
    Entry(menu, textvariable=ResultsName, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit,
        y = yinit + dyinit * 2, width = 165,  height = 25)

    # Reference subset size for stereo correlation (RSS S) [pixels]:
    canvas_window.create_line(xinit, yinit + dyinit * 4+23/2, xinit + dxinit*0.69-3, yinit + dyinit * 4+23/2)
    Label(menu, text='RSS S:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit, 
        y=yinit + dyinit * 4 - 23)
    Entry(menu, textvariable=SubIrS, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit,
        y=yinit + dyinit * 4, width=66, height=25)

    # Search subset size for stereo correlation (SSS S) [pixels]:
    Label(menu, text='SSS S:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit * 0.5 - 1, y=yinit + dyinit * 4 - 23)
    Entry(menu, textvariable=SubIbS, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit * 0.5,
        y=yinit + dyinit * 4, width=66, height=25)

    # Subset step (ST) [pixels]:
    Label(menu, text='ST:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit - 1, y=yinit + dyinit * 4 - 23)
    Entry(menu, textvariable=Step, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit,
        y=yinit + dyinit * 4, width=38, height=25)

    # Interpolation strategy:
    Label(menu, text='Interpolation:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit + 55 - 1, y=yinit + dyinit * 4 - 23)
    type_interp = ttk.Combobox(menu, textvariable=Interpolation, font=('Heveltica', 10))
    type_interp['values'] = ('Select', 'Before', 'After', 'Both')
    type_interp.place(x=xinit + dxinit + 55, y=yinit + dyinit * 4, width=94, height=25)
    type_interp.current(0)

    # Interpolation strategy - kb factor:
    Label(menu, text='Before', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + dxinit + 164 - 1, y=yinit + dyinit * 4 - 23)
    Label(menu, text='kb:', bg='#99b3c3', fg='#282C34', font=('Times', 10, 'italic')).place(x=xinit + dxinit+ 164+40 - 1, y=yinit + dyinit * 4 - 23+1)
    Entry(menu, textvariable=Opi, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit + 164,
        y=yinit + dyinit * 4, width=68, height=25)

    # Interpolation strategy - ka factor:
    Label(menu, text='After', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + dxinit + 248 - 1, y=yinit + dyinit * 4 - 23)
    Label(menu, text='ka:', bg='#99b3c3', fg='#282C34', font=('Times', 10, 'italic')).place(x=xinit + dxinit+ 248+30 - 1, y=yinit + dyinit * 4 - 23+1)
    cbb_subpixels = ttk.Combobox(menu, textvariable=OpiSub, font=('Heveltica', 10))
    cbb_subpixels['values'] = ('1', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100')
    cbb_subpixels.place(x=xinit + dxinit + 248, y=yinit + dyinit * 4, width=68, height=25)
    cbb_subpixels.current('0')

    # Reference subset size for temporal correlation (RSS T) [pixels]:
    canvas_window.create_line(xinit, yinit + dyinit * 5+23/2, xinit + dxinit*0.69-3, yinit + dyinit * 5+23/2)
    Label(menu, text='RSS T:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit - 1,
        y=yinit + dyinit * 5 - 23)
    Entry(menu, textvariable=SubIrT, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit,
        y=yinit + dyinit * 5, width=66, height=25)

    # Search subset size for temporal correlation (SSS T) [pixels]:
    Label(menu, text='SSS T:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit * 0.5- 1, y=yinit + dyinit * 5 - 23)
    Entry(menu, textvariable=SubIbT, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit * 0.5,
        y=yinit + dyinit * 5, width=66, height=25)

    # Number of elements in x direction:
    Label(menu, text='Nx:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit - 1, y=yinit + dyinit * 5 - 23)
    Entry(menu, textvariable=Nx, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit,
        y=yinit + dyinit * 5, width=58, height=25)

    # Number of elements in y direction:
    Label(menu, text='Ny:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + dxinit+76 - 1,
        y=yinit + dyinit * 5 - 23)
    Entry(menu, textvariable=Ny, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit +76, 
        y=yinit + dyinit * 5, width=58, height=25)

    # Displacement filtering:
    Label(menu, text='Filtering:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit + 151 - 1, y=yinit + dyinit * 5 - 23)
    type_filtering = ttk.Combobox(menu, textvariable=Filtering, font=('Heveltica', 10))
    type_filtering['values'] = ('Select', 'None', 'Gaussian')
    type_filtering.place(x=xinit + dxinit + 151, y=yinit + dyinit * 5, width=81, height=25)
    type_filtering.current(0)

    # Kernel size for displacement filtering (max is 5 pixels):
    Label(menu, text='Kernel:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + dxinit + 248 - 1,
        y=yinit + dyinit * 5 - 23)
    Entry(menu, textvariable=Kernel, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit + 248,
        y=yinit + dyinit * 5, width=68, height=25)

    # Contrast adjustment:
    Label(menu, text='Contrast:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit - 1,
        y=yinit + dyinit * 6 - 23)
    Entry(menu, textvariable=Adjust, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit, y=yinit + dyinit * 6,
        width=66, height=25)

    # Test the contrast adjustment:
    verify_btn = tk.Button(menu, text=' ', width=1, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.verify(Adjust, canvas_left, canvas_right, console))
    verify_btn.place(x=xinit + dxinit * 0.5 - 34, y=yinit + dyinit * 6)

    # Configuration (Eulerian or Lagrangian):
    Label(menu, text='Config.:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit - 1 + dxinit * 0.5,
        y=yinit + dyinit * 6 - 23)
    type_method = ttk.Combobox(menu, textvariable=Version, font=('Heveltica', 10))
    type_method['values'] = ('Select', 'Eulerian', 'Lagrangian')
    type_method.place(x=xinit + dxinit * 0.5, y=yinit + dyinit * 6, width=66, height=25)
    type_method.current(0)

    # Method - correlation function:
    Label(menu, text='Method:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit - 1,
        y=yinit + dyinit * 6 - 23)
    method_corr = ttk.Combobox(menu, textvariable=Method, font=('Heveltica', 10))
    method_corr['values'] = (
    'Select', 'TM_CCOEFF', 'TM_CCOEFF_NORMED', 'TM_CCORR', 'TM_CCORR_NORMED')
    method_corr.place(x=xinit + dxinit, y=yinit + dyinit * 6, width=135, height=25)
    method_corr.current(0)
    method_corr_dict = {'TM_CCOEFF': 0, 'TM_CCOEFF_NORMED': 1, 'TM_CCORR': 2, 'TM_CCORR_NORMED': 3}

    # Correlation strategy (Spatial or Incremental):
    Label(menu, text='Correlation:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit + 151 - 1, y=yinit + dyinit * 6 - 23)
    type_corr = ttk.Combobox(menu, textvariable=Correlation, font=('Heveltica', 10))
    type_corr['values'] = ('Select', 'Spatial', 'Incremental')
    type_corr.place(x=xinit + dxinit + 151, y=yinit + dyinit * 6, width=81, height=25)
    type_corr.current(0)

    # Correlation criterion (max is 1):
    Label(menu, text='Criterion:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + dxinit + 248 - 1,
        y=yinit + dyinit * 6 - 23)
    Entry(menu, textvariable=Criterion, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit + 248,
        y=yinit + dyinit * 6, width=68, height=25)

    # ROI construction and subsets generation:
    Label(menu, text='ROI CONSTRUCTION', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit + dxinit * 6 + 14, y=yinit + dyinit * 7 - 10)

    # Number of regions to cut out undesirable subsets:
    Label(menu, text='Cuts:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit - 1 + dxinit * 6 - 55, y=yinit + dyinit * 7 + 23)
    Entry(menu, textvariable=NumCut, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit * 6 - 55,
        y=yinit + 23 * 2 + dyinit * 7, width=77, height=25)

    # Selection button - crop captured images, ROI selection and subset construction: 
    selection_btn = tk.Button(menu, text='ROI', width=8, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: Thread(target=module.SelectionImage, 
        args=(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx,
        Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, progression, progression_bar, canvas_left,
        canvas_right, canvas_text, Method, Correlation, Criterion, Step, file_var_ROI, file_ROI,
        Interpolation, Filtering, Kernel,ResultsName)).start())
    selection_btn.place(x=xinit + dxinit * 6 + 98 - 55, y=yinit + 23 * 2 + dyinit * 7)

    # Load ROI log - crop captured images, ROI selection and subset construction:
    load_roi_btn = tk.Button(menu, text='Load ROI', width=8, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: Thread(target=module.SelectionLoad, 
        args=(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, SubIbS, SubIrT, SubIbT, Nx,
        Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, progression, progression_bar, canvas_left, canvas_right, 
        canvas_text, Method, Correlation, Criterion, Step, file_var_ROI, file_ROI, Interpolation, Filtering,
        Kernel,ResultsName)).start())
    load_roi_btn.place(x=xinit + dxinit * 6 + 186 - 55, y=yinit + 23 * 2 + dyinit * 7)

    # Type of cutting regions (Free, circular or rectangular):
    Label(menu, text='Type of cut:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(
        x=xinit - 1 + dxinit * 6 - 55, y=yinit + dyinit * 8 + 23)
    type_cut = ttk.Combobox(menu, textvariable=TypeCut, font=('Heveltica', 10), style = 'TCombobox')
    type_cut['values'] = ('None', 'Free', 'Rectangular', 'Circular inside', 'Circular outside')
    type_cut.bind('<ButtonPress>', module.combo_configure)
    type_cut.place(x=xinit + dxinit * 6 - 55, y=yinit + 23 * 2 + dyinit * 8, width=77, height=25)
    type_cut.current(0)

    # Save subset points:
    save_subset_btn = tk.Button(menu, text='Save points', width=8, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.SaveSubsets(console))
    save_subset_btn.place(x=xinit + dxinit * 6 + 98 - 55, y=yinit + 23 * 2 + dyinit * 8)

    # Load subset points:
    load_subset_btn = tk.Button(menu, text='Load points', width=8, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.LoadSubsets(
        console, canvas_left, canvas_right, capturedFolder, Nx, Ny, Interpolation, Opi, ResultsName, SubIrS, SubIbS))
    load_subset_btn.place(x=xinit + dxinit * 6 + 186 - 55, y=yinit + 23 * 2 + dyinit * 8)

    # Save DIC log:
    save_btn = tk.Button(menu, text='Save', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.save(menu, console, file_var, V, file, capturedFolder, calibFile, SubIrS, 
        SubIbS, SubIrT, SubIbT, Nx, Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion,
        Step, Interpolation, Filtering, Kernel))
    save_btn.place(x=xinit + dxinit * 7 + 53, y=yinit + 23 * 2 + dyinit * 6)

    # Save as DIC log:
    saveas_btn = tk.Button(menu, text='Save as', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.save_as(menu, console, file_var, V, file, capturedFolder, calibFile,
        SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation,
        Criterion, Step, Interpolation, Filtering, Kernel))
    saveas_btn.place(x=xinit + dxinit * 7 + 53, y=yinit + 23 * 2 + dyinit * 7)

    # Load DIC log:
    load_btn = tk.Button(menu, text='Load', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.load(menu, captured_status, console, canvas_left, canvas_right, file_var,
        V, file, capturedFolder, calibFile, calib_status, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny, Opi, OpiSub,
        Version, TypeCut, NumCut, Adjust, Method, Correlation, Criterion, Step, Interpolation, Filtering, Kernel))
    load_btn.place(x=xinit + dxinit * 7 + 53, y=yinit + 23 * 2 + dyinit * 8)

    # Clear GUI:
    clear_btn = tk.Button(menu, text='Clear', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.clear(menu, CurrentDir, captured_status, console, console_process,
        progression, progression_bar, canvas_left, canvas_right, canvas_text, file_var, V, file, capturedFolder,
        calibFile, calib_status, SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny, Opi, OpiSub, Version, TypeCut, NumCut,
        Adjust, Method, Correlation, Criterion, Step, Interpolation, Filtering, Kernel))
    clear_btn.place(x=xinit + dxinit * 7 + 53, y=yinit + 23 * 2 + dyinit * 9)

    # Start button:
    process_btn = tk.Button(menu, text='Start', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.initialize(menu, console, file_var, V, file, capturedFolder, calibFile,
        SubIrS, SubIbS, SubIrT, SubIbT, Nx, Ny, Opi, OpiSub, Version, TypeCut, NumCut, Adjust, Method, Correlation,
        Criterion, Step, Interpolation, Filtering, Kernel, ResultsName, process_btn, abort_param, progression,
        progression_bar, canvas_left, canvas_right, canvas_text, console_process, method_corr_dict, Cores))
    process_btn.place(x=xinit + dxinit * 7 + 53, y=yinit + 23 * 2 + dyinit * 10)

    # Close button:
    close_btn = tk.Button(menu, text='Close', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
        fg='#282C34', command=lambda: module.close(menu))
    close_btn.place(x=xinit + dxinit * 7 + 53, y=yinit + 23 * 2 + dyinit * 11)

    # Load and display the blank canvas:
    image_black = Image.open(os.path.join(CurrentDir,'static','ImageBlack.tiff'))
    image_black = image_black.resize((426, 320), Image.ANTIALIAS)
    image_black_re = ImageTk.PhotoImage(image_black)

    # Left canvas:
    canvas_left = tk.Label(menu, width=426, height=320, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                           image=image_black_re);
    canvas_left.place(x=xinit + 583 - 76, y=yinit + 2)

    # Right canvas:
    canvas_right = tk.Label(menu, width=426, height=320, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                            image=image_black_re);
    canvas_right.place(x=xinit + 1029 - 76, y=yinit + 2)

    # Progression bar:
    progression = Canvas(menu)
    progression.place(x=xinit, y=yinit + 23 * 2 + dyinit * 11, width=933, height=25)
    progression_bar = progression.create_rectangle(0, 0, 0, 25, fill='#00cd00')
    canvas_text = progression.create_text(np.round(933 / 2) - 10, 4, anchor=NW)
    progression.itemconfig(canvas_text, text='')

    # Console:
    console = st.ScrolledText(menu, bg='#ccd9e1')
    console.place(x=xinit, y=yinit + 23 * 2 + dyinit * 6, width=933, height=225)

    # Console to display the time consumption:
    console_process = st.ScrolledText(menu, bg='#ccd9e1')
    console_process.place(x=xinit + dxinit * 6 - 55, y=yinit + 23 * 2 + dyinit * 9, width=254, height=125)

    # Initial message:
    console.insert(tk.END,
        f'#######################################################################################################  {V}\n\n'
        '                                     **  iCorrVision-3D Correlation Module **                                     \n\n'
        '##################################################################################################################\n\n')

    console.insert(tk.END, 'Please load project or select the image captured folder, calibration file and DIC settings\n\n')
    console.see('insert')

    # Developer and supervisors list:
    Label(menu,
        text='Developer: João Carlos A. D. Filho, M.Sc. (joaocadf@id.uff.br) / Supervisors: Luiz C. S. Nunes, D.Sc. (luizcsn@id.uff.br) and José M. C. Xavier, P.hD. (jmc.xavier@fct.unl.pt)',
        bg='#99b3c3', fg='#282C34', font=('Heveltica', 8)).place(x=xinit - 1, y=yinit + dyinit * 12 + 23)

    menu.mainloop()
