
__all__ = []

import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLUT.freeglut
import sys
import numpy as np
import glm
from glm.gtc import quaternion as quat
import time
import atexit

from glovelet.viewer3DToolPython.worldobject import WorldObject
from glovelet.viewer3DToolPython.shaders import Shader
from glovelet.viewer3DToolPython.shadermanager import ShaderProgramManager
from glovelet.viewer3DToolPython.mesh import RectPrismMesh
from glovelet.sensorapi.glovelet_sensormonitor import GloveletBNO055IMUSensorMonitor
from glovelet.eventapi.event import EventDispatchManager, EventListener
from glovelet.eventapi.glovelet_hardware_events import GloveletSensorEventDispatcher, GloveletImuEvent, GloveletFlexEvent

ASPECT_RATIO = 1920 / 1080
MAX_FPS = 60.00
MAX_TDELTA = 1.0 / MAX_FPS
FRAME_TIME = time.time()
EVENT_MNGR = None
EVENT_DISP = None
EVENT_LIST = None
SHADER_DIR = 'shaders/'
VERTEX_SHADER_SOURCE = 'vertex_shader130.glsl'
FRAGMENT_SHADER_SOURCE = 'fragment_shader130.glsl'
SHADER = None
PROJECTION_MTRX = None
LOOKAT_MTRX = None
HAND = None
INDEX00 = None
INDEX01 = None
INDEX02 = None
INDEX00_ROT_MIN = glm.vec3(0, 0, 0)
INDEX01_ROT_MIN = glm.vec3(0, 0, 0)
INDEX02_ROT_MIN = glm.vec3(0, 0, 0)
INDEX00_ROT_MAX = glm.vec3(np.radians(80), 0, 0)
INDEX01_ROT_MAX = glm.vec3(np.radians(70), 0, 0)
INDEX02_ROT_MAX = glm.vec3(np.radians(60), 0, 0)
MIDDLE00 = None
MIDDLE01 = None
MIDDLE02 = None
MIDDLE00_ROT_MIN = glm.vec3(0, 0, 0)
MIDDLE01_ROT_MIN = glm.vec3(0, 0, 0)
MIDDLE02_ROT_MIN = glm.vec3(0, 0, 0)
MIDDLE00_ROT_MAX = glm.vec3(np.radians(85), 0, 0)
MIDDLE01_ROT_MAX = glm.vec3(np.radians(75), 0, 0)
MIDDLE02_ROT_MAX = glm.vec3(np.radians(60), 0, 0)
THUMB00 = None
THUMB01 = None
THUMB02 = None
THUMB00_ROT_MIN = glm.vec3(0, np.radians(45), np.radians(-5))
THUMB01_ROT_MIN = glm.vec3(0, 0, 0)
THUMB02_ROT_MIN = glm.vec3(0, 0, 0)
THUMB00_ROT_MAX = glm.vec3(0, 0, np.radians(-40))
THUMB01_ROT_MAX = glm.vec3(np.radians(50), np.radians(0), np.radians(-20))
THUMB02_ROT_MAX = glm.vec3(np.radians(80), np.radians(0), np.radians(-10))
MOUSE_POS = None


np.set_printoptions(precision=4, suppress=True)


class GloveletDemoController(EventListener):
    def __init__(self):
        callbacks = {GloveletImuEvent: self.on_imu_event, GloveletFlexEvent: self.on_flex_event}
        super().__init__(callbacks)
        self.orientation = None
        self.index = 0.0
        self.middle = 0.0
        self.thumb0 = 0.0

    def on_imu_event(self, event):
        self.orientation = event.orientation[0]

    def on_flex_event(self, event):
        self.index = np.average(event.index)
        self.middle = np.average(event.middle)
        self.thumb0 = np.average(event.thumb0)


def draw():
    global FRAME_TIME, EVENT_MNGR, EVENT_LIST,\
           HAND, INDEX00, INDEX01, INDEX02, MIDDLE00, MIDDLE01, MIDDLE02, THUMB00, THUMB01, THUMB02,\
           SHADER, LOOKAT_MTRX, PROJECTION_MTRX, MAX_TDELTA
    EVENT_MNGR.invoke_dispatch()
    tdelta = time.time() - FRAME_TIME
    if tdelta >= MAX_TDELTA:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        SHADER.use()
        SHADER.set_projection(PROJECTION_MTRX.value)
        SHADER.set_lookat(LOOKAT_MTRX.value)
        rot_delta_index00 = INDEX00_ROT_MAX * EVENT_LIST.index
        rot_delta_index01 = INDEX01_ROT_MAX * EVENT_LIST.index
        rot_delta_index02 = INDEX02_ROT_MAX * EVENT_LIST.index
        rot_delta_middle00 = MIDDLE00_ROT_MAX * EVENT_LIST.middle
        rot_delta_middle01 = MIDDLE01_ROT_MAX * EVENT_LIST.middle
        rot_delta_middle02 = MIDDLE02_ROT_MAX * EVENT_LIST.middle
        rot_delta_thumb00 = THUMB00_ROT_MAX * EVENT_LIST.thumb0
        rot_delta_thumb01 = THUMB01_ROT_MAX * EVENT_LIST.thumb0
        rot_delta_thumb02 = THUMB02_ROT_MAX * EVENT_LIST.thumb0
        rot_hand = quat.tquat(tuple(EVENT_LIST.orientation))
        HAND.set_rotation(rot_hand)
        INDEX00.set_rotation(rot_delta_index00 + INDEX00_ROT_MIN)
        INDEX01.set_rotation(rot_delta_index01 + INDEX01_ROT_MIN)
        INDEX02.set_rotation(rot_delta_index02 + INDEX02_ROT_MIN)
        MIDDLE00.set_rotation(rot_delta_middle00 + MIDDLE00_ROT_MIN)
        MIDDLE01.set_rotation(rot_delta_middle01 + MIDDLE01_ROT_MIN)
        MIDDLE02.set_rotation(rot_delta_middle02 + MIDDLE02_ROT_MIN)
        THUMB00.set_local_rotation(rot_delta_thumb00 + THUMB00_ROT_MIN)
        THUMB01.set_rotation(rot_delta_thumb01 + THUMB01_ROT_MIN)
        THUMB02.set_rotation(rot_delta_thumb02 + THUMB02_ROT_MIN)
        HAND.render()
        FRAME_TIME = time.time()
    glut.glutSwapBuffers()
    glut.glutPostRedisplay()


def mouse_motion(x, y):
    global MOUSE_POS, HAND
    if MOUSE_POS is None:
        MOUSE_POS = glm.vec2(x, y)
        return
    chg_x = x - MOUSE_POS.x
    chg_y = y - MOUSE_POS.y
    if chg_x > 0:
        MOUSE_POS.x += 0.025
    elif chg_x <= 0:
        MOUSE_POS.x -= 0.025
    if chg_y > 0:
        MOUSE_POS.y += 0.025
    elif chg_y <= 0:
        MOUSE_POS.y -= 0.025
    euler = glm.vec3(chg_y * 0.025, chg_x * 0.025, 0.0)
    HAND.rotate(euler)
    MOUSE_POS = glm.vec2(x, y)

def init_hand():
    global HAND, INDEX00, INDEX01, INDEX02, MIDDLE00, MIDDLE01, MIDDLE02, THUMB00, THUMB01, THUMB02
    color = np.array([[1.0, 0.0, 0.0, 1.0],
                      [0.5, 0.0, 0.0, 1.0],
                      [0.0, 1.0, 0.0, 1.0],
                      [0.0, 0.5, 0.0, 1.0],
                      [0.0, 0.0, 1.0, 1.0],
                      [0.0, 0.0, 0.5, 1.0]], 'f')
    palm_dim = (5.0, 2.0, 8.0)
    index00_dim = (1.75, 1.8, 3.8)
    index01_dim = (1.65, 1.5, 1.8)
    index02_dim = (1.55, 1.25, 1.57)
    middle00_dim = (1.75, 1.8, 4.2)
    middle01_dim = (1.65, 1.5, 2.2)
    middle02_dim = (1.55, 1.25, 1.57)
    thumb00_dim = (5.0, 1.8, 5.0)
    thumb01_dim = (1.75, 1.5, 3.0)
    thumb02_dim = (1.65, 1.35, 2.5)
    palm_mesh = RectPrismMesh(*palm_dim, face_colors=color)
    INDEX00 = WorldObject(RectPrismMesh(*index00_dim, face_colors=color))
    INDEX01 = WorldObject(RectPrismMesh(*index01_dim, face_colors=color))
    INDEX02 = WorldObject(RectPrismMesh(*index02_dim, face_colors=color))
    MIDDLE00 = WorldObject(RectPrismMesh(*middle00_dim, face_colors=color))
    MIDDLE01 = WorldObject(RectPrismMesh(*middle01_dim, face_colors=color))
    MIDDLE02 = WorldObject(RectPrismMesh(*middle02_dim, face_colors=color))
    THUMB00 = WorldObject(RectPrismMesh(*thumb00_dim, face_colors=color))
    THUMB01 = WorldObject(RectPrismMesh(*thumb01_dim, face_colors=color))
    THUMB02 = WorldObject(RectPrismMesh(*thumb02_dim, face_colors=color))
    HAND = WorldObject(palm_mesh)
    HAND.add_child(INDEX00)
    INDEX00.add_child(INDEX01)
    INDEX01.add_child(INDEX02)
    HAND.add_child(MIDDLE00)
    MIDDLE00.add_child(MIDDLE01)
    MIDDLE01.add_child(MIDDLE02)
    HAND.add_child(THUMB00)
    THUMB00.add_child(THUMB01)
    THUMB01.add_child(THUMB02)
    HAND.set_position((0, -20.0, 50.0))
    INDEX00.set_position((index00_dim[0] * 1.5, 0, palm_dim[2]))
    INDEX00.set_local_position((0, 0, index00_dim[2] * 1.2))
    INDEX01.set_position((0, 0, index00_dim[2]))
    INDEX01.set_local_position((0, 0, index01_dim[2] * 1.2))
    INDEX02.set_position((0, 0, index01_dim[2]))
    INDEX02.set_local_position((0, 0, index02_dim[2] * 1.2))
    INDEX00.set_rotation(INDEX00_ROT_MAX)
    INDEX01.set_rotation(INDEX01_ROT_MAX)
    INDEX02.set_rotation(INDEX02_ROT_MAX)
    MIDDLE00.set_position((-middle00_dim[0] * 1.5, 0, palm_dim[2]))
    MIDDLE00.set_local_position((0, 0, middle00_dim[2] * 1.2))
    MIDDLE01.set_position((0, 0, middle00_dim[2]))
    MIDDLE01.set_local_position((0, 0, middle01_dim[2] * 1.2))
    MIDDLE02.set_position((0, 0, middle01_dim[2]))
    MIDDLE02.set_local_position((0, 0, middle02_dim[2] * 1.2))
    MIDDLE00.set_rotation(MIDDLE00_ROT_MAX)
    MIDDLE01.set_rotation(MIDDLE01_ROT_MAX)
    MIDDLE02.set_rotation(MIDDLE02_ROT_MAX)
    THUMB00.set_position((thumb00_dim[0] * 0.75, 0, -thumb00_dim[0] * 0.25))
    THUMB00.set_local_position((0, -thumb00_dim[1] * 0.25, 0))
    THUMB01.set_position((thumb00_dim[0] * 0.65, 0, thumb00_dim[2]))
    THUMB01.set_local_position((0, 0, thumb01_dim[2] * 1.2))
    THUMB02.set_position((0, 0, thumb01_dim[2]))
    THUMB02.set_local_position((0, 0, thumb02_dim[2] * 1.2))
    THUMB00.set_local_rotation(THUMB00_ROT_MAX)
    THUMB01.set_rotation(THUMB01_ROT_MAX)
    THUMB02.set_rotation(THUMB02_ROT_MAX)


def init_shaders():
    global SHADER, VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE
    vertex_shader = Shader(gl.GL_VERTEX_SHADER,
                           SHADER_DIR + VERTEX_SHADER_SOURCE)
    fragment_shader = Shader(gl.GL_FRAGMENT_SHADER,
                             SHADER_DIR + FRAGMENT_SHADER_SOURCE)
    vertex_shader.compile()
    SHADER = ShaderProgramManager((vertex_shader, fragment_shader), True)
    return SHADER.is_linked()


def init_window():
    global ASPECT_RATIO
    disp_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
    disp_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)
    # Fixes an issue on where the display width/height of a multi-monitor
    # setup is calculated as a total of the width/height of all display
    # monitors.
    # Without the below, the result is a window with an ASPECT_RATIO ratio
    # stretched across multiple monitors.
    if int(disp_w * ASPECT_RATIO**(-1)) > disp_h:
        disp_w = int(disp_h * ASPECT_RATIO)
    elif int(disp_h * ASPECT_RATIO) > disp_w:
        disp_h = int(disp_w * ASPECT_RATIO**(-1))
    # Set the window position & size, and create the window.
    width = int(disp_w / 2)
    height = int(disp_h / 2)
    win_x = width - int(width / 2)
    win_y = height - int(height / 2)
    glut.glutInitWindowSize(width, height)
    glut.glutInitWindowPosition(win_x, win_y)
    glut.glutCreateWindow('Glovelet 3D Demo')
    glut.glutHideWindow()


def on_exit():
    global EVENT_MNGR
    print('='*10 + 'END' + '='*10)
    # EVENT_MNGR.end_dispatcher()
    time.sleep(0.8)


def main():
    global EVENT_MNGR, EVENT_DISP, EVENT_LIST,\
            PROJECTION_MTRX, LOOKAT_MTRX, ASPECT_RATIO
    atexit.register(on_exit)
    glut.glutInit(sys.argv)
    init_window()
    EVENT_DISP = GloveletSensorEventDispatcher('/dev/ttyACM0', 115200)
    EVENT_LIST = GloveletDemoController()
    EVENT_MNGR = EventDispatchManager(EVENT_DISP, EVENT_LIST)
    init_hand()
    glut.glutShowWindow()
    # Init shaders
    if not init_shaders():
        print('Failed to compile and link shader program.')
    # init OpenGL settings
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glEnable(gl.GL_DEPTH_TEST)
    # set render callback
    glut.glutDisplayFunc(draw)
    glut.glutPassiveMotionFunc(mouse_motion)
    # init perspective matrices
    PROJECTION_MTRX = glm.perspective(glm.radians(45.0), ASPECT_RATIO, 0.1, 100.0)
    LOOKAT_MTRX = glm.lookAt(glm.vec3((0.0, 2.0, -4), dtype='f'),   # eye
                              glm.vec3((0.0, 1.0, 0.0),
                                       dtype='f'),  # center
                              glm.vec3((0.0, 1.0, 0.0), dtype='f'))  # up
    # begin main loop
    EVENT_MNGR.deploy_dispatchers()
    glut.glutMainLoop()
    exit()


if __name__ == '__main__':
    main()
