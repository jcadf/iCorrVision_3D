########################################################################################################################
# iCorrVision-3D Calibration Module GUI                                                                                #
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
    iCorrVision-3D Calibration Module GUI
    Copyright (C) 2022 iCorrVision team

    This file is part of the iCorrVision-3D software.

    The iCorrVision-3D Calibration Module GUI is free software: you can redistribute it and/or modify
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

import os
import tkinter as tk;
import tkinter.scrolledtext as st
from threading import Thread
from tkinter import *
from tkinter import ttk;

########################################################################################################################
# Modules
########################################################################################################################
import numpy as np
from PIL import Image, ImageTk

import modules as module

########################################################################################################################
# Graphical interface - tkinter
########################################################################################################################
if __name__ == '__main__':

    # Current directory:
    CurrentDir = os.path.dirname(os.path.realpath(__file__))

    # GUI interface:
    menu = tk.Tk()

    # GUI title:
    menu.title('iCorrVision-3D Calibration Module '+V)
    menu.iconbitmap(CurrentDir+'\static\iCorrVision-3D Calibration.ico')

    # GUI style:
    s = ttk.Style()
    s.theme_use('alt')
    s.configure(style='TCombobox', fieldbackground='#ccd9e1')

    # Global variables:
    global abort_param; abort_param = BooleanVar(menu); abort_param.set(False)
    global TypePattern; TypePattern = StringVar(menu)
    global format_image; format_image = StringVar(menu)
    global selectionFolder; selectionFolder = StringVar(menu)
    global SquareSize; SquareSize = DoubleVar(menu)
    global TypeImg; TypeImg = StringVar(menu)
    global XChecker; XChecker = IntVar(menu); XChecker.set(1)
    global YChecker; YChecker = IntVar(menu); YChecker.set(1)
    global Processed; Processed = StringVar(menu); Processed.set('0 of 0')
    global Rejected; Rejected = IntVar(menu)
    global Selected; Selected = IntVar(menu)
    global darkbg; darkbg = IntVar(menu)
    global rotbtn; rotbtn = IntVar(menu); rotbtn.set(1)
    global eulerbtn; eulerbtn = IntVar(menu)

    # GUI size:
    app_width = 1495
    app_height = 715

    # Screen configuration:
    screen_width = menu.winfo_screenwidth()
    screen_height = menu.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2 ) - (app_height / 2)

    menu.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

    menu.configure(background='#99b3c3')##4c5b61
    menu.resizable (width = False, height = False)

    canvas_window = Canvas(menu, bg='#99b3c3', height=app_height - 4, width=app_width - 4)
    canvas_window.place(x=0, y=0)

    selectionFolder = StringVar(menu)

    # Grid configuration:
    xinit = 20; yinit = 20; dyinit = 50

    # iCorrVision-3D Calibration logo:
    image_logo = Image.open(os.path.join(CurrentDir, 'static', 'iCorrVision-3D Calibration.png'))
    image_logo = image_logo.resize((int(756 / 5), int(144 / 5)), Image.ANTIALIAS)
    image_logo_re = ImageTk.PhotoImage(image_logo)

    canvas_logo = tk.Label(menu, width=152, height=50, bg='#99b3c3', borderwidth=0, highlightthickness=0,
                           image=image_logo_re);
    canvas_logo.place(x=xinit, y=yinit)

    # Interface to select the captured images folder of the calibration pattern (must contain Left and Right folders):
    select_folder = tk.Button(menu, text = 'Select folder', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34', command=lambda: module.folder(console, selectionFolder, folder_status, Processed, format_image,canvas_left,canvas_right))
    select_folder.place(x=xinit, y=yinit+dyinit*2+19)
    folder_status = Entry(menu, bg='red')
    folder_status.place(x=xinit+142, y=yinit+dyinit*2-1+19,width=8,height=27)

    # Calibration pattern type:
    Label(menu, text = 'Pattern type:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit,y=yinit+dyinit*3)
    format_pattern = ttk.Combobox(menu, textvariable=TypePattern, font = ('Heveltica',10))
    format_pattern['values'] = ('Checkerboard') # Only checkerboard
    format_pattern.place(x=xinit,y=yinit+23+dyinit*3,width=150,height=25)
    format_pattern.current(0)

    # Distance between calibration points:
    Label(menu, text = 'Size:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit,y=yinit+dyinit*4)
    Entry(menu, textvariable=SquareSize, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit,y=yinit+23+dyinit*4,width=50,height=25)

    # Activate thresholding:
    Checkbutton(menu, variable=darkbg, bg='#99b3c3', activebackground='#99b3c3', fg='#282C34',
                font=('Heveltica', 10)).place(x=xinit - 4+65, y=yinit + dyinit * 5 - 5 - 23)
    Label(menu, text='Threshold', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + 20+65,
                                                                                               y=yinit + dyinit * 5 - 25)

    # Image format (automatically detected):
    Label(menu, text = 'Image format:',bg='#99b3c3', fg ='#282C34', font = ('Heveltica',10) ).place(x=xinit,y=yinit+dyinit*5)
    format_image = ttk.Combobox(menu, textvariable=TypeImg, font = ('Heveltica',10))
    format_image['values'] = ('.bmp','.tif','.jpg','.png')
    format_image.place(x=xinit,y=yinit+23+dyinit*5,width=150,height=25)
    format_image.current(1)

    # Number of calibration points in X and Y directions:
    Label(menu, text = 'x',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+30,y=yinit+dyinit*6)
    Label(menu, text = 'y',bg='#99b3c3', fg ='#282C34', font = ('Times',12,'italic') ).place(x=xinit+108,y=yinit+dyinit*6)
    Entry(menu, textvariable=XChecker, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit,y=yinit+23+dyinit*6,width=70,height=25)
    Entry(menu, textvariable=YChecker, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit+80,y=yinit+23+dyinit*6,width=70,height=25)

    # Activate to generate the calibration file with the rotation matrix:
    Checkbutton(menu, variable=rotbtn, bg='#99b3c3', activebackground='#99b3c3', fg='#282C34',
                font=('Heveltica', 10),command=lambda: module.checkbtn1(eulerbtn)).place(x=xinit-4, y=yinit + dyinit * 8 - 5 - 23)
    Label(menu, text='Rotation matrix', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit +20,
                                                                                       y=yinit + dyinit * 8 - 25)

    # Activate to generate the calibration file with the Euler angles:
    Checkbutton(menu, variable=eulerbtn, bg='#99b3c3', activebackground='#99b3c3', fg='#282C34',
                font=('Heveltica', 10),command=lambda: module.checkbtn2(rotbtn)).place(x=xinit - 4, y=yinit + dyinit * 9 - 5 - 23)
    Label(menu, text='Euler angles [degrees]', bg='#99b3c3', fg='#282C34', font=('Heveltica', 10)).place(x=xinit + 20,
                                                                                                  y=yinit + dyinit * 9 - 25)

    # Display the processes, accepted and rejected stereo pairs:
    Label(menu, text = 'Processed pairs:',bg='#99b3c3', fg ='#282C34',
          font = ('Heveltica',10) ).place(x=xinit,y=yinit+dyinit*10+23)
    Entry(menu, textvariable=Processed, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit,y=yinit+dyinit*10+23*2,width=150,height=25)
    Label(menu, text = 'Rejected pairs:',bg='#99b3c3', fg ='#282C34',
          font = ('Heveltica',10) ).place(x=xinit,y=yinit+dyinit*11+23)
    Entry(menu, textvariable=Rejected, bg = '#ccd9e1', font = ('Heveltica',10)).place(x=xinit,y=yinit+dyinit*11+23*2,width=150,height=25)
    Label(menu, text = 'Accepted pairs:',bg='#99b3c3', fg ='#282C34',
          font = ('Heveltica',10) ).place(x=xinit,y=yinit+dyinit*12+23)
    Entry(menu, textvariable=Selected, bg = '#ccd9e1',
          font = ('Heveltica',10)).place(x=xinit,y=yinit+dyinit*12+23*2,width=150,height=25)

    # Detect calibration points:
    process_btn = tk.Button(menu, text = 'Scan points', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1',
              fg ='#282C34',command=lambda: module.detect_points(menu, selectionFolder, SquareSize, TypeImg,  XChecker,
                                                                   YChecker, scan_status, progression, progression_bar, console,
                                                                   canvas_text, canvas_left, canvas_right, Selected, Rejected,
                                                                   Processed, TypePattern, darkbg, process_btn, abort_param))
    process_btn.place(x=xinit, y=yinit+dyinit*9+23*2)
    scan_status = Entry(menu, bg='red')
    scan_status.place(x=xinit+142, y=yinit+dyinit*9+23*2-1,width=8,height=27)

    # Start stereo calibration using the detected calibration points:
    tk.Button(menu, text = 'Calibrate', width=20, height=1,bg='#DADDE3',activebackground= '#ccd9e1',
              fg ='#282C34',command=lambda: Thread(target=module.stereo, args=(console, calib_status)).start()).place(x=xinit + 1305, y=yinit+dyinit*9+23*2)
    calib_status = Entry(menu, bg='red')
    calib_status.place(x=xinit+142+1305, y=yinit+dyinit*9+23*2-1,width=8,height=27)

    # Print reprojection error:
    tk.Button(menu, text = 'Print results', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34',
              command=lambda: module.result(result_status)).place(x=xinit+ 1305, y=yinit+dyinit*10+23*2)
    result_status = Entry(menu, bg='red')
    result_status.place(x=xinit+142+ 1305, y=yinit+dyinit*10+23*2-1,width=8,height=27)

    # Save calibration file:
    tk.Button(menu, text = 'Save file', width=19, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34',
              command=lambda: module.save(menu, console, save_status, canvas_right, canvas_left, folder_status, calib_status, result_status,
         scan_status, progression, progression_bar, canvas_text, Processed, Rejected, Selected, rotbtn, eulerbtn)).place(x=xinit+ 1305, y=yinit+dyinit*11+23*2)
    save_status = Entry(menu, bg='red')
    save_status.place(x=xinit+142+ 1305, y=yinit+dyinit*11+23*2-1,width=8,height=27)

    # Close GUI:
    tk.Button(menu, text = 'Close', width=20, height=1,bg='#DADDE3',activebackground= '#ccd9e1', fg ='#282C34',
              command=lambda: module.close(menu)).place(x=xinit+ 1305, y=yinit+dyinit*12+23*2)

    # Load and display the blank canvas:
    image_black = Image.open(CurrentDir+'\static\ImageBlack.tiff')
    image_black = image_black.resize((640, 480), Image.ANTIALIAS)
    image_black_re = ImageTk.PhotoImage(image_black)

    # Left canvas:
    canvas_left=tk.Label(menu,width = 640, height = 480, bg = '#99b3c3', borderwidth=0, highlightthickness =0,
                         image = image_black_re); canvas_left.place(x=xinit+170, y=yinit)

    # Right canvas:
    canvas_right=tk.Label(menu, width = 640, height = 480, bg = '#99b3c3', borderwidth=0, highlightthickness =0,
                         image = image_black_re); canvas_right.place(x=xinit+815, y=yinit)

    # Open user guide pdf:
    tk.Button(menu, text='User guide', width=20, height=1, bg='#DADDE3', activebackground='#ccd9e1',
              fg='#282C34', command=lambda: module.openguide(CurrentDir)).place(x=xinit, y=yinit+dyinit*1+19)

    # Progression bar:
    progression = Canvas(menu)
    progression.place(x=xinit+170,y=yinit+23*2+dyinit*12,width=1117,height=25)
    progression_bar = progression.create_rectangle(0, 0, 0, 25, fill='#00cd00')
    canvas_text = progression.create_text(np.round(1117/2)-30, 4, anchor=NW)
    progression.itemconfig(canvas_text, text='')

    # Console:
    console = st.ScrolledText(menu, bg = '#ccd9e1')
    console.place(x=xinit+170,y=yinit+23*2+dyinit*9,width=1117,height=126)

    # Initial message:
    console.insert(tk.END,
                   f'##############################################################################################################################  {V}\n\n'
                   '                                                 **  iCorrVision-3D Calibration Module **                                               \n\n'
                   '########################################################################################################################################\n\n')
    console.see('insert')

    # Developer and supervisors list:
    Label(menu, text = 'Developer: João Carlos A. D. Filho, M.Sc. (joaocadf@id.uff.br) / Supervisors: Luiz C. S. Nunes, '
                       'D.Sc. (luizcsn@id.uff.br) and José M. C. Xavier, P.hD. (jmc.xavier@fct.unl.pt)',
          bg='#99b3c3', fg ='#282C34', font = ('Heveltica',8) ).place(x=xinit-1,y=yinit+dyinit*13+23)

    menu.mainloop()
