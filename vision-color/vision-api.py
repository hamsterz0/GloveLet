import cv2
import numpy as np
import argparse

class Vision():
	def __init__(self):
		self.webcam = cv2.VideoCapture(0)
		self.cameraWidth = 1280
		self.cameraHeight = 720
		self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraWidth)
		self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraHeight)
		self.stationary = False
		self.window = []
		self.realX, self.realY = 0, 0
		self.stationary = False
		self.foundContour = True
		self.ap = argparse.ArgumentParser()
		self.ap.add_argument('-f', '--findrange', required=False, help='Range filter RGB')
		self.args = vars(self.ap.parse_args()) 

	def __read_webcam(self):
		_, self.frame = self.webcam.read()
		self.frame = cv2.flip(self.frame, 1)
		self.canvas = np.zeros(self.frame.shape, np.uint8)
		self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

	def __add_color_threshold(self):
		# G B R and not B G R
		if self.args['findrange']:
			pass
		boundaries = [([131, 69, 0], [181, 255, 255])]
		for (lower, upper) in boundaries:
			lower = np.array(lower, dtype="uint8")
			upper = np.array(upper, dtype="uint8")
			mask = cv2.inRange(self.frame, lower, upper)
			self.output = cv2.bitwise_and(self.frame, self.frame, mask=mask)
			self.output = cv2.cvtColor(self.output, cv2.COLOR_BGR2GRAY)
	
	def __extract_contours(self):
		_, self.contours, _ = cv2.findContours(self.output.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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
		self.handContour = cv2.approxPolyDP(self.realHandContour, 0.001 * self.realHandLength,True)

	def __get_contour_dimensions(self):
		self.minX, self.minY, self.handWidth, self.handHeight = \
			cv2.boundingRect(self.handContour)

	def __calculate_convex_hull(self):
		self.convexHull = cv2.convexHull(self.handContour,returnPoints = False)
		self.hullPoints = [self.handContour[i[0]] for i in self.convexHull]
		self.hullPoints = np.array(self.hullPoints, dtype = np.int32)
		self.defects = cv2.convexityDefects(self.handContour, self.convexHull)

	def __find_center(self):
		self.moments = cv2.moments(self.handContour)
		if self.moments["m00"] != 0:
			self.handX = int(self.moments["m10"] / self.moments["m00"])
			self.handY = int(self.moments["m01"] / self.moments["m00"])
			self.handMoment = (self.handX, self.handY)
			self.window += [self.handMoment]
		if len(self.window) == 4:
			self.realX, self.realY = 0, 0
			for (x, y) in self.window:
				self.realX += x
				self.realY += y
			self.realX = int(self.realX / len(self.window))
			self.realY = int(self.realY / len(self.window))
			self.__check_stationary()
			print('X: {}, Y: {}'.format(self.realX, self.realY))
			self.window = []

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

	def __check_stationary(self):
		factor = 0.04
		for (x, y) in self.window:
			if (x-self.realX)**2 + (y-self.realY) > factor * min(self.cameraWidth,self.cameraHeight):
				self.stationary = False
				return
		self.stationary = True
		
	def __draw(self):
		if self.realX != 0 and self.realY != 0:
			cv2.circle(self.canvas, (self.realX, self.realY),10, (255, 0, 0), -2)
		cv2.drawContours(self.canvas, [self.handContour], 0, (0, 255, 0), 1)
		# cv2.drawContours(self.canvas, [self.hullPoints], 0, (255, 0, 0), 2)
		cv2.imshow("images", self.canvas)

	def start_process(self):
		while True:
			self.__read_webcam()
			self.__add_color_threshold()
			self.__extract_contours()
			if self.foundContour:
				self.__get_contour_dimensions()
				self.__calculate_convex_hull()
				self.__find_center()
				# self.__find_palm_center()
				self.__draw()
			cv2.imshow('Output', self.output)
			cv2.imshow('Frame', self.frame)
			if cv2.waitKey(1) & 0xFF is ord('q'):
				break
		cv2.destroyAllWindows()


vision = Vision()
vision.start_process()