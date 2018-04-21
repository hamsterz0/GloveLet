from glovelet.vision.gesture import Gesture
import numpy as np
import math


class PreDefinedGestures:
    def __init__(self):
        self.point_count = 256
        self.predefined_gestures = []
        self.__circle_gesture() # create the gesture

    def __circle_gesture(self):
        radius = 512
        cc_points = [(radius*math.cos(t), radius*math.sin(t))
                     for t in np.linspace(0, 2*math.pi, num=self.point_count)]
        c_points = [(radius*math.cos(t), -radius*math.sin(t))
                    for t in np.linspace(0, 2*math.pi, num=self.point_count)]
        counter_clockwise = Gesture(cc_points, "CCW Circle")
        clockwise = Gesture(c_points, "CW Circle")
        self.predefined_gestures += [counter_clockwise, clockwise]

