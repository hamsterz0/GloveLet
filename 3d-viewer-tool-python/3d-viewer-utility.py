#!venv/bin/python
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np
import glm
import serial
import time
from ctypes import c_float, c_uint, c_void_p

from worldobject import WorldObject
from shaders import Shader
from shadermanager import ShaderProgramManager
from mesh import RectPrismMesh
from timeseries import DataTimeSeries


# glut & window values
_ASPECT_RATIO = 1920.0 / 1080.0
_MAX_FPS = 144.00
_MAX_TDELTA = 1.0 / _MAX_FPS
# shader & rendering
_SHADER_DIR = 'shaders/'
_VERTEX_SHADER_SOURCE = 'vertex_shader130.glsl'
_FRAGMENT_SHADER_SOURCE = 'fragment_shader130.glsl'
_SHADER = None
_PROJECTION_MTRX = None
_OBJ = None
_TIME = time.time()
_BAUD = 115200
_ARDUINO = serial.Serial('/dev/ttyACM0', _BAUD, timeout=1)
_DO_PRINT_FPS = False
# IMU specifications
_VZEROG = np.array([1.09375, 1.09375, 1.09375], c_float)
_ACC_BITWIDTH = 16
_ACC_VREF = 3.46
_ACC_SENSITIVITY = 4096
_GYR_BITWIDTH = 16
_GYR_VREF = 3.46
_GYR_SENSITIVITY = 4096
_MAG_BITWIDTH = 16
_MAG_VREF = 3.46
_MAG_SENSITIVITY = 4096
# time series & pre-processing
_SERIES_SIZE = 64


def print_fps(tdelta):
    print('fps: ' + '{:.2f}'.format(1 / tdelta) + '\r')


def draw():
    global _OBJ, _TIME, _PROJECTION_MTRX, _VIEW_LOOKAT
    tdelta = time.time() - _TIME
    if tdelta > _MAX_TDELTA:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        _SHADER.use()
        _SHADER.set_projection(_PROJECTION_MTRX.value)
        _SHADER.set_lookat(_VIEW_LOOKAT.value)
        # pre-process data
        # TODO: Implement data pre-processing
        _OBJ.render()
        _TIME = time.time()
        if _DO_PRINT_FPS:
            print_fps(tdelta)
    glut.glutSwapBuffers()
    glut.glutPostRedisplay()


def init_object():
    global _OBJ
    color = np.array([[1.0, 0.0, 0.0, 1.0],
                      [0.5, 0.0, 0.0, 1.0],
                      [0.0, 1.0, 0.0, 1.0],
                      [0.0, 0.5, 0.0, 1.0],
                      [0.0, 0.0, 1.0, 1.0],
                      [0.0, 0.0, 0.5, 1.0]], c_float)
    mesh = RectPrismMesh(0.05, 0.01, 0.05, face_colors=color)
    _OBJ = WorldObject(mesh)


def init_shaders():
    global _SHADER, _VERTEX_SHADER_SOURCE, _FRAGMENT_SHADER_SOURCE
    vertex_shader = Shader(gl.GL_VERTEX_SHADER,
                           _SHADER_DIR + _VERTEX_SHADER_SOURCE)
    fragment_shader = Shader(gl.GL_FRAGMENT_SHADER,
                             _SHADER_DIR + _FRAGMENT_SHADER_SOURCE)
    _SHADER = ShaderProgramManager((vertex_shader, fragment_shader), True)
    return _SHADER.is_linked()


def init_window():
    global _ASPECT_RATIO
    disp_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
    disp_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)
    # Fixes an issue on where the display width/height of a multi-monitor
    # setup is calculated as a total of the width/height of all display
    # monitors.
    # Without the below, the result is a window with an _ASPECT_RATIO ratio
    # stretched across multiple monitors.
    if int(disp_w * _ASPECT_RATIO**(-1)) > disp_h:
        disp_w = int(disp_h * _ASPECT_RATIO)
    elif int(disp_h * _ASPECT_RATIO) > disp_w:
        disp_h = int(disp_w * _ASPECT_RATIO**(-1))
    # Set the window position & size, and create the window.
    width = int(disp_w / 2)
    height = int(disp_h / 2)
    win_x = width - int(width / 2)
    win_y = height - int(height / 2)
    glut.glutInitWindowSize(width, height)
    glut.glutInitWindowPosition(win_x, win_y)
    glut.glutCreateWindow('3D Viewer Tool - TEST PROGRAM')


def main():
    global _PROJECTION_MTRX, _VIEW_LOOKAT, _ASPECT_RATIO, _TIME
    # OpenGL initialization.
    glut.glutInit(sys.argv)
    # Initialize buffer and OpenGL settings.
    # glut.glutInitDisplayMode(
    #     glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    init_window()
    # Initialize shaders.
    success = init_shaders()
    if not success:
        print('Failed to compile and link shader program.')
    # Initialize and create window, and set GLUT callback functions
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glEnable(gl.GL_DEPTH_TEST)
    # gl.glEnable(gl.GL_LIGHTING)   # TODO: Leave light disabled for now
    # gl.glShadeModel(gl.GL_SMOOTH) #
    # set display callback function
    glut.glutDisplayFunc(draw)
    # set mouse motion callback funciton
    # glut.glutPassiveMotionFunc(mouse_motion_handler)
    # set idle callback function
    # glut.glutIdleFunc(idle)
    # create perspective & look-at transformation matrices
    _PROJECTION_MTRX = glm.perspective(glm.radians(45.0), _ASPECT_RATIO, 0.1, 100.0)
    _VIEW_LOOKAT = glm.lookAt(glm.vec3((0.0, 0.0, -4), dtype=c_float),   # eye
                              glm.vec3((0.0, 0.0, 0.0), dtype=c_float),  # center
                              glm.vec3((0.0, 1.0, 0.0), dtype=c_float))  # up
    # Begin main loop.
    init_object()
    _TIME = time.time()
    glut.glutMainLoop()


if __name__ == '__main__':
    main()
