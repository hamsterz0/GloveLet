import cv2
import numpy as np

class Vision():
	def __init__(self):
		self.webcam = cv2.VideoCapture(0)
		self.cameraWidth = 1280
		self.cameraHeight = 720
		self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraWidth)
		self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraHeight)
		self.stationary = False

	def __read_camera(self):
		_, self.frame = self.webcam.read()
		self.frame = cv2.flip(self.frame, 1)

	def __add_color_threshold(self):
		boundaries = [([200, 200, 200], [255, 255, 255])]
		for (lower, upper) in boundaries:
			lower = np.array(lower, dtype="uint8")
			upper = np.array(upper, dtype="uint8")
			mask = cv2.inRange(self.frame, lower, upper)
			self.output = cv2.bitwise_and(self.frame, self.frame, mask=mask)
			self.output = cv2.cvtColor(self.output, cv2.COLOR_BGR2GRAY)
	
	def __extract_contours(self):
		_, self.contours, _ = cv2.findContours(self.output.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		maxArea, idx = 0, 0
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

	def find_center(self):
		self.moments = cv2.moments(self.handContour)
		self.handX = int(self.moments["m10"] / self.moments["m00"])
		self.handY = int(self.moments["m01"] / self.moments["m00"])
		self.handMoment = (self.handX, self.handY)
		self.handMomentPositions += [self.handMoment]

	def start_process(self):
		while True:
			self.__read_camera()
			self.__add_color_threshold()
			self.__extract_contours()
			self.__get_contour_dimensions()
			cv2.imshow("images", self.output)
			if cv2.waitKey(1) & 0xFF is ord('q'):
				break
		cv2.destryAllWindows()


vision = Vision()
vision.start_process()