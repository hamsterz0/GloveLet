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

def callback(value):
	pass


class Vision():

	FINGER1 = 'finger1'
	FINGER2 = 'finger2'
	ACTIVE_FINGERS = [FINGER1]
	TOTAL_FINGERS =[FINGER1, FINGER2]
	TRACKER_FINGER = FINGER1

	def __init__(self):
		pyautogui.FAILSAFE = False
		root = tkinter.Tk()
		root.withdraw()
		# member variables
		self.webcam = cv2.VideoCapture(0)
		self.screen_width = root.winfo_screenwidth()
		self.screen_height = root.winfo_screenheight()
		self.cameraWidth = self.screen_width
		self.cameraHeight = self.screen_height
		# self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraWidth)
		# self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraHeight)
		self.logger = logging.getLogger(__name__)
		self.output = {}
		self.handContour = {}
		self.canvas = {}
		self.handMoment = {}
		self.foundContour = {}
		self.realX = {}
		self.realY = {}
		self.stationary = False 
		self.mouseX = self.screen_width/2
		self.mouseY = self.screen_height/2
		self.queue = []
		self.dx = 0
		self.dy = 0
		self.clickThresh = 70
		self.clickCounter = 0
		self.pinched = False
		self.window = DataTimeSeries(4, 4, auto_filter=True)
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument('-f', '--find_range', 
			help="Find the range from within the program", 
			action="store_true", default=False)
		self.args = self.parser.parse_args()
		# self.data = np.zeros(4, np.float32)
		self.boundaries = {}
		self.__init_mem_vars()

	def __init_mem_vars(self):
		# initializing member variables with initial values.
		for finger in self.TOTAL_FINGERS:
			self.handMoment[finger] = (0, 0)
			self.foundContour[finger] = [True]
			self.realX[finger] = int(self.screen_width/2)
			self.realY[finger] = int(self.screen_height/2)

		if self.args.find_range:
			with open('.vision.config', 'w') as file:
				for finger in self.ACTIVE_FINGERS:
					value = self.__find_range()
					self.boundaries[finger] = value
					file.write('{}:{}'.format(finger, str(value)))
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
				print('Config file not found. Run the program with -f flag.')
				sys,exit()
			except Exception:
				print('Not all the fingers have colors configured. Run with -f flag')
				sys.exit()

	def __find_range(self):
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
			cv2.imshow('Image', image)
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
		for finger in self.ACTIVE_FINGERS:
			self.canvas[finger] = np.zeros(self.frame.shape, np.uint8)
		self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

	def __threshold(self, finger):
		'''
		adding the color threshold to the frame captured by the webcam.
		The threshold boundaries are specified in advance.
		'''
		# TODO: Give user the option to select the threshold color. Under configuration.
		(lower, upper) = self.boundaries[finger]
		lower = np.array(lower, dtype="uint8")
		upper = np.array(upper, dtype="uint8")
		mask = cv2.inRange(self.frame, lower, upper)
		self.output[finger] = cv2.bitwise_and(self.frame, self.frame, mask=mask)
		self.output[finger] = cv2.cvtColor(self.output[finger], cv2.COLOR_BGR2GRAY)
	
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

	def __check_stationary(self):
		factor = 0.04
		for (x, y) in self.window:
			if (x-self.realX)**2 + (y-self.realY) > factor * min(self.cameraWidth,self.cameraHeight):
				self.stationary = False
				return
		self.stationary = True

	def __find_center(self, finger):
		self.moments = cv2.moments(self.handContour[finger])
		if self.moments["m00"] != 0:
			self.handX = int(self.moments["m10"] / self.moments["m00"])
			self.handY = int(self.moments["m01"] / self.moments["m00"])
			self.handMoment[finger] = (self.handX, self.handY)

	def __update_cursor(self, coords, finger):
		self.data = np.zeros(4)
		self.data[:] = coords
		print(self.data)
		
	def __check_pinch(self):
		fingerDist = math.sqrt((self.realX[self.FINGER1] - self.realX[self.FINGER2])**2 + \
							   (self.realY[self.FINGER1] - self.realY[self.FINGER2])**2)
		print('Finger Distance: {}'.format(fingerDist))
		if fingerDist < self.clickThresh:
			if self.clickCounter > 3 and not self.pinched:
				pyautogui.click(x=self.realX[self.FINGER1], y=self.realY[self.FINGER1])
				self.pinched = True
				self.clickCounter = 0
			else:
				self.clickCounter += 1
		else:
			self.pinched = False

	def __draw(self, finger):
		if self.realX[finger] != 0 and self.realY[finger] != 0:
			cv2.circle(self.canvas[finger], (self.realX[finger], self.realY[finger]),10, (255, 0, 0), -2)
		cv2.drawContours(self.canvas[finger], [self.handContour[finger]], 0, (0, 255, 0), 1)
		# cv2.drawContours(self.canvas, [self.hullPoints], 0, (255, 0, 0), 2)

	def __frame_outputs(self, finger):
		if finger == self.FINGER1:
			cv2.imshow('Canvas: ' + finger, self.canvas[finger])
		cv2.imshow('Output ' + finger, self.output[finger])
		cv2.imshow('Frame', self.frame)

	def start_process(self):
		while True:
			for finger in self.ACTIVE_FINGERS:
				self.__read_webcam()
				self.__threshold(finger)
				self.__extract_contours(finger)
				if self.foundContour[finger]:
					self.__find_center(finger)
				self.__frame_outputs(finger)

			# coords = ()
			# for finger in self.TOTAL_FINGERS:
				# coords += self.handMoment[finger]
			
			# self.__update_cursor(coords, self.TRACKER_FINGER)


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