import numpy as np
import tkinter
import argparse
import pyautogui
import math
from glovelet.utility.timeseries import DataTimeSeries
from glovelet.utility.motion_multiplier import motion_multiplier
import logging
from ast import literal_eval
import sys
import cv2
from glovelet.vision.gesture import Gesture
from glovelet.vision.gestureAPI import PreDefinedGestures
from glovelet.eventapi.event import EventAPIException

def callback(value):
    pass


class Vision:
    WINDOW_SIZE = 4  # The window size for calculating hte average
    PREV_MEMORY = 2  # Previous points stored.

    def __init__(self):
        pyautogui.FAILSAFE = False
        root = tkinter.Tk()
        root.withdraw()
        # member variables
        self.webcam = cv2.VideoCapture(0)
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.cameraWidth = self.screen_width / 2
        self.cameraHeight = self.screen_height / 2
        self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraWidth)
        self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraHeight)
        self.output = {}
        self.handContour = {}
        self.canvas = None
        self.handMoment = {}
        self.foundContour = {}
        self.realX = {}
        self.realY = {}
        self.stationary = {}
        self.mouseX = self.screen_width/2
        self.mouseY = self.screen_height/2
        self.queue = []
        self.clickThresh = 45
        self.pinched = False
        self.window = {}
        self.movement_history = {}
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-r', '--find_range',
                                 help="Find the range from within the program",
                                 action="store_true", default=False)
        self.args = self.parser.parse_args()
        self.record = {}
        self.gesture_points = []
        self.can_do_gesture = False
        self.boundaries = {}
        self.init_mem_vars()
        self.handMoment = (0, 0)
        self.foundContour = True
        self.stationary = False
        self.record = False
        self.realX = 0
        self.realY = 0
        self.movement_history = []
        self.window = DataTimeSeries(
                self.WINDOW_SIZE, 2, auto_filter=True)
        self.init_gestures()

    def init_mem_vars(self):
        if not self.args.find_range:
            with open('.vision.config', 'w') as file:
                value = self.find_range()
                self.boundaries = value
                file.write('{}\n'.format(str(value)))
        else:
            try:
                with open('.vision.config', 'r') as file:
                    for line in file:
                        values = literal_eval(line)
                        self.boundaries = values
            except IOError:
                print('Config file not found. Run the program with -r flag.')
                sys, exit()
            except Exception:
                print('Not all the fingers have colors configured. Run with -r flag')
                sys.exit()

    def init_gestures(self):
        self.defined_gestures = PreDefinedGestures()
        self.gestures = self.defined_gestures.predefined_gestures
        self.gesture_names = []
        for gesture in self.gestures:
            self.gesture_names.append(gesture.name)

    def find_range(self):
        range_filter = 'HSV'
        cv2.namedWindow("Trackbar", 0)
        for i in ["MIN", "MAX"]:
            v = 0 if i == "MIN" else 255
            for j in range_filter:
                cv2.createTrackbar("%s_%s" %
                                   (j, i), "Trackbar", v, 255, callback)
        while True:
            _, image = self.webcam.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            values = []
            for i in ["MIN", "MAX"]:
                for j in range_filter:
                    v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbar")
                    values.append(v)
            lower = (values[:3])
            upper = (values[3:])
            thresh = cv2.inRange(image, tuple(lower), tuple(upper))
            # layout = np.vstack((thresh, image))
            cv2.imshow('Thresh', thresh)
            # cv2.imshow('Image', image)
            if cv2.waitKey(1) & 0xFF is ord('q'):
                cv2.destroyAllWindows()
                return tuple([lower, upper])

    def read_webcam(self):
        _, self.frame = self.webcam.read()
        self.frame = cv2.flip(self.frame, 1)
        # for finger in self.ACTIVE_FINGERS:
        self.canvas = np.zeros(self.frame.shape, np.uint8)
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

    def threshold(self):
        (lower, upper) = self.boundaries
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(self.frame, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        self.output = cv2.bitwise_and(
            self.frame, self.frame, mask=mask)
        self.output = cv2.cvtColor(
            self.output, cv2.COLOR_BGR2GRAY)
        self.output = cv2.erode(
            self.output, kernel, iterations=1)
        self.output = cv2.dilate(
            self.output, kernel, iterations=3)

    def extract_contours(self):
        _, self.contours, _ = cv2.findContours(
            self.output.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        maxArea, idx = 0, 0
        if len(self.contours) == 0:
            self.foundContour = False
            return
        else:
            self.foundContour = True

        for i in range(len(self.contours)):
            area = cv2.contourArea(self.contours[i])
            if area > maxArea:
                maxArea = area
                idx = i
        self.realHandContour = self.contours[idx]
        self.realHandLength = cv2.arcLength(self.realHandContour, True)
        self.handContour = cv2.approxPolyDP(
            self.realHandContour, 0.001 * self.realHandLength, True)

    def __check_stationary(self):
        search_len = 3
        val = -1 * (search_len + 1)
        self.prev_record_state = self.record
        if self.can_do_gesture:
            xPoints = [pt[0] for pt in self.movement_history[val:-1]]
            yPoints = [pt[1] for pt in self.movement_history[val:-1]]
            xAvg = np.average(xPoints)
            yAvg = np.average(yPoints)
            factor = 0.04
            for [x, y] in self.movement_history[-(search_len + 1):-1]:
                if (x-xAvg)**2 + (y-yAvg) > factor * \
                                                min(self.cameraWidth, self.cameraHeight):
                    if self.stationary:
                        self.record = True
                    self.stationary = False
                    return
            if not self.stationary:
                self.record = False
            self.stationary = True

    def find_center(self):
        self.moments = cv2.moments(self.handContour)
        if self.moments["m00"] != 0:
            self.handX = int(self.moments["m10"] / self.moments["m00"])
            self.handY = int(self.moments["m01"] / self.moments["m00"])
            self.handMoment = (self.handX, self.handY)

    def normalize_center(self):
        self.window.add(self.handMoment)
        self.realX, self.realY = self.window[0]
        #  print('{}'.format(self.window.timestamp[0]))
        self.movement_history += [(self.realX, self.realY)]
        self.__check_stationary()

    def move_cursor(self):
        x = self.realX * (self.screen_width / self.frame.shape[1])
        y = self.realY * (self.screen_height / self.frame.shape[0])
        # pyautogui.moveTo(x, y)
        return (x, y)

    def check_can_perform_gesture(self):
        if len(self.movement_history) > 10:
            self.can_do_gesture = True
        else:
            self.can_do_gesture = False

    def find_gesture(self):
        min_error = 2**31 - 1
        min_error_idx = -1
        self.human_gesture = Gesture(self.gesture_points,"Human Gesture")
        likelihoodscores = [0]*len(self.gestures)
        assessments = [{}] * len(self.gestures)
        for i in range(len(self.gestures)):
            assessments[i] = Gesture.compare_gesture(self.gestures[i],
                                                  self.human_gesture)
        error_list = [assessments[i]['totalError'] for i in range(len(assessments))]
        index = error_list.index(min(error_list))
        template_gesture_ratio = max((self.gestures[index].distance / self.human_gesture.distance),
                                     (self.human_gesture.distance / self.gestures[index].distance))
        distance_diff_ratio = assessments[index]['totalDistance'] / min(self.gestures[index].distance,
                                                                        self.human_gesture.distance)
        if template_gesture_ratio < 2.2 and distance_diff_ratio < 30:
            return index

    def determine_if_gesture(self):
        if self.record:
            self.gesture_points += [self.movement_history[-1]]
        elif self.prev_record_state == True and not self.record:
            min_gesture_points = 5
            if len(self.movement_history) > min_gesture_points:
                gesture_index = self.find_gesture()
                if gesture_index != None:
                    print('Gesture Performed: {}'.format(self.gesture_names[gesture_index]))
            self.gesture_points = []

    def draw(self):
        cv2.drawContours(
            self.canvas, [self.handContour], 0, (0, 255, 0), 1)
        cv2.circle(self.canvas, tuple([self.realX, self.realY]),
                   10, (255, 0, 0), -2)
        recent_positions = self.movement_history[-30:]
        if len(recent_positions) != 0:
            for i in range(len(recent_positions)):
                cv2.circle(self.canvas, recent_positions[i], 5,
                           (25*i, 255, 25*i), -1)

    def frame_outputs(self):
        #  cv2.imshow('Output ', self.output)
        #  cv2.imshow('Frame', self.frame)
        cv2.imshow('Canvas', self.canvas)
        pass

    def check_exit(self):
        if cv2.waitKey(1) & 0xFF is ord('q'):
            cv2.destroyAllWindows()
            raise EventAPIException('YOU DONE BAD.')

    def start_process(self):
        """start_process
        This is where all the functions for tracking the fingers and
        movement are called. This is the master function.
        """
        while True:
            self.read_webcam()
            self.threshold()
            self.extract_contours()
            if self.foundContour:
                self.find_center()
                self.normalize_center()
            else:
                self.stationary = True
            self.draw()
            self.frame_outputs()
            #  self.check_can_perform_gesture()
            #  self.determine_if_gesture()
            x, y = self.move_cursor()
            # Exit out of this hell hole.
            if cv2.waitKey(1) & 0xFF is ord('q'):
                break
        cv2.destroyAllWindows()

    '''**************** METHODS BELOW ARE FOR HAND PALM TRACKING ****************'''

    def __get_contour_dimensions(self):
        self.minX, self.minY, self.handWidth, self.handHeight = \
            cv2.boundingRect(self.handContour)

    def __calculate_convex_hull(self):
        self.convexHull = cv2.convexHull(self.handContour, returnPoints=False)
        self.hullPoints = [self.handContour[i[0]] for i in self.convexHull]
        self.hullPoints = np.array(self.hullPoints, dtype=np.int32)
        self.defects = cv2.convexityDefects(self.handContour, self.convexHull)

    def __ecludian_space_reduction(self):
        scaleFactor = 0.3
        reducedSize = np.array(self.handContour * scaleFactor, dtype=np.int32)
        tx, ty, w, h = cv2.boundingRect(reducedSize)
        maxPoint = None
        maxRadius = 0
        for x in range(w):
            for y in range(h):
                radius = cv2.pointPolygonTest(reducedSize, (tx+x, ty+y), True)
                if radius > maxRadius:
                    maxPoint = (tx+x, ty+y)
                    maxRadius = radius
        realCenter = np.array(np.array(maxPoint) / scaleFactor, dtype=np.int32)
        error = int((1 / scaleFactor) * 1.5)
        maxPoint = None
        maxRadius = 0
        for x in range(realCenter[0] - error, realCenter[0] + error):
            for y in range(realCenter[1] - error, realCenter[1] + error):
                radius = cv2.pointPolygonTest(self.handContour, (x, y), True)
                if radius > maxRadius:
                    maxPoint = (x, y)
                    maxRadius = radius
        return np.array(maxPoint)

    def __find_palm_center(self):
        self.palmCenter = self.__ecludian_space_reduction()
        self.palmRadius = cv2.pointPolygonTest(
            self.handContour, tuple(self.palmCenter), True)


# vision = Vision()
# vision.start_process()
