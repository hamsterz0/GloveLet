from glovelet.eventapi.event import EventDispatchManager, EventListener
from glovelet.eventapi.glovelet_hardware_events import GloveletSensorEventDispatcher, GloveletImuEvent, GloveletFlexEvent
from pyautogui import click


class SensorListener(EventListener):
    def __init__(self):
        callbacks = {GloveletImuEvent: self.on_imu_event, GloveletFlexEvent: self.on_flex_event}
        super().__init__(callbacks)
        self.accel = None
        self.orientation = None
        self.index = None
        self.middle = None
        self.thumb0 = None
        self.thumb1 = None
        self.left_click_down = False
        self.right_click_down = False

    def on_imu_event(self, event):
        self.acceleration = event.acceleration
        self.orientation = event.orientation

    def on_flex_event(self, event):
        self.index = sum(event.index) / len(event.index)
        self.middle = sum(event.middle) / len(event.middle)
        self.thumb0 = sum(event.thumb0) / len(event.thumb0)
        self.thumb1 = sum(event.thumb1) / len(event.thumb1)
        if self.left_click_down:
            if self.index < 0.78:
                
        elif self.thumb0 > 0.75:
            if not self.left_click_down and not self.right_click_down:
                if self.index > 0.8 and not self.middle > 0.8:
                    self.left_click_down = True
                    click(button='left')
                elif self.middle > 0.8 and not self.index > 0.8:
                    self.right_click_down = True
                    click(button='right')
