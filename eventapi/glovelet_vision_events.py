import numpy as np
from multiprocessing import Queue
import pyautogui

from glovelet.eventapi.event import Event, EventListener, EventDispatcher
from glovelet.vision.vision import Vision


class GloveletVisionEvent(Event):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class GloveletVisionEventDispatcher(EventDispatcher):
    def __init__(self):
        super().__init__(GloveletVisionEvent)

    def init(self):
        vision = Vision()
        return (vision, ), {}

    def update(self, vision):
        vision.read_webcam()
        vision.threshold()
        vision.extract_contours()
        if vision.foundContour:
            vision.find_center()
            vision.normalize_center()
        else:
            vision.stationary = True
        # vision.draw()
        vision.frame_outputs()
        #  vision.check_can_perform_gesture()
        #  vision.determine_if_gesture()
        x, y = vision.move_cursor()
        vision_event = GloveletVisionEvent(x, y)
        # Exit out of this hell hole.
        vision.check_exit()
        return vision_event

    def finish(self, *args, **kwargs):
        pass


class GloveletVisionListener(EventListener):
    def __init__(self):
        callbacks = {GloveletVisionEvent: self.on_vision_event}
        super().__init__(callbacks)

    def on_vision_event(self, event):
        print('{} {}'.format(event.x, event.y))
        # pyautogui.moveTo(event.x, event.y)
