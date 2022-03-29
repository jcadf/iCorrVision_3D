########################################################################################################################
# iCorrVision-3D Calibration Module                                                                                    #
# iCorrVision team:     João Carlos Andrade de Deus Filho, M.Sc. (PGMEC/UFF¹) <joaocadf@id.uff.br>                     #
#                       Prof. Luiz Carlos da Silva Nunes, D.Sc.  (PGMEC/UFF¹) <luizcsn@id.uff.br>                      #
#                       Prof. José Manuel Cardoso Xavier, P.hD.  (FCT/NOVA²)  <jmc.xavier@fct.unl.pt>                  #
#                                                                                                                      #
#   1. Department of Mechanical Engineering | PGMEC - Universidade Federal Fluminense (UFF)                            #
#     Campus da Praia Vermelha | Niterói | Rio de Janeiro | Brazil                                                     #
#   2. NOVA SCHOOL OF SCIENCE AND TECHNOLOGY | FCT NOVA - Universidade NOVA de Lisboa (NOVA)                           #
#     Campus de Caparica | Caparica | Portugal                                                                         #
#                                                                                                                      #
# Date: 28-03-2022                                                                                                     #
########################################################################################################################

'''
    iCorrVision-3D Calibration Module
    Copyright (C) 2022 iCorrVision team

    This file is part of the iCorrVision-3D software.

    The iCorrVision-3D Calibration Module is free software: you can redistribute it and/or modify
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
import cv2; import numpy as np;  import glob
import math as math; import matplotlib.pyplot as plt; from threading import Thread
import tkinter as tk; from tkinter import *
import os; from tkinter import filedialog
import cv2 as cv; from PIL import Image, ImageTk
import pickle
from tkinter import messagebox
import csv
from scipy.spatial.transform import Rotation as rotate
import subprocess

########################################################################################################################
# Open user guide
########################################################################################################################
def openguide(CurrentDir):
    subprocess.Popen([CurrentDir + '\static\iCorrVision-3D.pdf'], shell=True)

########################################################################################################################
# If rotbtn is activated, eulerbtn is deactivated
########################################################################################################################
def checkbtn1(eulerbtn):
    eulerbtn.set(0)

########################################################################################################################
# If eulerbtn is activated, rotbtn is deactivated
########################################################################################################################
def checkbtn2(rotbtn):
    rotbtn.set(0)

########################################################################################################################
# Function to select the folder where the calibration images were saved
########################################################################################################################
def folder(console, selectionFolder, folder_status, Processed, format_image,canvas_left,canvas_right):
    global filename_selection, folder_test

    filename_selection = filedialog.askdirectory()
    selectionFolder.set(filename_selection)

    if not filename_selection:
        folder_status.configure(bg = 'red') # Red indicatior
        console.insert(tk.END, 'The folder where the calibration images were saved was not selected\n\n')
        console.see('insert')
        messagebox.showerror('Error','The folder where the calibration images were saved was not selected!')
    else:
        folder_status.configure(bg = '#00cd00') # Green indicator
        console.insert(tk.END, f'Selected folder {selectionFolder.get()}\n\n')
        console.see('insert')
        fileNamesLeft = sorted(glob.glob(filename_selection+'\\Left\\*'))
        fileNamesRight = sorted(glob.glob(filename_selection + '\\Right\\*'))
        Format = fileNamesLeft[0].rsplit('.', 1)[1]
        Images = len(fileNamesLeft)
        Processed.set(f'0 of {Images}')
        console.insert(tk.END, f'{Images} images were found with .{Format} format\n\n')
        console.see('insert')
        format_image.set(f'.{Format}')
        folder_test = True

        # Draw and display the corners
        img_left = cv2.imread(fileNamesLeft[0])
        img_left = cv2.resize(img_left, (640, 480))
        cv.putText(img_left, f'MASTER CAMERA (L)', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                   cv.LINE_AA)
        imgleft = ImageTk.PhotoImage(Image.fromarray(img_left))
        canvas_left.imgleft = imgleft
        canvas_left.configure(image=imgleft)

        # Draw and display the corners
        img_right = cv2.imread(fileNamesRight[0])
        img_right = cv2.resize(img_right, (640, 480))
        cv.putText(img_right, f'SLAVE CAMERA (R)', (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                   cv.LINE_AA)
        imgright = ImageTk.PhotoImage(Image.fromarray(img_right))
        canvas_right.imgright = imgright
        canvas_right.configure(image=imgright)

########################################################################################################################
# Abort function
########################################################################################################################
def abort(abort_param):
    abort_param.set(True)

########################################################################################################################
# Calibration function
########################################################################################################################
def calibrate(menu, scan_status, canvas_text, progression, progression_bar, console,
              canvas_left, canvas_right, Selected, Rejected, Processed, darkbg, process_btn, abort_param, selectionFolder, SquareSize, TypeImg,  XChecker, YChecker, TypePattern):
    global k, rejected, patternSize, criteria, cancel_id, selected, imageSize
    global nImagesLeft, objpoints_left, imgpoints_left, left_image, objp_left, fileNamesLeft
    global nImagesRight, objpoints_right, imgpoints_right, right_image, objp_right, fileNamesRight

    abort_param.set(False)
    Rejected.set(rejected)
    Selected.set(selected)

    scan_status.configure(bg = '#ffa500') # Orange indicator

    # Define the background color:
    if darkbg.get() == 1:
        ret,left_image = cv.threshold(cv2.cvtColor(cv2.imread(fileNamesLeft[k]),cv2.COLOR_BGR2GRAY),0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        ret,right_image = cv.threshold(cv2.cvtColor(cv2.imread(fileNamesRight[k]),cv2.COLOR_BGR2GRAY),0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    else:
        left_image = cv2.cvtColor((cv2.imread(fileNamesLeft[k])), cv2.COLOR_BGR2GRAY)
        right_image = cv2.cvtColor((cv2.imread(fileNamesRight[k])), cv2.COLOR_BGR2GRAY)

    ret_left, corners_left = cv2.findChessboardCornersSB(left_image, (patternSize[0],patternSize[1]),flags=cv2.CALIB_CB_NORMALIZE_IMAGE  + cv2.CALIB_CB_EXHAUSTIVE  + cv2.CALIB_CB_ACCURACY );
    ret_right, corners_right = cv2.findChessboardCornersSB(right_image, (patternSize[0],patternSize[1]),flags=cv2.CALIB_CB_NORMALIZE_IMAGE  + cv2.CALIB_CB_EXHAUSTIVE  + cv2.CALIB_CB_ACCURACY );

    if ret_left == True and ret_right == True:

        objpoints_left.append(objp_left)
        corners_left2 =   cv2.cornerSubPix(left_image,corners_left,(23,23),(-1,-1),criteria)
        imgpoints_left.append(corners_left2)

        # Draw and display the corners
        img_left= cv2.cvtColor(left_image,cv2.COLOR_GRAY2RGB)
        img_left=cv2.drawChessboardCorners(img_left, (patternSize[0],patternSize[1]), corners_left2 ,ret_left)
        img_left = cv2.resize(img_left, (640, 480))
        cv.putText(img_left,f'MASTER CAMERA (L) - Image {k+1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv.LINE_AA)
        imgleft = ImageTk.PhotoImage (Image.fromarray (img_left))
        canvas_left.imgleft = imgleft
        canvas_left.configure(image = imgleft)

        objpoints_right.append(objp_right)
        corners_right2 =   cv2.cornerSubPix(right_image,corners_right,(23,23),(-1,-1),criteria)
        imgpoints_right.append(corners_right2)

        # Draw and display the corners
        img_right= cv2.cvtColor(right_image,cv2.COLOR_GRAY2RGB)
        img_right=cv2.drawChessboardCorners(img_right, (patternSize[0],patternSize[1]), corners_right2 ,ret_right)
        img_right = cv2.resize(img_right, (640, 480))
        cv.putText(img_right,f'SLAVE CAMERA (R) - Image {k+1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv.LINE_AA)
        imgright = ImageTk.PhotoImage (Image.fromarray (img_right))
        canvas_right.imgright = imgright
        canvas_right.configure(image = imgright)

        selected = selected + 1
        Selected.set(selected)
    else:

        img_left= cv2.cvtColor(left_image,cv2.COLOR_GRAY2RGB)
        img_left = cv2.resize(img_left, (640, 480))
        cv.putText(img_left,f'MASTER CAMERA (L) - Image {k+1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
        cv.putText(img_left,'REJECTED',(90,260),cv.FONT_HERSHEY_SIMPLEX,3,(255,0,0),1,cv.LINE_AA)
        imgleft = ImageTk.PhotoImage (Image.fromarray (img_left))
        canvas_left.imgleft = imgleft
        canvas_left.configure(image = imgleft)

        img_right= cv2.cvtColor(right_image,cv2.COLOR_GRAY2RGB)
        img_right = cv2.resize(img_right, (640, 480))
        cv.putText(img_right,f'SLAVE CAMERA (R) - Image {k+1}',(5,20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv.LINE_AA)
        cv.putText(img_right,'REJECTED',(90,260),cv.FONT_HERSHEY_SIMPLEX,3,(255,0,0),1,cv.LINE_AA)
        imgright = ImageTk.PhotoImage (Image.fromarray (img_right))
        canvas_right.imgright = imgright
        canvas_right.configure(image = imgright)

        rejected = rejected + 1
        Rejected.set(rejected)

    if k == nImagesLeft-1:

        Processed.set(f'{k+1} de {nImagesLeft}')
        console.insert(tk.END, 'The points were detected! Click on Calibrate button for stereo system calibration\n\n')
        console.see('insert')
        scan_status.configure(bg = '#00cd00') # Green indicator

        green_length = int(1117*((k+1)/nImagesLeft))
        progression.coords(progression_bar, 0, 0, green_length, 25); progression.itemconfig(canvas_text, text=f'{k+1} of {nImagesLeft} - {100*(k+1)/nImagesLeft:.2f}%')

        process_btn.configure(text='Scan points', fg='#282C34',
                              command=lambda: detect_points(menu, selectionFolder, SquareSize, TypeImg, XChecker,
                                                              YChecker, scan_status, progression, progression_bar,
                                                              console,
                                                              canvas_text, canvas_left, canvas_right, Selected,
                                                              Rejected,
                                                              Processed, TypePattern, darkbg, process_btn,
                                                              abort_param))
        console.see('insert')
        abort_param.set(False)

    else:
        if abort_param.get():
            process_btn.configure(text='Scan points', fg='#282C34', command=lambda: detect_points(menu, selectionFolder, SquareSize, TypeImg,  XChecker,
                                                                   YChecker, scan_status, progression, progression_bar, console,
                                                                   canvas_text, canvas_left, canvas_right, Selected, Rejected,
                                                                   Processed, TypePattern, darkbg, process_btn, abort_param))
            scan_status.configure(bg = '#00cd00') # Green indicator
            console.insert(tk.END, 'The process was aborted\n\n')
            console.see('insert')
            abort_param.set(False)
            return
        else:
            Processed.set(f'{k+1} of {nImagesLeft}')

            green_length = int(1117*((k+1)/nImagesLeft))
            progression.coords(progression_bar, 0, 0, green_length, 25); progression.itemconfig(canvas_text, text=f'{k+1} of {nImagesLeft} - {100*(k+1)/nImagesLeft:.2f}%')

            k = k + 1
            cancel_id = menu.after(2,calibrate(menu, scan_status, canvas_text, progression, progression_bar, console,
                  canvas_left, canvas_right, Selected, Rejected, Processed, darkbg, process_btn, abort_param, selectionFolder, SquareSize, TypeImg,  XChecker, YChecker, TypePattern))

########################################################################################################################
# Stereo calibration
########################################################################################################################
def stereo(console, calib_status):
    global k, rejected, patternSize, criteria, cancel_id, selected, imageSize
    global nImagesLeft, objpoints_left, imgpoints_left, left_image, objp_left, fileNamesLeft, imgpoints2_left, rvecs_left, tvecs_left, mtx_left, dist_left
    global nImagesRight, objpoints_right, imgpoints_right, right_image, objp_right, fileNamesRight, imgpoints2_right, rvecs_right, tvecs_right, mtx_right, dist_right
    global K1, D1, K2, D2, R, T, E, F, Mean_Left, Mean_Right

    try:
        objpoints_left
    except NameError:
        messagebox.showerror('Error','Detect all points before calibration!')
    else:

        console.insert(tk.END, 'Please wait\n\n')
        console.see('insert')

        calib_status.configure(bg = '#ffa500') # Orange indicator

        ret_left , mtx_left , dist_left ,  rvecs_left, tvecs_left = cv2.calibrateCamera(objpoints_left, imgpoints_left, left_image.shape[::-1], None, criteria)

        console.insert(tk.END, 'The master (L) camera was calibrated\n\n')
        console.see('insert')

        ret_right, mtx_right, dist_right,  rvecs_right, tvecs_right  = cv2.calibrateCamera(objpoints_right, imgpoints_right, right_image.shape[::-1], None, criteria)

        console.insert(tk.END, 'The slave (R) camera was calibrated\n\n')
        console.see('insert')

        TERMINATION_CRITERIA = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 15, 0.0001)
        ret, K1, D1, K2, D2, R, T, E, F = cv2.stereoCalibrate(
                objpoints_left, imgpoints_left, imgpoints_right,
                mtx_left, dist_left,
                mtx_right, dist_right,
                (imageSize[0], imageSize[1]), None, None,
                cv2.CALIB_FIX_INTRINSIC, TERMINATION_CRITERIA)

        console.insert(tk.END, 'The system was calibrated\n\n')
        console.see('insert')

        console.insert(tk.END, f'Intrinsic matrix of the master camera (L): \n{K1}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Lens distortion coefficients of the master camera (L):\n{D1}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Intrinsic matrix of the slave camera (R):\n{K2}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Lens distortion coefficients of the slave camera (R):\n{D2}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Rotation matrix (R):\n{R}\n\n')
        console.see('insert')
        console.insert(tk.END, f'Translation vector (T):\n{T}\n\n')
        console.see('insert')

        mean_error_left = 0
        mean_error_right = 0
        for i in range(len(objpoints_left)):
            imgpoints2_left, _ = cv2.projectPoints(objpoints_left[i], rvecs_left[i], tvecs_left[i], mtx_left, dist_left)
            error_left = cv2.norm(imgpoints_left[i],imgpoints2_left, cv2.NORM_L2)/len(imgpoints2_left)
            mean_error_left += error_left

        Mean_Left = mean_error_left/len(objpoints_left);
        console.insert(tk.END, f'Mean reprojection error of camera L: {mean_error_left/len(objpoints_left)}\n')
        console.see('insert')

        for i in range(len(objpoints_right)):
            imgpoints2_right, _ = cv2.projectPoints(objpoints_right[i], rvecs_right[i], tvecs_right[i], mtx_right, dist_right)
            error_right = cv2.norm(imgpoints_right[i],imgpoints2_right, cv2.NORM_L2)/len(imgpoints2_right)
            mean_error_right += error_right

        Mean_Right = mean_error_right / len(objpoints_right);
        console.insert(tk.END, f'Mean reprojection error of camera R: {mean_error_right/len(objpoints_right)}\n\n')
        console.see('insert')

        calib_status.configure(bg = '#00cd00') # Green indicator

########################################################################################################################
# Plot the reprojection error
########################################################################################################################
def result(result_status):
    global k, rejected, patternSize, criteria, cancel_id, selected, imageSize
    global nImagesLeft, objpoints_left, imgpoints_left, left_image, objp_left, fileNamesLeft, imgpoints2_left, rvecs_left, tvecs_left, mtx_left, dist_left
    global nImagesRight, objpoints_right, imgpoints_right, right_image, objp_right, fileNamesRight, imgpoints2_right, rvecs_right, tvecs_right, mtx_right, dist_right
    global Mean_Left, Mean_Right

    # Current directory:
    CurrentDir = os.path.dirname(os.path.realpath(__file__))

    try:
        tvecs_left
    except NameError:
        messagebox.showerror('Error','Perform the calibration before plotting the results!')
    else:

        fig, fig1 = plt.subplots(num='Reprojection error of the calibrated system')
        thismanager = plt.get_current_fig_manager()
        # thismanager.window.wm_iconbitmap(CurrentDir+'/static/iCorrVision-3D Calibration.ico')

        for i, op in enumerate(objpoints_left):
            ip2 = cv2.projectPoints(op, rvecs_left[i], tvecs_left[i], mtx_left, dist_left)[0]
            p1 = (ip2 - imgpoints_left[i]).reshape(2, -1)
            fig1.scatter(p1[0], p1[1], s=2, color='red', alpha=0.5)

        for i, op in enumerate(objpoints_right):
            ip2 = cv2.projectPoints(op, rvecs_right[i], tvecs_right[i], mtx_right, dist_right)[0]
            p2 = (ip2 - imgpoints_right[i]).reshape(2, -1)
            fig1.scatter(p2[0], p2[1], s=2, color='blue', alpha=0.5)

        fig1.plot(Mean_Left, Mean_Left, 'r+')
        fig1.plot(Mean_Right, Mean_Right, 'b+')

        pontos = [];
        pontos.append(np.absolute(p1[0]))
        pontos.append(np.absolute(p1[1]))
        pontos.append(np.absolute(p2[0]))
        pontos.append(np.absolute(p2[1]))

        pontoslabel = math.ceil(np.max(pontos)) + 0.5

        result_status.configure(bg = '#00cd00') # Green indicator

        ax = plt.gca()
        ax.set_ylim([-pontoslabel,pontoslabel])
        ax.set_xlim([-pontoslabel,pontoslabel])
        ax.set_xticklabels(ax.get_xticks(), fontname='Times New Roman',fontsize=14)
        ax.set_yticklabels(ax.get_yticks(), fontname='Times New Roman',fontsize=14)
        plt.xlabel('Pixels',fontname='Times New Roman',fontsize=14)
        plt.ylabel('Pixels',fontname='Times New Roman',fontsize=14)
        ax.set_aspect('equal')
        plt.show()

########################################################################################################################
# Function to detect the calibration points
########################################################################################################################
def detect_points(menu, selectionFolder, SquareSize, TypeImg,  XChecker, YChecker, scan_status, progression,
                    progression_bar, console, canvas_text, canvas_left, canvas_right, Selected, Rejected,
                    Processed, TypePattern, darkbg, process_btn, abort_param):
    global k, rejected, patternSize, criteria, cancel_id, selected, imageSize, folder_test
    global nImagesLeft, objpoints_left, imgpoints_left, left_image, objp_left, fileNamesLeft
    global nImagesRight, objpoints_right, imgpoints_right, right_image, objp_right, fileNamesRight

    # Current directory:
    CurrentDir = os.path.dirname(os.path.realpath(__file__))

    try:
        folder_test
    except NameError:
        messagebox.showerror('Error','Select the folder where the calibration images were saved before scanning the points!')
    else:

        if TypePattern.get() == 'Checkerboard':

            calibrationFolder = CurrentDir
            patternSize = [XChecker.get(),YChecker.get()];

            pathLeft =   selectionFolder.get()+'/Left/'
            pathRight = selectionFolder.get()+'/Right/'

            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 0.0001)

            # prepare object points, (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
            objp_left  = np.zeros((patternSize[0]*patternSize[1],3), np.float32);  objp_left[:,:2] = np.mgrid[0:patternSize[0],0:patternSize[1]].T.reshape(-1,2)*SquareSize.get()
            objp_right = np.zeros((patternSize[0]*patternSize[1],3), np.float32); objp_right[:,:2] = np.mgrid[0:patternSize[0],0:patternSize[1]].T.reshape(-1,2)*SquareSize.get()

            # Arrays to store object points and image points from all the images.
            objpoints_left = [] # 3d point in real world space
            objpoints_right = [] # 3d point in real world space
            imgpoints_left = [] # 2d points in image plane.
            imgpoints_right = [] # 2d points in image plane.

            fileNamesLeft = sorted(glob.glob(pathLeft+'*'+TypeImg.get()))
            fileNamesRight = sorted(glob.glob(pathRight+'*'+TypeImg.get()))
            nImagesLeft = len(fileNamesLeft)
            nImagesRight = len(fileNamesRight)

            imageSize = np.flip(cv2.cvtColor(cv2.imread(fileNamesLeft[0]),cv2.COLOR_BGR2GRAY).shape)

            rejected = 0

            selected = 0

            k = 0

            process_btn.configure(text='Abort', fg='#cc0000', command=lambda: abort(abort_param))

            t2 = Thread(target=calibrate,
                        args=(menu, scan_status, canvas_text, progression, progression_bar, console,
                              canvas_left, canvas_right, Selected, Rejected, Processed, darkbg, process_btn, abort_param, selectionFolder, SquareSize, TypeImg,  XChecker, YChecker, TypePattern))
            t2.setDaemon(True)
            t2.start()

        else:
            messagebox.showerror('Error',
                                 'Check if the pattern type is correct!')

########################################################################################################################
# Close GUI
########################################################################################################################
def close(menu):
    ans = messagebox.askquestion('Close', 'Are you sure you want to exit iCorrVision-3D Calibration module?',
                                 icon='question')
    if ans == 'yes':

        plt.close()
        menu.destroy()
        menu.quit()

########################################################################################################################
# Save object function
########################################################################################################################
def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output)

########################################################################################################################
# Save calibration file
########################################################################################################################
def save(menu, console, save_status, canvas_right, canvas_left, folder_status, calib_status, result_status,
         scan_status, progression, progression_bar, canvas_text, Processed, Rejected, Selected, rotbtn, eulerbtn):
    global K1, D1, K2, D2, R, T, E, F
    global selectionFolder, filename_selection, folder_test
    global k, rejected, patternSize, criteria, cancel_id, selected, imageSize
    global nImagesLeft, objpoints_left, imgpoints_left, left_image, objp_left, fileNamesLeft, imgpoints2_left, rvecs_left, tvecs_left, mtx_left, dist_left
    global nImagesRight, objpoints_right, imgpoints_right, right_image, objp_right, fileNamesRight, imgpoints2_right, rvecs_right, tvecs_right, mtx_right, dist_right

    try:
        K1
    except NameError:
        messagebox.showerror('Error','Perform calibration before saving!')
    else:
        filename_save = filedialog.asksaveasfilename()

        if not filename_save:
            save_status.configure(bg = 'red') # Red indicator
            console.insert(tk.END, 'The calibration file was not selected!\n\n')
            console.see('insert')
            messagebox.showerror('Error','The calibration file was not selected!')
        else:
            if rotbtn.get() == 1:
                calib_result = [('iCorrVision-3D Calibration - Rotation matrix 0 - Euler angles 1', 0),
                                ('CamL_F0 [px]', K1[0,0]),
                                ('CamL_F1 [px]', K1[1,1]),
                                ('CamL_Fs [px]', K1[0,1]),
                                ('CamL_C0 [px]', K1[0,2]),
                                ('CamL_C1 [px]', K1[1,2]),
                                ('CamL_K1     ', D1[0,0]),
                                ('CamL_K2     ', D1[1,0]),
                                ('CamL_k3     ', D1[4,0]),
                                ('CamL_P1     ', D1[2,0]),
                                ('CamL_P2     ', D1[3,0]),
                                ('CamR_F0 [px]', K2[0, 0]),
                                ('CamR_F1 [px]', K2[1, 1]),
                                ('CamR_Fs [px]', K2[0, 1]),
                                ('CamR_C0 [px]', K2[0, 2]),
                                ('CamR_C1 [px]', K2[1, 2]),
                                ('CamR_K1     ', D2[0, 0]),
                                ('CamR_K2     ', D2[1, 0]),
                                ('CamR_k3     ', D2[4, 0]),
                                ('CamR_P1     ', D2[2, 0]),
                                ('CamR_P2     ', D2[3, 0]),
                                ('T0 [mm]     ', T[0,0]),
                                ('T1 [mm]     ', T[1,0]),
                                ('T2 [mm]     ', T[2,0]),
                                ('R00         ', R[0,0]),
                                ('R01         ', R[0,1]),
                                ('R02         ', R[0,2]),
                                ('R10         ', R[1,0]),
                                ('R11         ', R[1,1]),
                                ('R12         ', R[1,2]),
                                ('R20         ', R[2,0]),
                                ('R21         ', R[2,1]),
                                ('R22         ', R[2,2])]
            elif eulerbtn.get() == 1:

                ANGLE = rotate.from_matrix(R).as_euler('xyz', degrees=True)

                calib_result = [('iCorrVision-3D Calibration - Rotation matrix 0 - Euler angles 1', 1),
                                ('CamL_F0 [px]', K1[0,0]),
                                ('CamL_F1 [px]', K1[1,1]),
                                ('CamL_Fs [px]', K1[0,1]),
                                ('CamL_C0 [px]', K1[0,2]),
                                ('CamL_C1 [px]', K1[1,2]),
                                ('CamL_K1     ', D1[0, 0]),
                                ('CamL_K2     ', D1[1, 0]),
                                ('CamL_k3     ', D1[4, 0]),
                                ('CamL_P1     ', D1[2, 0]),
                                ('CamL_P2     ', D1[3, 0]),
                                ('CamR_F0 [px]', K2[0, 0]),
                                ('CamR_F1 [px]', K2[1, 1]),
                                ('CamR_Fs [px]', K2[0, 1]),
                                ('CamR_C0 [px]', K2[0, 2]),
                                ('CamR_C1 [px]', K2[1, 2]),
                                ('CamR_K1     ', D2[0, 0]),
                                ('CamR_K2     ', D2[1, 0]),
                                ('CamR_k3     ', D2[4, 0]),
                                ('CamR_P1     ', D2[2, 0]),
                                ('CamR_P2     ', D2[3, 0]),
                                ('T0 [mm]     ', T[0,0]),
                                ('T1 [mm]     ', T[1,0]),
                                ('T2 [mm]     ', T[2,0]),
                                ('Theta [deg] ', ANGLE[0]),
                                ('Phi [deg]   ', ANGLE[1]),
                                ('Psi [deg]   ', ANGLE[2])]

            with open(filename_save, 'w', newline='') as f:
                writer_object = csv.writer(f, delimiter=';')
                writer_object.writerows(calib_result)
                f.close()

            console.insert(tk.END, f'The calibration results were saved in {filename_save}\n\n')
            console.see('insert')
            save_status.configure(bg = '#00cd00') # Green indicator

            ans1 = messagebox.askquestion('Clear','Do you want to perform another calibration?',icon ='question')
            if ans1 == 'yes':
                # Current directory:
                CurrentDir = os.path.dirname(os.path.realpath(__file__))

                image_black = Image.open(CurrentDir+'\static\ImageBlack.tiff')
                image_black = image_black.resize((640, 480), Image.ANTIALIAS)
                image_black_re = ImageTk.PhotoImage(image_black)
                canvas_right.image_black_re = image_black_re
                canvas_right.configure(image = image_black_re)
                canvas_left.image_black_re = image_black_re
                canvas_left.configure(image = image_black_re)
                save_status.configure(bg = 'red') # Red indicator
                folder_status.configure(bg = 'red') # Red indicator
                calib_status.configure(bg = 'red') # Red indicator
                result_status.configure(bg = 'red') # Red indicator
                scan_status.configure(bg = 'red') # Red indicator
                progression.coords(progression_bar, 0, 0, 0, 25); progression.itemconfig(canvas_text, text='')
                console.delete('1.0', END)
                del K1, D1, K2, D2, R, T, E, F
                del filename_selection, folder_test
                del k, rejected, patternSize, criteria, cancel_id, selected, imageSize
                del nImagesLeft, objpoints_left, imgpoints_left, left_image, objp_left, fileNamesLeft, imgpoints2_left, rvecs_left, tvecs_left, mtx_left, dist_left
                del nImagesRight, objpoints_right, imgpoints_right, right_image, objp_right, fileNamesRight, imgpoints2_right, rvecs_right, tvecs_right, mtx_right, dist_right
                Processed.set('0 of 0')
                Rejected.set(0)
                Selected.set(0)

            else:
                close(menu)