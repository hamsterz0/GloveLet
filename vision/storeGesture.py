import numpy as np
import sys


class StoreGestures:
    GESTURE_MAX_DIM = 1024.0

    def __init__(self, points, name):
        self.points = np.array(points, dtype=np.float)
        self.name = name
        self.normalize_points()
        scale_factor = self.calculate_scale_factor()
        self.points *= scale_factor

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
        return (self.GESTURE_MAX_DIM / max(yMax-yMin, xMax-xMin))
