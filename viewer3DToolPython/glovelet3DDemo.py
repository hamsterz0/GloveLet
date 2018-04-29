
__all__ = []

import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLUT.freeglut
import numpy as np
import glm
import time
import atexit

from glovelet.viewer3DToolPython.worldobject import WorldObject
from glovelet.viewer3DToolPython.shaders import Shader
from glovelet.viewer3DToolPython.shadermanager import ShaderProgramManager
from glovelet.viewer3DToolPython.mesh import RectPrismMesh
from glovelet.sensorapi.glovelet_sensormonitor import GloveletBNO055IMUSensorMonitor
from glovelet.eventapi.event import EventDispatcherManager, EventListener
from glovelet.eventapi.glovelet_hardware_events import GloveletSensorEventDispatcher, GloveletImuEvent, GloveletFlexEvent


EVENT_MNGR = None
EVENT_DISP = None
EVENT_LIST = None


class GloveletDemoController(EventListener):
    def __init__(self):
        callbacks = {GloveletImuEvent: self.on_imu_event, GloveletFlexEvent: self.on_flex_event}
        super().__init__(callbacks)

    def on_imu_event(self, event):
        self.orientation = event.orientation[0]

    def on_flex_event(self, event):
        self.index = np.average(event.index)
        self.middle = np.average(event.middle)
        self.thumb0 = np.average(event.thumb0)

    def draw(self):
        pass


def on_exit():
    global EVENT_MNGR
    print('='*10 + 'END' + '='*10)
    EVENT_MNGR.end_dispatcher()
    time.sleep(0.8)


def main():
    global EVENT_MNGR, EVENT_DISP, EVENT_LIST
    atexit.register(on_exit)
    EVENT_DISP = GloveletSensorEventDispatcher('/dev/ttyACM0', 115200)
    EVENT_LIST = GloveletDemoController()
    EVENT_MNGR = EventDispatcherManager(EVENT_DISP, EVENT_LIST)


if __name__ == '__main__':
    main()
