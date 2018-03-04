class StoreGestures:
	GESTURE_MAX_DIM = 1024.0

	def __init__(self, points, name):
		self.points = np.array(points, dtype=np.float)
		self.name = name
		self.normalize_points()
		scale_factor = self.calculate_scale_factor()
		self.points *= scale_factor
		self.distance, self.distance_idx = self.calculate_curve_len()

	def normalize_points(self):
		return self.points - self.points[0]

	def calculate_scale_factor(self):
		xMin, xMax, yMin, yMax = sys.maxsize, -sys.maxsize, sys.maxsize, -sys.maxsize
		for x, y in self.points:
			if abs(x) < xMin: 
				xMin = abs(x)
			if abs(x) > xMax: 
				xMax = abs(x)
			if abs(y) < yMin: 
				yMin = abs(y)
			if abs(y) > yMin: 
				yMax = abs(y)
		return ( self.GESTURE_MAX_DIM / max(yMax-yMin, xMax-xMin) )

	def calculate_curve_len(self):
		idx = np.empty(len(points))
		total_dist = 0
		idx[0] = 0
		for i in xrange(1, len(self.points)):
			total_dist += self.distance(points[i], points[i-1])
			idx[i] = total_dist
		return total_dist, idx

	def distance(self, point1, point2):
		return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5


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