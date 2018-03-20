import numpy as np
import sys


class Gesture:
    GESTURE_MAX_DIM = 1024.0

    def __init__(self, points, name):
        self.points = np.array(points, dtype=np.float)
        self.name = name
        self.normalize_points()
        scale_factor = self.calculate_scale_factor()
        self.points *= scale_factor
        self.distance, self.distance_index = self.curve_length()

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
    
    def curve_length(self):
        cummulative_distance = 0
        indices = np.empty(len(self.points))
        indices[0] = 0
        for i in range(1, len(self.points)):
            cummulative_distance += Gesture.calculate_distance(self.points[i], self.points[i-1]) 
            indices[i] = cummulative_distance
        return cummulative_distance, indices
    
    @staticmethod
    def calculate_distance(point1, point2):
        return ((point1[0] - point2[0])**2 +
                (point1[1] - point2[1])**2)**0.5

    @staticmethod
    def find_indices(template, template_distance):
        if template_distance > template.distance_index[-1]:
            return (len(template.distance_index) - 2, 
                    len(template.distance_index) - 1)
        elif template_distance < template.distance_index[0]:
            return 0, 1
        start = 0
        end = len(template.distance_index)
        while True:
            mid = int((start + end)/2)
            if template.distance_index[mid] == template_distance:
                return max(mid-1, 0), min(mid+1, len(template.distance_index)-1)
            elif start == end:
                if template.distance_index[start] < template_distance:
                    return start, min(start+1, len(template.distance_index)-1)
                else:
                    return max(start-1, 0), start
            elif abs(start-end) == 1:
                return (min(start, end), max(start, end))
            elif template.distance_index[mid] < template_distance:
                start = mid
            else:
                end = mid

    @staticmethod
    def linear_template(template, template_distance):
        min_index, max_index = Gesture.find_indices(template, template_distance)
        distance_diff = (template.distance_index[max_index] - template.distance_index[min_index])
        template_distance -= template.distance_index[min_index]
        scale = template_distance / distance_diff
        change = template.points[max_index] - template.points[min_index]
        change *= scale
        return template.points[min_index] + change

    @staticmethod
    def compare_gesture(template, human_gesture):
        total_distance = 0
        total_error = 0
        distances = []
        for i in range(len(human_gesture.distance_index)):
            # Getting the template distance in terms of the human gesture size
            to_find = (template.distance * human_gesture.distance_index[i] / human_gesture.distance)
            compare_point = Gesture.linear_template(template, to_find)
            # Calculating how different the two points are
            distance = Gesture.calculate_distance(compare_point, human_gesture.points[i])
            total_distance += distance
            distances += [distance]
            total_error += distance**2
        min_distance = min(distances)
        max_distance = max(distances)
        distance_range = max_distance - min_distance
        result = {
            'gestureList': distances,
            'minDistance': min_distance,
            'maxDistance': max_distance,
            'totalDistance': total_distance,
            'totalError': total_error
            }
        return result

