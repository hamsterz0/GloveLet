from glovelet.vision.storeGesture import StoreGestures
import numpy as np

class Gesture:
	def __init__(self):
		self.point_count = 256
		self.predefined_gestures = []

	def __circle_gesture(self):
		radius = 512
		cc_points = [(radius*math.cos(t), radius*math.sin(t)) \
			for t in np.linspace(0, 2*math.pi, num=self.point_count)]
		c_points = [(radius*math.cos(t), -radius*math.sin(t)) \
			for t in np.linspace(0, 2*math.pi, num=self.point_count)]
		counter_clockwise = StoreGestures(cc_points, "Counter Clockwise")
		clockwise = StoreGestures(c_points, "Clockwise")
		self.predefined_gestures += [counter_clockwise, clockwise]