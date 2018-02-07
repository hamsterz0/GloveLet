import cv2
import numpy as np

class Vision():
	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		self.cameraWidth = 1280
		self.cameraHeight = 720
		self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.cameraWidth)
        self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.cameraHeight)
        self.stationary = False