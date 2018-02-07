import cv2
import numpy as np

class Vision():
	def __init__(self):
		self.webcam = cv2.VideoCapture(0)
		# self.cameraWidth = 1280
		# self.cameraHeight = 720
		# self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraWidth)
		# self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraHeight)
		self.stationary = False

	def __read_camera(self):
		_, self.frame = self.webcam.read()
		self.frame = cv2.flip(self.frame, 1)

	def __add_color_threshold(self):
		boundaries = [([180, 180, 180], [255, 255, 255])]
		for (lower, upper) in boundaries:
			lower = np.array(lower, dtype="uint8")
			upper = np.array(upper, dtype="uint8")
			mask = cv2.inRange(self.frame, lower, upper)
			this.output = cv2.bitwise_and(self.frame, self.frame, mask=mask)
			# grey = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
			# _, self.thresholded = cv2.threshold(grey, 0, 255,
			#  									 cv2.THRESH_BINARY+cv2.THRESH_OTSU)
			

	def start_process(self):
		while True:
			self.__read_camera()
			self.__add_color_threshold()
			cv2.imshow("images", this.output)
			if cv2.waitKey(1) & 0xFF is ord('q'):
				break
		cv2.destryAllWindows()


vision = Vision()
vision.start_process()