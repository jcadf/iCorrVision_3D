########################################################################################################################
# iCorrVision-3D Grabber Module GUI                                                                                    #
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
    iCorrVision-3D Grabber Module GUI
    Copyright (C) 2022 iCorrVision team

    This file is part of the iCorrVision-3D software.

    The iCorrVision-3D Grabber Module GUI is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The iCorrVision-3D Grabber Module GUI is distributed in the hope that it will be useful,
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
import tkinter as tk
from tkinter import *
import os
import tkinter.scrolledtext as st
from threading import Thread
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import ttk
import modules as module

########################################################################################################################
# Graphical interface
########################################################################################################################
if __name__ == '__main__':

    # Current directory:
    CurrentDir = os.path.dirname(os.path.realpath(__file__))

    # GUI interface:
    menu = tk.Tk()

    # GUI title:
    menu.title('iCorrVision-3D Grabber Module ' + V)
    menu.iconbitmap(CurrentDir + '\static\StereoGrabber.ico')

    # GUI style:
    s = ttk.Style()
    s.theme_use('alt')

    # Global variables:
    global selectionFolder; selectionFolder = StringVar(menu)
    global Width; Width = IntVar(menu)
    global Height; Height = IntVar(menu)
    global Exposure; Exposure = IntVar(menu)
    global Fps; Fps = IntVar(menu)
    global nImagesInit; nImagesInit = IntVar(menu)
    global TimeInit; TimeInit = DoubleVar(menu)
    global TimeAcquisition; TimeAcquisition = DoubleVar(menu)
    global switch_grid; switch_grid = BooleanVar(menu);
    global gridvar1; gridvar1 = IntVar(menu)
    global gridvar2; gridvar2 = IntVar(menu)
    global invert_camera; invert_camera = IntVar(menu)
    global k_snapshot; k_snapshot = IntVar(menu);
    global amplifyRight; amplifyRight = BooleanVar(menu);
    global amplifyLeft; amplifyLeft = BooleanVar(menu);
    global TypeImg; TypeImg = StringVar(menu);
    global preview_test; preview_test = BooleanVar(menu)

    # Default values:
    Width.set(1280);
    Height.set(1024);
    Exposure.set(60000);
    Fps.set(203)
    nImagesInit.set(0);
    TimeInit.set(0.0);
    TimeAcquisition.set(0.0)
    switch_grid.set(False)
    k_snapshot.set(1)
    preview_test.set(False)
    amplifyRight.set(False)
    amplifyLeft.set(False)

    # GUI size:
    app_width = 1495
    app_height = 717

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

    # Grid configuration:
    xinit = 20; yinit = 20; dyinit = 50

    # iCorrVision-3D Grabber logo:
    image_logo = Image.open(os.path.join(CurrentDir, 'static', 'iCorrVision-3D Grabber.png'))
    image_logo = image_logo.resize((int(712 / 4.8), int(144 / 4.8)), Image.ANTIALIAS)
    image_logo_re = ImageTk.PhotoImage(image_logo)

    canvas_logo = tk.Label(menu, width=150, height=50, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                           image=image_logo_re)
    canvas_logo.place(x=xinit + 5, y=yinit - 7)

    # Interface to select the captured images folder:
    selection_btn = tk.Button(menu, text='Select folder', width=19, height=1, bg='#DADDE3', activebackground='#ccd9e1',
                         fg='#282C34', command=lambda: module.folder(console, folder_status, selectionFolder, k_snapshot))
    selection_btn.place(x=xinit, y=yinit+dyinit)
    folder_status = Entry(menu, bg='red')
    folder_status.place(x=xinit + 142, y=yinit +dyinit- 1, width=8, height=27)

    # Width in pixels:
    Label(menu, text='Width (pixels):', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                  y=yinit + dyinit*2)
    Entry(menu, textvariable=Width, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit, y=yinit + 23 + dyinit*2,
                                                                                width=150, height=25)

    # Height in pixels:
    Label(menu, text='Height (pixels):', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                   y=yinit + dyinit * 3)
    Entry(menu, textvariable=Height, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit, y=yinit + 23 + dyinit * 3,
                                                                                 width=150, height=25)

    # Exposure time in µs:
    Label(menu, text='Exposure time (µs):', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                 y=yinit + dyinit * 4)
    Entry(menu, textvariable=Exposure, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit, y=yinit + 23 + dyinit * 4,
                                                                                   width=150, height=25)

    # Frames per second:
    Label(menu, text='Frames per second (FPS):', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                           y=yinit + dyinit * 5)
    Entry(menu, textvariable=Fps, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit, y=yinit + 23 + dyinit * 5,
                                                                              width=150, height=25)

    # Interface to add primary gridlines:
    Checkbutton(menu, variable=gridvar1, bg='#99b3c3', activebackground='#99b3c3', fg='#282C34',
                font=('Heveltica', 10)).place(x=xinit - 4, y=yinit + dyinit * 7 - 2 - 23)
    Label(menu, text='Primary grid', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + 20,
                                                                                               y=yinit + dyinit * 7 - 23)
    # Interface to add secondary gridlines:
    Checkbutton(menu, variable=gridvar2, bg='#99b3c3', activebackground='#99b3c3', fg='#282C34',
                font=('Heveltica', 10)).place(x=xinit - 4, y=yinit + dyinit * 7.5 - 2 - 23)
    Label(menu, text='Secondary grid', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + 20,
                                                                                                 y=yinit + dyinit * 7.5 - 23)

    # Interface to switch between master and slave cameras:
    Checkbutton(menu, variable=invert_camera, bg='#99b3c3', activebackground='#99b3c3', fg='#282C34',
                font=('Heveltica', 10)).place(x=xinit - 4, y=yinit + dyinit * 8 - 2 - 23)
    Label(menu, text='Flip', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + 20,
                                                                                       y=yinit + dyinit * 8 - 23)

    # Interface to select the image format ('.bmp', '.tif', '.jpg', '.png'):
    Label(menu, text='Image format:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                y=yinit + dyinit * 8.2 )
    format_image = ttk.Combobox(menu, textvariable=TypeImg, font=('Heveltica', 10))
    format_image['values'] = ('.bmp', '.tif', '.jpg', '.png')
    format_image.place(x=xinit, y=yinit + 23 + dyinit * 8.2, width=150, height=25)
    format_image.current(1)

    # Preview cameras:
    tk.Button(menu, text='Preview', width=19, height=1, bg='#DADDE3', activebackground='#ccd9e1', fg='#282C34',
              command=lambda: module.preview(menu, preview_test, visualize_status, console, Width, Height, Exposure, Fps, amplifyLeft, amplifyRight,
            canvas_left, canvas_right, gridvar1, gridvar2, invert_camera)).place(x=xinit, y=yinit + dyinit * 12 + 23 * 2)
    visualize_status = Entry(menu, bg='red')
    visualize_status.place(x=xinit + 142, y=yinit + dyinit * 12 + 23 * 2 - 1, width=8, height=27)

    # Number of images at the beginning of the experimental test:
    Label(menu, text='Number of images:', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                    y=yinit + dyinit * 9 + 23)
    Entry(menu, textvariable=nImagesInit, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit,
                                                                                      y=yinit + 23 * 2 + dyinit * 9,
                                                                                      width=150, height=25)

    # Time step at the beginning of the experimental test in seconds:
    Label(menu, text='Initial time (s):', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                    y=yinit + dyinit * 10 + 23)
    Entry(menu, textvariable=TimeInit, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit,
                                                                                   y=yinit + 23 * 2 + dyinit * 10,
                                                                                   width=150, height=25)

    # Acquisition time in seconds:
    Label(menu, text='Acquisition time (s):', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit,
                                                                                                        y=yinit + dyinit * 11 + 23)
    Entry(menu, textvariable=TimeAcquisition, bg='#ccd9e1', font=('Heveltica', 10)).place(x=xinit,
                                                                                          y=yinit + 23 * 2 + dyinit * 11,
                                                                                          width=150, height=25)

    # Button to acquire single snapshots:
    tk.Button(menu, text='Snapshot', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1', fg='#282C34',
              command=lambda: module.snapshot(console, selectionFolder, preview_test, k_snapshot, TypeImg, invert_camera)).place(x=xinit + 1306, y=yinit + dyinit * 9 + 23 * 2)

    # Button to start the image capture:
    tk.Button(menu, text='Start capture', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1', fg='#282C34',
              command=lambda: module.start_capture(menu, console, visualize_status, preview_test, Width, Height, Exposure, Fps, selectionFolder, TypeImg,
                  canvas_left, canvas_right, nImagesInit, TimeInit, TimeAcquisition, invert_camera)).place(x=xinit + 1306, y=yinit + dyinit * 10 + 23 * 2)

    # Button to stop the image capture:
    tk.Button(menu, text='Stop capture', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1', fg='#282C34',
              command=lambda: module.stop_capture(menu, console, selectionFolder, folder_status)).place(x=xinit + 1306, y=yinit + dyinit * 11 + 23 * 2)
    tk.Button(menu, text='Close', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1', fg='#282C34',
              command=lambda: module.close(menu)).place(x=xinit + 1306, y=yinit + dyinit * 12 + 23 * 2)

    # Load and display the blank canvas:
    image_black = Image.open(CurrentDir + '\static\ImageBlack.tiff')
    image_black = image_black.resize((640, 480), Image.ANTIALIAS)
    image_black_re = ImageTk.PhotoImage(image_black)

    # Left canvas:
    canvas_left = tk.Label(menu, width=640, height=480, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                           image=image_black_re);
    canvas_left.place(x=xinit + 170, y=yinit)

    # Right canvas:
    canvas_right = tk.Label(menu, width=640, height=480, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                            image=image_black_re);
    canvas_right.place(x=xinit + 815, y=yinit)

    # Open user guide pdf:
    tk.Button(menu, text='User guide', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
              fg='#282C34', command=lambda: module.openguide(CurrentDir)).place(x=xinit + 1306-9, y=yinit +10)

    # Console:
    console = st.ScrolledText(menu, bg='#ccd9e1')
    console.place(x=xinit + 170, y=yinit + 23 * 2 + dyinit * 9, width=1115, height=176)

    # Button to amplify the left (master) image:
    tk.Button(menu, text='Amplify L', width=10, height=1, bg='#DADDE3', activebackground='#ccd9e1', fg='#282C34',
              command=lambda: Thread(target=module.amplifyL, args=(preview_test, amplifyLeft)).start()).place(x=xinit + 722, y=yinit + dyinit * 8 + 23 * 2)

    # Button to amplify the right (slave) image:
    tk.Button(menu, text='Amplify R', width=10, height=1, bg='#DADDE3', activebackground='#ccd9e1', fg='#282C34',
              command=lambda: Thread(target=module.amplifyR, args=(preview_test, amplifyRight)).start()).place(x=xinit + 1368, y=yinit + dyinit * 8 + 23 * 2)

    # Initial message:
    console.insert(tk.END,
                   f'##############################################################################################################################  {V}\n\n'
                   '                                                 **  iCorrVision-3D Grabber Module **                                               \n\n'
                   '########################################################################################################################################\n\n')
    console.see('insert')

    # Developer and supervisors list:
    Label(menu,
          text='Developer: João Carlos A. D. Filho, M.Sc. (joaocadf@id.uff.br) / Supervisors: Luiz C. S. Nunes, D.Sc. (luizcsn@id.uff.br) and José M. C. Xavier, P.hD. (jmc.xavier@fct.unl.pt)',
          bg='#99b3c3', fg='#282C34', font=('Heveltica', 8)).place(x=xinit - 1, y=yinit + dyinit * 13 + 23)

    menu.mainloop()
