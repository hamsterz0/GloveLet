import cv2
import numpy as np
import tkinter
import argparse
import pyautogui
import math
from timeseries import DataTimeSeries
import logging
from ast import literal_eval
import sys
from PIL import Image
from motion_multiplier import motion_multiplier


def callback(value):
	pass

class Vision:
	FINGER1 = 'finger1' # finger 1 tag
	FINGER2 = 'finger2' # finger 2 tag
	ACTIVE_FINGERS = [FINGER1]  # Number of fingers tracking
	TOTAL_FINGERS =[FINGER1, FINGER2]   # Total numbers of fingers
	TRACKER_FINGER = FINGER1    # The cursor tracker finger
	WINDOW_SIZE = 4 # The window size for calculating hte average
	PREV_MEMORY = 2 # Previous points stored. 

	def __init__(self):
		pyautogui.FAILSAFE = False
		root = tkinter.Tk()
		root.withdraw()
		# member variables
		self.webcam = cv2.VideoCapture(1)
		self.screen_width = root.winfo_screenwidth()
		self.screen_height = root.winfo_screenheight()
		self.cameraWidth = self.screen_width / 2
		self.cameraHeight = self.screen_height / 2
		self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraWidth)
		self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraHeight)
		self.logger = logging.getLogger(__name__)
		self.output = {}
		self.click_queue = {}
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
		self.dx = 0
		self.dy = 0
		self.clickThresh = 45
		self.clickCounter = 0
		self.pinched = False
		# self.window = DataTimeSeries(2, self.WINDOW_SIZE, auto_filter=True)
		self.window = {}
		self.cursor_history = []
		self.movement_history = {}
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument('-r', '--find_range', 
			help="Find the range from within the program", 
			action="store_true", default=False)
		self.args = self.parser.parse_args()
		# self.data = np.zeros(4, np.float32)
		self.boundaries = {}
		self.counter = 0
		self.prev_mouse = ()
		self.prev_rmouse = ()
		self.__init_mem_vars()

	def __init_mem_vars(self):
		# initializing member variables with initial values.
		for finger in self.ACTIVE_FINGERS:
			self.handMoment[finger] = (0, 0)
			self.foundContour[finger] = True
			self.stationary[finger] = False
			self.realX[finger] = 0
			self.realY[finger] = 0
			self.click_queue[finger] = 0
			self.mouseX = int(self.screen_width/2)
			self.mouseY = int(self.screen_height/2)
			self.movement_history[finger] = []
			self.window[finger] = DataTimeSeries(2, self.WINDOW_SIZE, auto_filter=True)

		if self.args.find_range:
			with open('.vision.config', 'w') as file:
				for finger in self.ACTIVE_FINGERS:
					value = self.__find_range()
					self.boundaries[finger] = value
					file.write('{}:{}\n'.format(finger, str(value)))
		else:
			try:
				finger_map = {}
				with open('.vision.config', 'r') as file:
					for line in file:
						[finger_name, finger_tuple] = line.split(':')
						finger_tuple = literal_eval(finger_tuple)
						self.boundaries[finger_name] = finger_tuple
				if len(self.boundaries.keys()) < len(self.ACTIVE_FINGERS):
					raise Exception
			except IOError:
				print('Config file not found. Run the program with -r flag.')
				sys,exit()
			except Exception:
				print('Not all the fingers have colors configured. Run with -r flag')
				sys.exit()

	def __find_range(self):
		'''
		Checking the if the configuration file exists. If not, then load up the 
		GUI for finding the HSV range. Else, just read the values of the 
		.vision.conf file.
		'''
		range_filter = 'HSV'
		cv2.namedWindow("Trackbar", 0)
		for i in ["MIN", "MAX"]:
			v = 0 if i == "MIN" else 255
			for j in range_filter:
				cv2.createTrackbar("%s_%s" % (j, i), "Trackbar", v, 255, callback)
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

	def __read_webcam(self):
		'''
		Reading the webcam, flipping the frame vertically by 180 degrees and 
		creating canvas for all the ACTIVE_FINGERS. Also converting the frame into HSV colorspace
		'''
		_, self.frame = self.webcam.read()
		self.frame = cv2.flip(self.frame, 1)
		# for finger in self.ACTIVE_FINGERS:
		self.canvas = np.zeros(self.frame.shape, np.uint8)
		self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

	def __threshold(self, finger):
		'''
		adding the color threshold to the frame captured by the webcam.
		The threshold boundaries are specified in advance.
		'''
		(lower, upper) = self.boundaries[finger]
		lower = np.array(lower, dtype="uint8")
		upper = np.array(upper, dtype="uint8")
		mask = cv2.inRange(self.frame, lower, upper)
		kernel = np.ones((5,5),np.uint8)
		self.output[finger] = cv2.bitwise_and(self.frame, self.frame, mask=mask)
		self.output[finger] = cv2.cvtColor(self.output[finger], cv2.COLOR_BGR2GRAY)
		self.output[finger] = cv2.erode(self.output[finger],kernel,iterations = 1)
		self.output[finger] = cv2.dilate(self.output[finger],kernel,iterations = 3)
	
	def __extract_contours(self, finger):
		'''
		Extracting the contours and finding the maximum amount of area that is being tracked.
		'''
		_, self.contours, _ = cv2.findContours(self.output[finger].copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		maxArea, idx = 0, 0
		if len(self.contours) == 0:
			self.foundContour[finger] = False
			return
		else:
			self.foundContour[finger] = True

		for i in range(len(self.contours)):
			area = cv2.contourArea(self.contours[i])
			if area > maxArea:
				maxArea = area
				idx = i
		self.realHandContour = self.contours[idx]
		self.realHandLength = cv2.arcLength(self.realHandContour, True)
		self.handContour[finger] = cv2.approxPolyDP(self.realHandContour, 0.001 * self.realHandLength,True)

	def __check_stationary(self, finger):
		'''
		Finding the absolute deviation from the mean to find if the finger is stationary. 
		'''
		factor = 0.02
		for [x, y] in self.window[finger].data_series:
			if (x-self.realX[finger])**2 + (y-self.realY[finger]) > factor * min(self.cameraWidth,self.cameraHeight):
				self.stationary[finger] = False
				return
		self.stationary[finger] = True

	def __find_center(self, finger):
		'''
		Finding the center of the contour of the finger that we are tracking.
		'''
		self.moments = cv2.moments(self.handContour[finger])
		if self.moments["m00"] != 0:
			self.handX = int(self.moments["m10"] / self.moments["m00"])
			self.handY = int(self.moments["m01"] / self.moments["m00"])
			self.handMoment[finger] = (self.handX, self.handY)

	def __normalize_center(self, finger):
		'''
		Using the time series data to normalize the data. 
		This is calling the Mean function in the window[finger] object and 
		then getting the data from it. 
		The realX and realY are basically are just the mean of n handX and handY 
		values (to stop the gitter)
		'''
		self.window[finger].add(self.handMoment[finger])
		self.realX[finger], self.realY[finger] = self.window[finger].get_data()
		self.movement_history[finger] += [(self.realX[finger], self.realY[finger])]
		self.__check_stationary(finger)

	def __move_cursor(self, finger):
		'''
			Just simpler to create a new function to calculate the mouse pos,
			I'm not fucking messing with Git ever again. This is too much for me to
			handle.
		'''
		self.cursor_history.append([self.realX[finger], self.realY[finger]])
		if len(self.cursor_history) < self.PREV_MEMORY:
			return
		# dx = self.cursor_history[1][0] - self.cursor_history[0][0]
		# dy = self.cursor_history[1][1] - self.cursor_history[0][1]
		
		self.x = self.realX[finger] * (self.screen_width / self.frame.shape[1]) # * ((self.screen_width + buff))
		self.y = self.realY[finger] * (self.screen_height / self.frame.shape[0]) # * ((self.screen_height + buff))

		pyautogui.moveTo(self.x, self.y)
		
	def __check_pinch(self):
		'''
		The left click action on the screen.
		'''
		fingerDist = math.sqrt((self.realX[self.FINGER1] - self.realX[self.FINGER2])**2 + \
							   (self.realY[self.FINGER1] - self.realY[self.FINGER2])**2)
		print('Finger Distance: {}'.format(fingerDist))
		if fingerDist < self.clickThresh:
			self.stationary[self.TRACKER_FINGER] = True
			pyautogui.mouseDown()
			self.pinched = True
			self.clickCounter = 0
		else:
			pyautogui.mouseUp()
			self.pinched = False
			self.stationary[self.TRACKER_FINGER] = False
		
		# print('{} {}'.format(self.realY[self.FINGER2],self.realY[self.FINGER2]))

	def __draw(self, finger):
		# if self.realX[finger] != 0 and self.realY[finger] != 0:
		# 	cv2.circle(self.canvas[finger], (self.realX[finger], self.realY[finger]),10, (255, 0, 0), -2)
		# cv2.drawContours(self.canvas[finger], [self.handContour[finger]], 0, (0, 255, 0), 1)
		cv2.drawContours(self.canvas, [self.handContour[finger]], 0, (0, 255, 0), 1)
		cv2.circle(self.canvas, tuple([self.realX[finger], self.realY[finger]]),
			10, (255, 0, 0), -2)
		recent_positions = self.movement_history[finger][-30:]
		if len(recent_positions) != 0:
			for i in range(len(recent_positions)):
				cv2.circle(self.canvas, recent_positions[i], 5, 
					(25*i, 255, 25*i), -1)

	def __frame_outputs(self, finger):
		cv2.imshow('Output ' + finger, self.output[finger])
		cv2.imshow('Frame' + finger, self.frame)
		# cv2.imshow('Canvas' + finger, self.canvas)
		pass

	def start_process(self):
		run_once = False
		while True:
			for finger in self.ACTIVE_FINGERS:
				self.__read_webcam()
				self.__threshold(finger)
				self.__extract_contours(finger)
				if self.foundContour[finger]:
					self.__find_center(finger)
					self.__normalize_center(finger)
				else:
					self.stationary[self.TRACKER_FINGER] = True
				self.__draw(finger)
				self.__frame_outputs(finger)

			# Check if the user pinched his finger for left click
			# if self.FINGER1 in self.ACTIVE_FINGERS \
			# 	and self.FINGER2 in self.ACTIVE_FINGERS:
			# 	self.__check_pinch()
			
			# Update the cursor location with the new finger location.
			if not self.stationary[self.TRACKER_FINGER]:
				self.__move_cursor(self.TRACKER_FINGER)
			self.counter += 1

			# Exit out of this hell hole.
			if cv2.waitKey(1) & 0xFF is ord('q'):
				break
		cv2.destroyAllWindows()

	'''**************** METHODS BELOW ARE FOR HAND PALM TRACKING ****************'''	
	def __get_contour_dimensions(self):
		self.minX, self.minY, self.handWidth, self.handHeight = \
			cv2.boundingRect(self.handContour)

	def __calculate_convex_hull(self):
		self.convexHull = cv2.convexHull(self.handContour,returnPoints = False)
		self.hullPoints = [self.handContour[i[0]] for i in self.convexHull]
		self.hullPoints = np.array(self.hullPoints, dtype = np.int32)
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
					maxPoint =(tx+x, ty+y)
					maxRadius = radius
		realCenter = np.array(np.array(maxPoint) / scaleFactor, dtype=np.int32)
		error = int((1 / scaleFactor) * 1.5)
		maxPoint = None
		maxRadius = 0
		for x in range(realCenter[0] - error, realCenter[0] + error):
			for y in range(realCenter[1] - error, realCenter[1] + error):
				radius = cv2.pointPolygonTest(self.handContour, (x, y), True)
				if radius > maxRadius:
					maxPoint = (x,y)
					maxRadius = radius
		return np.array(maxPoint)

	def __find_palm_center(self):
		self.palmCenter = self.__ecludian_space_reduction()
		self.palmRadius = cv2.pointPolygonTest(self.handContour, tuple(self.palmCenter), True)


vision = Vision()
vision.start_process()
