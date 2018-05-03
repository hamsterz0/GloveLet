from glovelet.eventapi.event import EventDispatchManager, EventListener
from glovelet.eventapi.glovelet_hardware_events import GloveletSensorEventDispatcher, GloveletImuEvent, GloveletFlexEvent
from glovelet.eventapi.glovelet_vision_events import GloveletVisionEventDispatcher, GloveletVisionListener, GloveletVisionEvent
from pyautogui import mouseDown, mouseUp, click, scroll
import pyautogui
from numpy import average
import numpy as np
from glm.gtc import quaternion as quat
from glm import vec3, vec4


class GloveletListener(EventListener):
    def __init__(self):
        callbacks = {GloveletImuEvent: self.on_imu_event, GloveletFlexEvent: self.on_flex_event, GloveletVisionEvent: self.on_vision_event}
        super().__init__(callbacks)
        self.accel = None
        self.orientation = None
        self.index = None
        self.middle = None
        self.thumb0 = None
        self.thumb1 = None
        self.left_click_down = False
        self.right_click_down = False
        self.is_thumb_up = False
        self.arctan = 0.0

    def on_imu_event(self, event):
        self.acceleration = event.acceleration
        self.orientation = event.orientation
        rot = quat.tquat(self.orientation[0][0], self.orientation[0][3], self.orientation[0][2], self.orientation[0][1])
        r = vec3(quat.mat4_cast(rot) * vec4(1.0, 0.0, 0.0, 0))
        self.arctan = np.degrees(np.arctan2(r[1], r[0] + r[2]))

    def on_flex_event(self, event):
        self.index = np.average(event.index)
        self.middle = np.average(event.middle)
        self.thumb0 = np.average(event.thumb0)
        self.thumb1 = np.average(event.thumb1)
        if self.left_click_down:
            if self.index < 0.70 and self.thumb0 < 0.75:
                self.left_click_down = False
                mouseUp(button='left')
                print('left up')
        elif self.right_click_down:
            if self.middle < 0.70 and self.thumb0 < 0.72:
                self.right_click_down = False
                mouseUp(button='right')
                print('right up')
        elif self.is_thumb_up:
            if self.index < 0.75 or self.middle < 0.75:
                self.is_thumb_up = False
                print('thumb up release')
            else:
                if int(self.arctan) in range(60, 126):
                    w = (self.arctan - 60) / (125 - 60)
                    scroll(int(5 * w))
                    print(w)
                elif int(self.arctan) in range(-35, 1):
                    w = abs(self.arctan) / 35
                    scroll(int(-5 * w))
        elif self.thumb0 > 0.80:
            if not self.left_click_down and not self.right_click_down:
                if self.index > 0.80 and not self.middle > 0.65:
                    self.left_click_down = True
                    click(clicks=2, button='left')
                    print('left double')
                elif self.middle > 0.80 and not self.index > 0.65:
                    self.right_click_down = True
                    mouseDown(button='right')
                    print('right click')
        elif self.index > 0.85 and self.middle > 0.85:
            if self.thumb0 < 0.1 and not self.is_thumb_up:
                self.is_thumb_up = True
                print('thumb up')

        # Left button down
        elif self.index > 0.85 and not (self.left_click_down or self.right_click_down or self.middle > 0.65):
            self.left_click_down = True
            print('left click')
            mouseDown(button='left')



    def on_vision_event(self, event):
        print('{} {}'.format(event.x, event.y))
        pyautogui.moveTo(event.x, event.y)


def main():
    sensor_disp = GloveletSensorEventDispatcher('/dev/ttyACM0', 115200)
    sensor_list = GloveletListener()
    vision_disp = GloveletVisionEventDispatcher()
    event_mgr = EventDispatchManager(sensor_disp, sensor_list, vision_disp)
    event_mgr.deploy_dispatchers()
    while True:
        event_mgr.invoke_dispatch()
    event_mgr.end_dispatchers()


if __name__ == '__main__':
    pyautogui.FAILSAFE = False
    main()
