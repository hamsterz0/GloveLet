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

class VisionTracking(object):
 
    THRESHOLD_MAX = 255
    THRESHOLD_MIN = 0
    SCREEN_UPDATE_TIME = 5

    def __init__(self):
        """
        Initializing the member variables.
        """
        self.threshold = None
        self.screen_width = 0
        self.screen_height = 0
        self.posX = 0
        self.posY = 0
        self.camera = None

    def __callback(self, value):
        """
        Placeholder method just used to pass to a cv2 function. 
        """
        pass

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

    def __rangeDetector(self):
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
            self.threshold = self.__getMinMaxValues()
            [hmin, smin, vmin, hmax, smax, vmax] = self.threshold
            min_values = (hmin, smin, vmin)
            max_values = (hmax, smax, vmax)

            frame_thresh = cv2.inRange(frame_thresh, min_values, max_values)    # adding the user selected thresh.
            cv2.imshow("Frames", frame_thresh)

            if cv2.waitKey(1) & 0xFF is ord('q'):
                break

    def __selectWebCam(self):
        """
        This function will let the user select which webcam he wants to collect
        the data from. 
        """
        # TODO: For now using the default camera.
        self.camera = cv2.VideoCapture(0)

    def __findScreenSize():
        root = tkinter.Tk()
        root.withdraw()
        self.width, self.height = root.winfo_screenwidth(), root.winfo_screenheight()

    def __track(self):
        print('Hello, World!')

    def getCoordinates(self):
        """
        Main function from where the tracking would begin.
        The main function that the public can call. 
        """
        # Running the webcam to collect the data. 
        self.__selectWebCam()
        # Running the range detector
        # This would be used for now to calibrate. 
        # self.__rangeDetector()
        # Calling the vision tracking process every x seconds
        threading.Timer(self.SCREEN_UPDATE_TIME, self.__track).start()
