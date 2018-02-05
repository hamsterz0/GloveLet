'''
*****************************************
@author: Arnav Garg
@date: Oct 11, 2017

Computer Vision for finger(s) tracking
*****************************************
'''
import cv2
import numpy as np
import tkinter
import threading
import pyautogui
import pdb
import math


class VisionTracking(object):
 
    THRESHOLD_MAX = 255
    THRESHOLD_MIN = 0
    SCREEN_UPDATE_TIME = 3
    FINGER_1 = 1
    FINGER_2 = 2
    LEFTCLICK_DELAY = 2
    PINCH_RIGHT = 70

    def __init__(self):
        """
        Initializing the member variables.
        """
        self.threshold_finger1 = None
        self.threshold_finger2 = None
        self.screen_width = 0
        self.screen_height = 0
        self.camera = None
        self.smoothness = 8
        self.window_fing1 = []
        self.window_fing2 = []
        pyautogui.FAILSAFE = False
        self.finger1_posX = 0
        self.finger1_posY = 0
        self.finger2_posX = 0
        self.finger2_posY = 0
        self.mouseInit_X = 0
        self.mouseInit_Y = 0
        self.mouseFinal_X = 0
        self.mouseFinal_Y = 0
        self.mousePoint_X = 0
        self.mousePoint_Y = 0
        self.pre_X = 0
        self.pre_Y = 0
        self.dx = 0
        self.dy = 0
        self.tempX = 0
        self.tempY = 0
        self.motionEnable = False
        self.leftClickWC = 0
        self.pinch = False
        self.frame = 0
        self.buttonPress = False

    def __callback(self, value):
        """
        Placeholder method just used to pass to a cv2 function. 
        """
        pass

    def __config_saved(self):
        try:
            line = []
            with open('.vision.conf', 'r') as file:
                for values in file:
                    line.append(values)
            self.threshold_finger1 = [int(x) for x in line[0].split(',')]
            self.threshold_finger2 = [int(x) for x in line[1].split(',')]
        except IOError:
            return False
        return True

    def __createTrackbar(self):
        """
        Used for creating the trackbar for calculating the range
        values for the threshold for the user's color. 
        """
        # Creating a trackbar. 
        cv2.namedWindow('Calibrate', 0)
        for bound in ['MIN', 'MAX']:
            if bound == 'MIN':
                value = self.THRESHOLD_MIN
            else:
                value = self.THRESHOLD_MAX

            for valueType in ['Hue', 'Sat', 'Value']:
                cv2.createTrackbar('%s (%s)' % (valueType, bound),
                                  'Calibrate',
                                  value,
                                  self.THRESHOLD_MAX, 
                                  self.__callback)

    def __getMinMaxValues(self):
        """
        This method would return the min and max HSV threshold values
        that the user has selected. 
        """
        values = []
        for bound in ["MIN", "MAX"]:
            for valueType in ['Hue', 'Sat', 'Value']:
                val = cv2.getTrackbarPos('%s (%s)' % (valueType, bound),
                                        'Calibrate')
                values.append(val)
        return values

    def __rangeDetector(self, finger_num):
        """
        Master function for calling the CV Trackbar GUI to select the threshold 
        values for the threshold for the user selected colors. 
        This function would call the __createTrackbar and __getMinMaxValues function
        to create the GUI and get the values from the GUI respectively.  
        """

        self.__createTrackbar()
        while True:
            ret, img = self.camera.read()   # getting the return value and the frame.
            # Error handling
            if not ret:
                break
            
            frame_thresh = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # converting to HSV colorscale.
            threshold = self.__getMinMaxValues()
            [hmin, smin, vmin, hmax, smax, vmax] = threshold
            min_values = (hmin, smin, vmin)
            max_values = (hmax, smax, vmax)

            frame_thresh = cv2.inRange(frame_thresh, min_values, max_values)    # adding the user selected thresh.
            cv2.imshow("Frames", frame_thresh)

            if cv2.waitKey(1) & 0xFF is ord('q'):
                break
        if finger_num == 1:
            self.threshold_finger1 = threshold
            with open('.vision.conf', 'a') as file:
                file.write('{},{},{},{},{},{}\n'.format(*self.threshold_finger1))
        else:
            self.threshold_finger2 = threshold
            with open('.vision.conf', 'a') as file:
                file.write('{},{},{},{},{},{}'.format(*self.threshold_finger2))

        cv2.destroyAllWindows()

    def __selectWebCam(self):
        """
        This function will let the user select which webcam he wants to collect
        the data from. 
        """
        # TODO: For now using the default camera.
        self.camera = cv2.VideoCapture(1)

    def __findScreenSize(self):
        root = tkinter.Tk()
        root.withdraw()
        self.screen_width, self.screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        self.mouseFinal_X = self.screen_width/2
        self.mouseFinal_Y = self.screen_height/2


    def __frameOperations(self, mask):
        kernel = np.ones((5,5), np.uint8)
        frame = cv2.erode(mask, kernel, iterations=2)
        frame = cv2.dilate(mask, kernel, iterations=2)
        frame = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        frame = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return frame

    def __track_object(self, frame, finger_num):
        # contours = cv2.findContours(frame, 1, 2)
        # cnt = contours[0]
        # M = cv2.moments(cnt)

        cnts = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        posX = 0
        posY = 0
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            """
            Type of data returned by cv2.moments. 
            {'nu12': 2.429873851311728e-06, 'mu12': 1381809220.850586, 'm11': 25132807395.0, 
            'm30': 57909074053770.0, 'm01': 60077235.0, 
            'mu11': 85381234.61649323, 'm21': 10519418922885.0, 'nu21': 5.220555276767182e-07, 
            'nu03': -1.9641993131654756e-06, 'nu02': 0.0012610491682499118, 
            'mu21': 296880079.4124689, 'm03': 520824457515.0, 'mu20': 68320922.18600464, 
            'nu11': 0.00013411302032940116, 'm12': 2234892975645.0, 'nu30': 8.039795096010302e-09, 
            'm10': 332658720.0, 'm02': 5326324995.0, 'm20': 138760534800.0, 
            'mu02': 802829841.8216686, 'nu20': 0.00010731544545134859, 'mu03': -1116991617.0978394,
             'm00': 797895.0, 'mu30': 4572032.8203125}
            """
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
            moment00 = int(M['m00'])
            moment01 = int(M['m01'])
            moment10 = int(M['m10'])
            posX = moment10/moment00
            posY = moment01/moment00
            marker = True
            # print(moment00)
            # if moment00 > 20000 and moment00 < 20000000:
            #     posX = moment10/moment00
            #     posY = moment01/moment00
            #     marker = True
            # else:
            #     marker = False
        else:
            marker = False
        return [marker, posX, posY]

    def __move_mouse(self):
        mouseFlag = False
        self.dx = pow((self.mousePoint_X - self.mouseInit_X), 2)
        self.dy = pow((self.mousePoint_Y - self.mouseInit_Y), 2)
        r2 = pow(self.smoothness, 2)

        if (self.dx+self.dy) >= r2:
            mouseFlag = True
        else:
            mouseFlag = False

        if mouseFlag:
            self.mousePoint_X = self.mouseInit_X
            self.mousePoint_Y = self.mouseInit_Y
            mouseFlag = False

    def __pre_click(self):
        self.pinch = 0
        fingers_dist = math.sqrt( pow((self.finger2_posX - self.mouseInit_X), 2) + pow((self.finger2_posY - self.mouseInit_Y), 2) )
        # print('{} {}'.format(fingers_dist, self.PINCH_RIGHT))
        if fingers_dist < self.PINCH_RIGHT:
            self.pinch = True
        else:
            self.pinch = False

    def __calculate_window_avg(self):
        X = 0
        Y = 0
        for [x, y] in self.window_fing1:
            X += x
            Y += y
        X = X/len(self.window_fing1)
        Y = Y/len(self.window_fing1)
        return X, Y 

    def __track(self):
        ret, self.frame = self.camera.read()
        self.frame = cv2.flip(self.frame, 1)    # flipping the frame vertically.
        frame_rows, frame_cols, tmp = self.frame.shape
        # frameRGB = cv2.cvtColor(frame, cv2.RGB2BGR)
        frameHSV = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        lower_threshold_f1 = np.array(self.threshold_finger1[:3])
        upper_threshold_f1 = np.array(self.threshold_finger1[3:])

        lower_threshold_f2 = np.array(self.threshold_finger2[:3])
        upper_threshold_f2 = np.array(self.threshold_finger2[3:])

        mask_f1 = cv2.inRange(frameHSV, lower_threshold_f1, upper_threshold_f1)
        mask_f2 = cv2.inRange(frameHSV, lower_threshold_f2, upper_threshold_f2)
        frame_f1 = self.__frameOperations(mask_f1)
        frame_f2 = self.__frameOperations(mask_f2)
        frame = self.__frameOperations(mask_f2)
        frame = self.__frameOperations(mask_f1)

        marker1, self.finger1_posX, self.finger1_posY = self.__track_object(frame_f1, self.FINGER_1)
        marker2, self.finger2_posX, self.finger2_posY = self.__track_object(frame_f2, self.FINGER_2)

        self.window_fing1.append([self.finger1_posX, self.finger1_posY])

        if len(self.window_fing1) <= 3:
            return
        else:
            self.finger1_posX, self.finger1_posY = self.__calculate_window_avg()
            self.window_fing1 = []

        self.mouseInit_X = self.finger1_posX
        self.mouseInit_Y = self.finger1_posY

        if marker1:
            self.__move_mouse()
            if not self.motionEnable:
                self.pre_x = self.mousePoint_X
                self.pre_Y = self.mousePoint_Y
                self.motionEnable = True
            else:
                self.dx = self.mousePoint_X
                self.dy = self.mousePoint_Y
                self.mouseFinal_X = self.dx * (self.screen_width/(frame_cols*1))
                self.mouseFinal_Y = self.dy * (self.screen_height/(frame_cols*1))
                if self.mouseFinal_X > self.screen_width:
                    self.mouseFinal_X = self.screen_width
                elif self.mouseFinal_Y > self.screen_height:
                    self.mouseFinal_Y = self.screen_height
                self.pre_X = self.mousePoint_X
                self.pre_Y = self.mouseFinal_Y
            if self.mouseFinal_X != 0 and self.mouseFinal_Y != 0:
                pyautogui.moveTo(self.mouseFinal_X, self.mouseFinal_Y)
        if marker2:
            self.__pre_click()
            if self.pinch:
                pyautogui.click()
                self.buttonPress = False
            

        # print('W: {}, H: {}'.format(frame.shape[1], frame.shape[0]))
        
        # contours = cv2.findContours(frame_f1, 1, 2)
        # cnt = contours[0]
        # M = cv2.moments(cnt)

        # cv2.imshow("Mask", mask_f1)
        
        # cv2.imshow("Frame", frame_f2)

    def get_coordinates(self):
        """
        Main function from where the tracking would begin.
        The main function that the public can call. 
        """
        # Running the webcam to collect the data. 
        self.__selectWebCam()
        self.__findScreenSize()
        # Running the range detector
        # This would be used for now to calibrate.
        # for finger 1. 

        if not self.__config_saved():
            self.__rangeDetector(self.FINGER_1)
            # range for finger 2
            self.__rangeDetector(self.FINGER_2)

        # Calling the vision tracking process every x seconds
        while True:
            self.__track()
            # threading.Timer(self.SCREEN_UPDATE_TIME, self.__track).start()
            if cv2.waitKey(1) & 0xFF is ord('q'):
                break
        cv2.destroyAllWindows()

