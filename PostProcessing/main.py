########################################################################################################################
# iCorrVision Post-processing Module GUI                                                                               #
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
    iCorrVision Post-processing Module GUI
    Copyright (C) 2022 iCorrVision team

    This file is part of the iCorrVision software.

    The iCorrVision Post-processing Module GUI is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The iCorrVision-3D Calibration Module GUI is distributed in the hope that it will be useful,
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
import numpy as np
import tkinter as tk; from tkinter import *; import os
import tkinter.scrolledtext as st
from tkinter import ttk
import modules as module
from PIL import Image, ImageTk

########################################################################################################################
# Graphical interface - tkinter
########################################################################################################################
if __name__ == '__main__':

    # Current directory:
    CurrentDir = os.path.dirname(os.path.realpath(__file__))

    # GUI interface:
    menu = tk.Tk()

    # GUI title:
    menu.title('iCorrVision Post-processing Module '+V)
    menu.iconbitmap(CurrentDir+'\static\iCorrVision Post-processing Icon.ico')

    # Global variables:

    # Input variables:
    global file; file = StringVar(menu)
    global file_var; file_var = BooleanVar(menu); file_var.set(False)
    global resultsFolder; resultsFolder = StringVar(menu)
    global selectionFolder; selectionFolder = StringVar(menu)
    # Study variables:
    global Method; Method = StringVar(menu)
    global Correlation; Correlation = StringVar(menu)
    global Valmm; Valmm = DoubleVar(menu); Valmm.trace("w", lambda name, index, mode, Valmm=Valmm: module.callback(Valmm, Valpixel, Calib_factor))
    global Valpixel; Valpixel = IntVar(menu); Valpixel.trace("w", lambda name, index, mode, Valmm=Valmm: module.callback(Valmm, Valpixel, Calib_factor))
    global Calib_factor; Calib_factor = DoubleVar(menu); Calib_factor.trace("w", lambda name, index, mode, Valmm=Valmm: module.callback(Valmm, Valpixel, Calib_factor))
    # Strain calculation variables:
    global Strain_window; Strain_window = IntVar(menu)
    global Shape_function; Shape_function = StringVar(menu)
    # Figure parameters:
    global figureFolder; figureFolder = StringVar(menu)
    global outputFolder; outputFolder = StringVar(menu)
    global TextFont; TextFont = StringVar(menu)
    global FontSize; FontSize = IntVar(menu)
    global xTicks; xTicks = IntVar(menu)
    global yTicks; yTicks = IntVar(menu)
    global AddTitle; AddTitle = StringVar(menu)
    global AddAxes; AddAxes = StringVar(menu)
    global Linewidth; Linewidth = DoubleVar(menu)
    global AxesDigits; AxesDigits = IntVar(menu)
    global cbarTicks; cbarTicks = IntVar(menu)
    global ImgFormat; ImgFormat = StringVar(menu)
    global Alpha; Alpha = DoubleVar(menu)
    global cbarDigits; cbarDigits = IntVar(menu)
    global cbarFormat; cbarFormat = StringVar(menu)
    global Tag; Tag = StringVar(menu)
    global Instant; Instant = StringVar(menu)
    global EndInstant; EndInstant = IntVar(menu)
    # Output variables:
    global AllPlots; AllPlots = IntVar(menu)
    global ReferenceGrid; ReferenceGrid = IntVar(menu)
    global CurrentGrid; CurrentGrid = IntVar(menu)
    global Udisplacement; Udisplacement = IntVar(menu)
    global Vdisplacement; Vdisplacement = IntVar(menu)
    global UVdisplacement; UVdisplacement = IntVar(menu)
    global Wdisplacement; Wdisplacement = IntVar(menu)
    global exx; exx = IntVar(menu)
    global eyy; eyy = IntVar(menu)
    global exy; exy = IntVar(menu)
    global Reconstruction; Reconstruction = IntVar(menu)
    global AllAuto; AllAuto = IntVar(menu)
    global UdisplacementAuto; UdisplacementAuto = IntVar(menu)
    global VdisplacementAuto; VdisplacementAuto = IntVar(menu)
    global UVdisplacementAuto; UVdisplacementAuto = IntVar(menu)
    global WdisplacementAuto; WdisplacementAuto = IntVar(menu)
    global exxAuto; exxAuto = IntVar(menu)
    global eyyAuto; eyyAuto = IntVar(menu)
    global exyAuto; exyAuto = IntVar(menu)
    global ReconstructionAuto;  ReconstructionAuto = IntVar(menu)
    global UdisplacementMax; UdisplacementMax = DoubleVar(menu)
    global VdisplacementMax; VdisplacementMax = DoubleVar(menu)
    global UVdisplacementMax; UVdisplacementMax = DoubleVar(menu)
    global WdisplacementMax; WdisplacementMax = DoubleVar(menu)
    global exxMax; exxMax = DoubleVar(menu)
    global eyyMax; eyyMax = DoubleVar(menu)
    global exyMax; exyMax = DoubleVar(menu)
    global ReconstructionMax; ReconstructionMax = DoubleVar(menu)
    global UdisplacementMin; UdisplacementMin = DoubleVar(menu)
    global VdisplacementMin; VdisplacementMin = DoubleVar(menu)
    global UVdisplacementMin; UVdisplacementMin = DoubleVar(menu)
    global WdisplacementMin; WdisplacementMin = DoubleVar(menu)
    global exxMin; exxMin = DoubleVar(menu)
    global eyyMin; eyyMin = DoubleVar(menu)
    global exyMin; exyMin = DoubleVar(menu)
    global ReconstructionMin;  ReconstructionMin = DoubleVar(menu)
    # Canvas variables:
    global Preview_field; Preview_field = StringVar(menu)
    global Preview; Preview = IntVar(menu)
    global Color_map; Color_map = StringVar(menu)

    # Default values:
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

    # GUI size:
    app_width = 1455
    app_height = 725

    # Screen configuration:
    screen_width = menu.winfo_screenwidth()
    screen_height = menu.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2 ) - (app_height / 2)

    menu.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

    # GUI style:
    s = ttk.Style()
    s.theme_use('alt')

    # Grid configuration:
    xinit = 20; yinit = 20; dyinit = 50; dxinit = 168

    menu.configure(background='#99b3c3')##4c5b61
    menu.resizable (width = True, height = True)

    canvas_window=Canvas(menu,bg='#99b3c3',height=app_height-4,width=app_width-4)
    canvas_window.place(x=0,y=0)

    # iCorrVision Post-processing logo:
    image_logo = Image.open(os.path.join(CurrentDir, 'static', 'iCorrVision Post-processing.png'))
    image_logo = image_logo.resize((int(798 / 4), int(158 / 4)), Image.ANTIALIAS)
    image_logo_re = ImageTk.PhotoImage(image_logo)

    canvas_logo = tk.Label(menu, width=200, height=50, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                           image=image_logo_re);
    canvas_logo.place(x=xinit + 5, y=10)

    # Open user guide pdf 2D:
    tk.Button(menu, text='User guide 2D', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
              fg='#282C34', command=lambda: module.openguide2D(CurrentDir)).place(x=xinit + dxinit*2 + 126 , y=yinit, width=135, height=25)

    # Open user guide pdf 3D:
    tk.Button(menu, text='User guide 3D', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
              fg='#282C34', command=lambda: module.openguide3D(CurrentDir)).place(x=xinit + dxinit * 3 + 114, y=yinit,
                                                                                  width=135, height=25)

    # Input parameters:
    Label(menu, text = 'INPUT',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit-10+42)
    canvas_window.create_rectangle(xinit-10,yinit+45,xinit-5+756,yinit+23+10-5+112, outline='#282C34')

    # Interface to select the output folder of the correlation module:
    results_btn = tk.Button(menu, text = 'Results folder', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.results_folder(console, results_status, resultsFolder))
    results_btn.place(x=xinit, y=yinit+dyinit+5)
    results_status = Entry(menu, bg='red')
    results_status.place(x=xinit+142, y=yinit-1+dyinit+5,width=8,height=27)
    Entry(menu, textvariable=resultsFolder, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit,y=yinit+dyinit+5,width=572,height=25)

    # Interface to select the cropped images folder of the correlation module (must contain Left and Right folders):
    selection_btn = tk.Button(menu, text = 'Images folder', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.selection_folder(console, selection_status, selectionFolder))
    selection_btn.place(x=xinit, y=yinit+dyinit*2+5)
    selection_status = Entry(menu, bg='red')
    selection_status.place(x=xinit+142, y=yinit+dyinit*2-1+5,width=8,height=27)
    Entry(menu, textvariable=selectionFolder, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit,y=yinit+dyinit*2+5,width=572,height=25)

    # Correlation parameters:
    Label(menu, text = 'PARAMETERS',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit+23+dyinit*2.5+10)
    canvas_window.create_rectangle(xinit-10,yinit+23+dyinit*3+10-5-10,xinit-5+200,yinit+23+dyinit*4+10-5+112, outline='#282C34')

    # Configuration used in the correlation module (Eulerian or Lagrangian):
    Label(menu, text = 'Config.:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit+dyinit*3+23+10)
    corr_method = ttk.Combobox(menu, textvariable=Method, font = ('Heveltica',10))
    corr_method['values'] = ('Select','Eulerian','Lagrangian')
    corr_method.place(x=xinit,y=yinit+23*2+dyinit*3+10,width=82,height=25)

    # Correlation strategy used in the correlation module (Spatial or Incremental):
    Label(menu, text='Correlation:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit - 1+102, y=yinit + dyinit * 3 + 23 + 10)
    corr_method = ttk.Combobox(menu, textvariable=Correlation, font=('Heveltica', 10))
    corr_method['values'] = ('Select', 'Spatial', 'Incremental')
    corr_method.place(x=xinit+102, y=yinit + 23 * 2 + dyinit * 3 + 10, width=82, height=25)

    # Variable for calibration used in the correlation module [mm]:
    Label(menu, text = 'Valmm:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit+dyinit*4+23+10)
    Entry(menu, textvariable=Valmm, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit,y=yinit+23*2+dyinit*4+10,width=82,height=24)

    # Variable for calibration used in the correlation module [pixel]:
    Label(menu, text = 'Valpixel:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+102,y=yinit+dyinit*4+23+10)
    Entry(menu, textvariable=Valpixel, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+102,y=yinit+23*2+dyinit*4+10,width=82,height=24)

    # Calibration factor (Valpixel/Valmm):
    Label(menu, text = 'Calibration factor (pixel/mm):',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit+dyinit*5+23+10)
    Entry(menu, textvariable=Calib_factor, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit,y=yinit+23*2+dyinit*5+10,width=185,height=24)

    # Strain calculation interface:
    Label(menu, text = 'STRAIN CALCULATION',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit+23+dyinit*6.5+10)
    canvas_window.create_rectangle(xinit-10,yinit+23+dyinit*7+10-5-10,xinit-5+200,yinit+23+dyinit*7+10-5+112, outline='#282C34')

    # Strain window [pixels]:
    Label(menu, text = 'Strain window:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit+23+dyinit*7+10)
    spinbox = ttk.Spinbox(menu, from_=5, increment=2, to= 1000,textvariable=Strain_window, font=('Heveltica', 10))
    spinbox.place(x=xinit,y=yinit+23*2+dyinit*7+10,width=185,height=25)
    spinbox.set(5)

    # Shape function for displacement fitting (Bilinear Q4 and Biquadratic Q9):
    Label(menu, text = 'Shape function:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1,y=yinit+23+dyinit*8+10)
    shape_f = ttk.Combobox(menu, textvariable=Shape_function, font = ('Heveltica',10))
    shape_f['values'] = ('None','Bilinear','Biquadratic')
    shape_f.place(x=xinit,y=yinit+23*2+dyinit*8+10,width=185,height=25)

    # Figure properties and output parameters:
    Label(menu, text = 'FIGURES PROPERTIES and OUTPUT PARAMETERS',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+230,y=yinit+23+dyinit*2.5+10)
    canvas_window.create_rectangle(xinit-10+230,yinit+23+dyinit*3+10-5-10,xinit-5+205+230+321,yinit+23+dyinit*7+10-5+112, outline='#282C34')

    # Select the folder to save the output figures:
    figure_btn = tk.Button(menu, text = 'Save figures', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.figure_folder(console, figure_status, figureFolder))
    figure_btn.place(x=xinit+dxinit*1.37,y=yinit+23*2+dyinit*3+10)
    figure_status = Entry(menu, bg='red')
    figure_status.place(x=xinit+dxinit*1.37+142,y=yinit+23*2+dyinit*3+10-1,width=8,height=27)
    Entry(menu, textvariable=figureFolder, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.37+168,y=yinit+23*2+dyinit*3+10,width=342,height=25)

    # Select the folder to save the output data:
    save_out_btn = tk.Button(menu, text = 'Save output', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.output_folder(console, save_out_status, outputFolder))
    save_out_btn.place(x=xinit+dxinit*1.37,y=yinit+23*2+dyinit*4+10)
    save_out_status = Entry(menu, bg='red')
    save_out_status.place(x=xinit+dxinit*1.37+142,y=yinit+23*2+dyinit*4+10-1,width=8,height=27)
    Entry(menu, textvariable=outputFolder, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.37+168,y=yinit+23*2+dyinit*4+10,width=342,height=25)

    # Text font (Times New Roman, Arial and Heveltica):
    Label(menu, text = 'Text font:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*1.37,y=yinit+dyinit*5+23+10)
    image_font = ttk.Combobox(menu, textvariable=TextFont, font = ('Heveltica',10))
    image_font['values'] = ('Select','Times New Roman','Arial','Heveltica')
    image_font.place(x=xinit+dxinit*1.37,y=yinit+23*2+dyinit*5+10,width=190,height=25)

    # Font size:
    Label(menu, text = 'Font size:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*2.65,y=yinit+dyinit*5+23+10)
    font_size = ttk.Combobox(menu, textvariable=FontSize, font = ('Heveltica',10))
    font_size['values'] = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20')
    font_size.place(x=xinit+dxinit*2.65,y=yinit+23*2+dyinit*5+10,width=82,height=25)

    # x ticks:
    Label(menu, text = '    ticks:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3.29,y=yinit+dyinit*5+23+10)
    Label(menu, text = 'x',bg='#99b3c3', fg ='#282C34', font = ('Times',11,'italic') ).place(x=xinit-1+dxinit*3.29,y=yinit+dyinit*5+23+10)
    font_size = ttk.Combobox(menu, textvariable=xTicks, font = ('Heveltica',10))
    font_size['values'] = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20')
    font_size.place(x=xinit+dxinit*3.29,y=yinit+23*2+dyinit*5+10,width=82,height=25)

    # y ticks:
    Label(menu, text = '    ticks:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3.93,y=yinit+dyinit*5+23+10)
    Label(menu, text = 'y',bg='#99b3c3', fg ='#282C34', font = ('Times',11,'italic') ).place(x=xinit-1+dxinit*3.93,y=yinit+dyinit*5+23+10)
    font_size = ttk.Combobox(menu, textvariable=yTicks, font = ('Heveltica',10))
    font_size['values'] = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20')
    font_size.place(x=xinit+dxinit*3.93,y=yinit+23*2+dyinit*5+10,width=82,height=25)

    # Add title (Yes or No):
    Label(menu, text = 'Add title:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*1.37,y=yinit+dyinit*6+23+10)
    add_title = ttk.Combobox(menu, textvariable=AddTitle, font = ('Heveltica',10))
    add_title['values'] = ('Select','Yes','No')
    add_title.place(x=xinit+dxinit*1.37,y=yinit+23*2+dyinit*6+10,width=82,height=25)

    # Add axes (Yes or No):
    Label(menu, text = 'Add axes:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*2.01,y=yinit+dyinit*6+23+10)
    add_axes = ttk.Combobox(menu, textvariable=AddAxes, font = ('Heveltica',10))
    add_axes['values'] = ('Select','Yes','No')
    add_axes.place(x=xinit+dxinit*2.01,y=yinit+23*2+dyinit*6+10,width=82,height=25)

    # Line width:
    Label(menu, text = 'Line width:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*2.65,y=yinit+dyinit*6+23+10)
    line_width = ttk.Combobox(menu, textvariable=Linewidth, font = ('Heveltica',10))
    line_width['values'] = ('0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1','2','3','4','5','6','7','8','9','10')
    line_width.place(x=xinit+dxinit*2.65,y=yinit+23*2+dyinit*6+10,width=82,height=25)

    # Axes digits:
    Label(menu, text = 'Axes digits:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3.29,y=yinit+dyinit*6+23+10)
    font_size = ttk.Combobox(menu, textvariable=AxesDigits, font = ('Heveltica',10))
    font_size['values'] = ('1','2','3','4','5','6','7','8','9','10')
    font_size.place(x=xinit+dxinit*3.29,y=yinit+23*2+dyinit*6+10,width=82,height=25)

    # Colorbar ticks
    Label(menu, text = 'Cbar ticks:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3.93,y=yinit+dyinit*6+23+10)
    font_size = ttk.Combobox(menu, textvariable=cbarTicks, font = ('Heveltica',10))
    font_size['values'] = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20')
    font_size.place(x=xinit+dxinit*3.93,y=yinit+23*2+dyinit*6+10,width=82,height=25)

    # Output image format ('.bmp','.tif','.jpg','.png' and '.pdf'):
    Label(menu, text = 'Image format:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*1.37,y=yinit+dyinit*7+23+10)
    format_image = ttk.Combobox(menu, textvariable=ImgFormat, font = ('Heveltica',10))
    format_image['values'] = ('Select','.bmp','.tif','.jpg','.png','.pdf')
    format_image.place(x=xinit+dxinit*1.37,y=yinit+23*2+dyinit*7+10,width=82,height=25)

    # Full-field map transparency (from 0 to 1):
    Label(menu, text = 'Transparency:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*2.01,y=yinit+dyinit*7+23+10)
    Entry(menu, textvariable=Alpha, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*2.01,y=yinit+23*2+dyinit*7+10,width=82,height=25)

    # Image tag:
    Label(menu, text = 'Image tag:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*2.65,y=yinit+dyinit*7+23+10)
    Entry(menu, textvariable=Tag, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*2.65,y=yinit+23*2+dyinit*7+10,width=82,height=25)

    # Colorbar digits:
    Label(menu, text = 'Cbar digits:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3.29,y=yinit+dyinit*7+23+10)
    font_size = ttk.Combobox(menu, textvariable=cbarDigits, font = ('Heveltica',10))
    font_size['values'] = ('1','2','3','4','5','6','7','8','9','10')
    font_size.place(x=xinit+dxinit*3.29,y=yinit+23*2+dyinit*7+10,width=82,height=25)

    # Number format of the colorbar ('Float' and 'Scientific'):
    Label(menu, text = 'Cbar format:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3.93,y=yinit+dyinit*7+23+10)
    font_size = ttk.Combobox(menu, textvariable=cbarFormat, font = ('Heveltica',10))
    font_size['values'] = ('Integer', 'Float', 'Scientific')
    font_size.place(x=xinit+dxinit*3.93,y=yinit+23*2+dyinit*7+10,width=82,height=25)

    # Plot instant:
    Label(menu, text = 'Plot instant:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3.29,y=yinit+dyinit*8+23+10)
    Entry(menu, textvariable=Instant, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*3.29,y=yinit+23*2+dyinit*8+10,width=120,height=25)

    Checkbutton(menu, command=lambda: module.end_instant(Instant, EndInstant),text = 'End', variable = EndInstant, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit-1+183+dxinit*3,y=yinit+dyinit*8+23+33)

    # Check to plot all figures:
    Checkbutton(menu, command=lambda: module.checkall(AllPlots, cbs_plot), text = 'All', variable = AllPlots, bg = '#99b3c3', fg ='#282C34',activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*1.37,y=yinit+dyinit*8+23+33)

    # Check to change the axes limits to automatic:
    Checkbutton(menu, command=lambda: module.checkallauto(AllAuto, cbs_auto), text = 'All auto', variable = AllAuto, bg = '#99b3c3', fg ='#282C34',activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*2-50,y=yinit+dyinit*8+23+33)

    # Reference gid lines:
    Checkbutton(menu, text = 'Reference', variable = ReferenceGrid, bg = '#99b3c3', fg ='#282C34',activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*2.5-50,y=yinit+dyinit*8+23+33)

    # Current gid lines:
    Checkbutton(menu, text = 'Current', variable = CurrentGrid, bg = '#99b3c3', fg ='#282C34',activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit-1+dxinit*3-40,y=yinit+dyinit*8+23+33)

    # u-displacement figure:
    Checkbutton(menu, text = '   -displacement', variable = Udisplacement, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0,y=yinit+23*2+dyinit*9+10)
    Label(menu, text = 'u',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+dxinit*0+20,y=yinit+23*2+dyinit*9+10)
    Entry(menu, textvariable=UdisplacementMin, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3,y=yinit+23*2+dyinit*9+10,width=40,height=25)
    Entry(menu, textvariable=UdisplacementMax, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+60,y=yinit+23*2+dyinit*9+10,width=40,height=25)
    Checkbutton(menu, text = 'Auto', variable = UdisplacementAuto, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0.85,y=yinit+23*2+dyinit*9+10)
    canvas_window.create_line(xinit+dxinit*0, yinit+23*2+dyinit*9+23, xinit+dxinit*1.3+60, yinit+23*2+dyinit*9+23)

    # v-displacement figure:
    Checkbutton(menu, text = '   -displacement', variable = Vdisplacement, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0,y=yinit+23*2+dyinit*10+10)
    Label(menu, text = 'v',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+dxinit*0+20,y=yinit+23*2+dyinit*10+10)
    Entry(menu, textvariable=VdisplacementMin, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3,y=yinit+23*2+dyinit*10+10,width=40,height=25)
    Entry(menu, textvariable=VdisplacementMax, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+60,y=yinit+23*2+dyinit*10+10,width=40,height=25)
    Checkbutton(menu, text = 'Auto', variable = VdisplacementAuto, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0.85,y=yinit+23*2+dyinit*10+10)
    canvas_window.create_line(xinit+dxinit*0, yinit+23*2+dyinit*10+23, xinit+dxinit*1.3+60, yinit+23*2+dyinit*10+23)

    # Total-displacement figure:
    Checkbutton(menu, text='     -displacement', variable=UVdisplacement, bg='#99b3c3', fg='#282C34', activebackground='#99b3c3', font=('Heveltica', 10)).place(x=xinit + dxinit * 0,y=yinit + 23 * 2 + dyinit * 11 + 10)
    Label(menu, text = 'uv',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+dxinit*0+20,y=yinit+23*2+dyinit*11+10)
    Entry(menu, textvariable=UVdisplacementMin, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit * 1.3, y=yinit + 23 * 2 + dyinit * 11 + 10, width=40, height=25)
    Entry(menu, textvariable=UVdisplacementMax, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit * 1.3 + 60,y=yinit + 23 * 2 + dyinit * 11 + 10, width=40, height=25)
    Checkbutton(menu, text='Auto', variable=UVdisplacementAuto, bg='#99b3c3', fg='#282C34', activebackground='#99b3c3', font=('Heveltica', 10)).place(x=xinit + dxinit * 0.85, y=yinit + 23 * 2 + dyinit * 11 + 10)
    canvas_window.create_line(xinit + dxinit * 0, yinit + 23 * 2 + dyinit * 11 + 23, xinit + dxinit * 1.3 + 60, yinit + 23 * 2 + dyinit * 11 + 23)

    # w-displacement figure:
    wDisplacementCheck = Checkbutton(menu, text = '   -displacement', variable = Wdisplacement, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) )
    wDisplacementLabel = Label(menu, text = 'w',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') )
    wDisplacementCheck.place(x=xinit+dxinit*0,y=yinit+23*2+dyinit*12+10)
    wDisplacementLabel.place(x=xinit + dxinit * 0 + 20, y=yinit + 23 * 2 + dyinit * 12 + 10)
    Entry(menu, textvariable=WdisplacementMin, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3,y=yinit+23*2+dyinit*12+10,width=40,height=25)
    Entry(menu, textvariable=WdisplacementMax, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+60,y=yinit+23*2+dyinit*12+10,width=40,height=25)
    wDisplacementCheckAuto = Checkbutton(menu, text = 'Auto', variable = WdisplacementAuto, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) )
    wDisplacementCheckAuto.place(x=xinit+dxinit*0.85,y=yinit+23*2+dyinit*12+10)
    canvas_window.create_line(xinit+dxinit*0, yinit+23*2+dyinit*12+23, xinit+dxinit*1.3+60, yinit+23*2+dyinit*12+23)

    # eₓₓ-strain figure:
    Checkbutton(menu, text = '     -strain', variable = exx, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0+350,y=yinit+23*2+dyinit*9+10)
    Label(menu, text = '\u03B5ₓₓ',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+dxinit*0++350+22,y=yinit+23*2+dyinit*9+10)
    Entry(menu, textvariable=exxMin, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+308,y=yinit+23*2+dyinit*9+10,width=40,height=25)
    Entry(menu, textvariable=exxMax, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+60+308,y=yinit+23*2+dyinit*9+10,width=40,height=25)
    Checkbutton(menu, text = 'Auto', variable = exxAuto, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0.85+308,y=yinit+23*2+dyinit*9+10)
    canvas_window.create_line(xinit+dxinit*0+350, yinit+23*2+dyinit*9+23, xinit+dxinit*1.3+40+350, yinit+23*2+dyinit*9+23)

    # eᵧᵧ-strain figure:
    Checkbutton(menu, text = '     -strain', variable = eyy, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0+350,y=yinit+23*2+dyinit*10+10)
    Label(menu, text = '\u03B5ᵧᵧ',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+dxinit*0++350+22,y=yinit+23*2+dyinit*10+10)
    Entry(menu, textvariable=eyyMin, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+308,y=yinit+23*2+dyinit*10+10,width=40,height=25)
    Entry(menu, textvariable=eyyMax, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+60+308,y=yinit+23*2+dyinit*10+10,width=40,height=25)
    Checkbutton(menu, text = 'Auto', variable = eyyAuto, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0.85+308,y=yinit+23*2+dyinit*10+10)
    canvas_window.create_line(xinit+dxinit*0+350, yinit+23*2+dyinit*10+23, xinit+dxinit*1.3+40+350, yinit+23*2+dyinit*10+23)

    # eₓᵧ-strain figure:
    Checkbutton(menu, text = '     -strain', variable = exy, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0+350,y=yinit+23*2+dyinit*11+10)
    Label(menu, text = '\u03B5ₓᵧ',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+dxinit*0++350+22,y=yinit+23*2+dyinit*11+10)
    Entry(menu, textvariable=exyMin, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+308,y=yinit+23*2+dyinit*11+10,width=40,height=25)
    Entry(menu, textvariable=exyMax, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+dxinit*1.3+60+308,y=yinit+23*2+dyinit*11+10,width=40,height=25)
    Checkbutton(menu, text = 'Auto', variable = exyAuto, bg = '#99b3c3', fg ='#282C34', activebackground='#99b3c3', font = ('Heveltica',10) ).place(x=xinit+dxinit*0.85+308,y=yinit+23*2+dyinit*11+10)
    canvas_window.create_line(xinit+dxinit*0+350, yinit+23*2+dyinit*11+23, xinit+dxinit*1.3+40+350, yinit+23*2+dyinit*11+23)

    # 3D reconstruction figure:
    ReconstructionCheck = Checkbutton(menu, text='3D shape', variable=Reconstruction, bg='#99b3c3', fg='#282C34', activebackground='#99b3c3',font=('Heveltica', 10))
    ReconstructionCheck.place(x=xinit + dxinit * 0 + 350, y=yinit + 23 * 2 + dyinit * 12 + 10)
    Entry(menu, textvariable=ReconstructionMin, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit * 1.3 + 308,y=yinit + 23 * 2 + dyinit * 12 + 10,width=40, height=25)
    Entry(menu, textvariable=ReconstructionMax, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit + dxinit * 1.3 + 60 + 308,y=yinit + 23 * 2 + dyinit * 12 + 10,width=40, height=25)
    ReconstructionCheckAuto = Checkbutton(menu, text='Auto', variable=ReconstructionAuto, bg='#99b3c3', fg='#282C34', activebackground='#99b3c3',font=('Heveltica', 10))
    ReconstructionCheckAuto.place(x=xinit + dxinit * 0.85 + 308, y=yinit + 23 * 2 + dyinit * 12 + 10)
    canvas_window.create_line(xinit + dxinit * 0 + 350, yinit + 23 * 2 + dyinit * 12 + 23,xinit + dxinit * 1.3 + 40 + 350, yinit + 23 * 2 + dyinit * 12 + 23)

    # Group of images to plot:
    cbs_plot = [ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction]

    # Group of automatic limits to consider:
    cbs_auto = [UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto]

    # Maximum limit:
    var_Max = [UdisplacementMax, VdisplacementMax, UVdisplacementMax, WdisplacementMax, exxMax, eyyMax, exyMax, ReconstructionMax]

    # Minimum limit:
    var_Min = [UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin]

    # Preview canvas:
    canvas = tk.Label(menu, bg='#99b3c3')
    canvas.place(x=xinit+775+2, y=yinit+4)
    canvas_window.create_rectangle(xinit+775,yinit,xinit+775+640,yinit+480+9, outline='#282C34')

    # Select which data will be previewed:
    Label(menu, text = 'Preview map:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit+dxinit*5-40-16,y=yinit+23+dyinit*8+8)
    preview_f = ttk.Combobox(menu, textvariable=Preview_field, font = ('Heveltica',10))
    preview_f['values'] = ('Select','u-displacement','v-displacement','w-displacement','uv-displacement','exx-strain','eyy-strain','exy-strain', '3D Reconstruction')
    preview_f.place(x=xinit+dxinit*5-40-15,y=yinit+23*2+dyinit*8+8,width=250,height=25)
    Preview_field_dict = {'u-displacement': 0, 'v-displacement': 1, 'w-displacement': 2, 'uv-displacement': 3,'exx-strain': 4, 'eyy-strain': 5, 'exy-strain': 6, '3D Reconstruction': 7}

    # Color map:
    Label(menu, text = 'Color map:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit+dxinit*5-40-16+280,y=yinit+23+dyinit*8+8)
    color_map = ttk.Combobox(menu, textvariable=Color_map, font = ('Heveltica',10))
    color_map['values'] = ('Select','Blues','Greens','Greys','Oranges','Reds','Afmhot','Autumn','Bone','Copper','Hot','Hsv','Jet','Winter')
    color_map.place(x=xinit+dxinit*5-40-15+280,y=yinit+23*2+dyinit*8+8,width=120,height=25)
    color_map_dict = {'Blues':0,'Greens':1,'Greys':2,'Oranges':3,'Reds':4,'Afmhot':5,'Autumn':6,'Bone':7,'Copper':8,'Hot':9,'Hsv':10,'Jet':11,'Winter':12}


    # Check to preview the full-field map:
    Checkbutton(menu, text = 'Preview', variable = Preview, anchor='w', bg = '#99b3c3', fg ='#282C34',activebackground='#99b3c3',
        font = ('Heveltica',10) ).place(x=xinit+dxinit*8-138,y=yinit+23*2+dyinit*8+8,width=195,height=25)

    # Plot button:
    plot_btn = tk.Button(menu, text = 'Plot', width=25, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.plot_figures(
        menu, console, file, file_var, canvas, wDisplacementCheck, wDisplacementCheckAuto, wDisplacementLabel, ReconstructionCheck, ReconstructionCheckAuto, progression, progression_bar,
        canvas_text, resultsFolder,
        selectionFolder, figureFolder, outputFolder, Valmm, Valpixel, Instant, Shape_function, Strain_window,
        Preview_field, Preview,
        Preview_field_dict, Color_map, color_map_dict, Method, Tag, Alpha, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, AxesDigits,
        cbarTicks, ImgFormat, cbarDigits, cbarFormat, cbs_auto, cbs_plot, var_Min, var_Max, DIC_status_2D,
        DIC_status_3D, Linewidth,
        AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, Correlation
    ))
    plot_btn.place(x=xinit+dxinit*8-40,y=yinit+23*2+dyinit*8+8,width=100,height=25)

    # Identification of the DIC software:
    DIC_status_2D = Entry(menu, bg='#ccd9e1')
    DIC_status_2D.place(x=xinit + 775 + 2 + 621-60-10, y=yinit + 4, width=15, height=15)
    Label(menu, text = 'DIC 2D',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit + 775 + 2 + 621-110-10, y=yinit +1)

    DIC_status_3D = Entry(menu, bg='#ccd9e1')
    DIC_status_3D.place(x=xinit+775+2+621, y=yinit+4, width=15, height=15)
    Label(menu, text = 'DIC 3D',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit + 775 + 2 + 621-50, y=yinit +1)

    # Progression bar:
    progression = Canvas(menu)
    progression.place(x=xinit + 775,y=yinit+23*2+dyinit*12+10,width=515,height=25)
    progression_bar = progression.create_rectangle(0, 0, 0, 25, fill='#00cd00')
    canvas_text = progression.create_text(np.round(515/2)-30, 4, anchor=NW)
    progression.itemconfig(canvas_text, text='')

    # Console:
    console = st.ScrolledText(menu, bg = '#ccd9e1')
    console.place(x=xinit + 775,y=yinit+dyinit*10+6, width=640,height=125)

    # Close button:
    close_btn = tk.Button(menu, text = 'Close', width=25, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.close(menu))
    close_btn.place(x=xinit+dxinit*8-29,y=yinit+23*2+dyinit*12+10,width=100,height=25)

    # Save the results log:
    save_btn = tk.Button(menu, text = 'Save', width=25, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.save(menu, console, file,
         file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm, Valpixel, Strain_window,
         Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
         ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, Correlation))
    save_btn.place(x=xinit+dxinit*4-20,y=yinit+23*2+dyinit*9+10,width=100,height=25)

    # Save as the results log:
    saveas_btn = tk.Button(menu, text = 'Save as', width=25, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.save_as(menu, console, file,
         file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm, Valpixel, Strain_window,
         Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
         ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, Correlation))
    saveas_btn.place(x=xinit+dxinit*4-20,y=yinit+23*2+dyinit*10+10,width=100,height=25)

    # Load the results log:
    load_btn = tk.Button(menu, text = 'Load', width=25, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.load(menu, console, file,
         file_var, resultsFolder, selectionFolder, figureFolder, outputFolder, Method, Valmm, Valpixel, Strain_window,
         Shape_function, TextFont, FontSize, xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks,
         ImgFormat, Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, results_status,
         figure_status, selection_status, save_out_status, Correlation))
    load_btn.place(x=xinit+dxinit*4-20,y=yinit+23*2+dyinit*11+10,width=100,height=25)

    # Clear the GUI:
    clear_btn = tk.Button(menu, text = 'Clear', width=25, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34',
        command=lambda: module.clear(menu, canvas, console, wDisplacementCheck,  wDisplacementCheckAuto,wDisplacementLabel, ReconstructionCheck,ReconstructionCheckAuto,results_status, selection_status, figure_status, save_out_status,
            Method, Valmm, Valpixel, Calib_factor, Strain_window, Shape_function, TextFont, FontSize,
            xTicks, yTicks, AddTitle, AddAxes, Linewidth, AxesDigits, cbarTicks, ImgFormat,
            Alpha, cbarDigits, cbarFormat, Tag, Instant, Preview_field, Color_map, resultsFolder, selectionFolder,
            figureFolder, outputFolder, AllPlots, ReferenceGrid, CurrentGrid, Udisplacement, Vdisplacement, UVdisplacement, Wdisplacement, exx, eyy, exy, Reconstruction,AllAuto,
        UdisplacementAuto, VdisplacementAuto, UVdisplacementAuto, WdisplacementAuto, exxAuto, eyyAuto, exyAuto, ReconstructionAuto, UdisplacementMax, VdisplacementMax, UVdisplacementMax,
        WdisplacementMax,
        exxMax, eyyMax, exyMax, ReconstructionMax, UdisplacementMin, VdisplacementMin, UVdisplacementMin, WdisplacementMin, exxMin, eyyMin, exyMin, ReconstructionMin, progression, progression_bar, canvas_text, DIC_status_2D, DIC_status_3D, Correlation))
    clear_btn.place(x=xinit+dxinit*4-20,y=yinit+23*2+dyinit*12+10,width=100,height=25)

    # Developer and supervisors list:
    Label(menu, text = 'Developer: João Carlos A. D. Filho, M.Sc. (joaocadf@id.uff.br) / Supervisors: Luiz C. S. Nunes, D.Sc. (luizcsn@id.uff.br) and José M. C. Xavier, P.hD. (jmc.xavier@fct.unl.pt)',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',8) ).place(x=xinit-1,y=yinit+dyinit*13+33)

    # Initial message:
    console.insert(tk.END,
                   f'###################################################################  {V}\n\n'
                   '                 **  iCorrVision Post-processing Module **                   \n\n'
                   '#############################################################################\n\n\n')


    menu.mainloop()
