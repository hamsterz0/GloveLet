from glovelet.eventapi.event import EventDispatchManager, EventListener
from glovelet.eventapi.glovelet_hardware_events import GloveletSensorEventDispatcher, GloveletImuEvent, GloveletFlexEvent
from glovelet.eventapi.glovelet_vision_events import GloveletVisionEventDispatcher, GloveletVisionListener
from pyautogui import mouseDown, mouseUp
import pyautogui


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
            if self.index < 0.65 and self.thumb0 < 0.75:
                self.left_click_down = False
                mouseUp(button='left')
                print('left up')
        elif self.right_click_down:
            if self.middle < 0.65 and self.thumb0 < 0.72:
                self.right_click_down = False
                mouseUp(button='right')
                print('right up')
        elif self.thumb0 > 0.80:
            if not self.left_click_down and not self.right_click_down:
                if self.index > 0.70 and not self.middle > 0.70:
                    self.left_click_down = True
                    mouseDown(button='left')
                    print('left click')
                elif self.middle > 0.70 and not self.index > 0.70:
                    self.right_click_down = True
                    mouseDown(button='right')
                    print('right click')


def main():
    sensor_disp = GloveletSensorEventDispatcher('/dev/ttyACM0', 115200)
    sensor_list = SensorListener()
    vision_disp = GloveletVisionEventDispatcher()
    vision_list = GloveletVisionListener()
    event_mgr = EventDispatchManager(sensor_disp, sensor_list, vision_disp, vision_list)
    event_mgr.deploy_dispatchers()
    while True:
        event_mgr.invoke_dispatch()
    event_mgr.end_dispatchers()


if __name__ == '__main__':
    pyautogui.FAILSAFE = False
    main()
