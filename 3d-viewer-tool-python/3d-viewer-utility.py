#!venv/bin/python
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np
import glm
import serial
import time
import sys
from ctypes import c_float, c_int, c_uint, c_void_p

from worldobject import WorldObject
from shaders import Shader
from shadermanager import ShaderProgramManager
from mesh import RectPrismMesh
from timeseries import DataTimeSeries


# glut & window values
_ASPECT_RATIO = 1920.0 / 1080.0
_MAX_FPS = 60.00
_MAX_TDELTA = 1.0 / _MAX_FPS
# shader & rendering
_SHADER_DIR = 'shaders/'
_VERTEX_SHADER_SOURCE = 'vertex_shader130.glsl'
_FRAGMENT_SHADER_SOURCE = 'fragment_shader130.glsl'
_SHADER = None
_PROJECTION_MTRX = None
_OBJ = None
_FRAME_TIME = time.time()
_DO_PRINT_FPS = False
# serial port
_BAUD = 115200
_PORT = '/dev/ttyACM0'
_SERIAL = None
_SUCCESS_STR = 'successful@'
# IMU specifications
_DOF = 6
_ACC_VZEROG = np.array([1.09375, 1.09375, 1.09375], c_float)
_ACC_BITWIDTH = 16
_ACC_VREF = 3.46
_PREV_DATA = None
# 16384, 8192, 4096, 2048
_ACC_SENSITIVITY = 16384
_GYR_VZEROG = np.array([1.09375, 1.09375, 1.09375], c_float)
_GYR_BITWIDTH = 16
_GYR_VREF = 3.46
_GYR_SENSITIVITY = 131
_MAG_BITWIDTH = 16
_MAG_VREF = 3.46
_MAG_SENSITIVITY = 16384
# time series & pre-processing
_UPDATE_TIME = time.time()
_SERIES_SIZE = 10
_ACC_TIME_SERIES = DataTimeSeries(size=_SERIES_SIZE, dimensions=3)
_GYR_TIME_SERIES = DataTimeSeries(size=_SERIES_SIZE, dimensions=3)
_MAG_TIME_SERIES = DataTimeSeries(size=_SERIES_SIZE, dimensions=3)
_GRAV_MAGNITUDE = 0.0
_GRAV_VECTOR = glm.vec3(0, dtype=c_float)
_VELOCITY = np.zeros((3), c_float)


def print_fps(tdelta):
    print('fps: ' + '{:.2f}'.format(1 / tdelta) + '\r')


def draw():
    global _OBJ, _FRAME_TIME, _PROJECTION_MTRX, _VIEW_LOOKAT, _VELOCITY
    # pre-process data
    vel, rot = get_motion_data()
    _VELOCITY += vel
    # _OBJ.move(_VELOCITY)
    _OBJ.rotate(rot)
    tdelta = time.time() - _FRAME_TIME
    if tdelta > _MAX_TDELTA:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        _SHADER.use()
        _SHADER.set_projection(_PROJECTION_MTRX.value)
        _SHADER.set_lookat(_VIEW_LOOKAT.value)
        _OBJ.render()
        _FRAME_TIME = time.time()
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


def get_motion_data():
    """
    Returns current velocity and rotation as a tuple.
    """
    global _UPDATE_TIME, _DOF, _GRAV_MAGNITUDE, _GRAV_VECTOR, _FRAME_TIME
    acc, gyr, mag = filter_imu_data()
    tdelta = time.time() - _UPDATE_TIME
    acc_norm = np.linalg.norm(acc)
    print(acc_norm)
    gyr_norm = np.linalg.norm(gyr)
    # print(gyr_norm)
    # velocity =
    rotation = glm.tquat(glm.vec3((0, 0, 0), dtype=c_float))
    if abs(gyr_norm - 0.34) > 5.453437:
        rotation = glm.tquat(glm.vec3(gyr * tdelta))
    # grav_rot = rotation
    if _DOF == 9:
        # TODO: implement magnetometer rotation
        # 'rotation' quat multiplied by magnitometer rotation
        pass
    inv_rotation = glm.inverse_quat(rotation)
    _GRAV_VECTOR = _GRAV_VECTOR * inv_rotation * rotation
    acceleration = np.zeros((3), c_float)
    if abs(acc_norm - 1.0) > 0.0361864:
        acceleration = acc * tdelta
    grav = np.ones((3), c_float)
    grav[2] = _GRAV_MAGNITUDE
    # acceleration -= grav
    # print(acceleration)
    velocity = acceleration
    velocity[1], velocity[2] = -velocity[2], velocity[1]
    # velocity[0] = 0
    # velocity[1] = 0
    # velocity[2] = 0
    return velocity, rotation


def filter_imu_data():
    global _ACC_TIME_SERIES, _GYR_TIME_SERIES, _MAG_TIME_SERIES
    update_time_series()
    accel = _ACC_TIME_SERIES.calc_ewma()
    gyr_rot = _GYR_TIME_SERIES.calc_sma()
    mag_rot = _MAG_TIME_SERIES.calc_ewma()
    # print('accel:' + str(accel) + ', gyro:' + str(gyr_rot))
    return accel, gyr_rot, mag_rot


def convert_raw_data(data_raw):
    global _ACC_TIME_SERIES, _GYR_TIME_SERIES, _MAG_TIME_SERIES, _DOF,\
        _ACC_VREF, _ACC_VZEROG, _ACC_SENSITIVITY,\
        _GYR_VREF, _GYR_VZEROG, _GYR_SENSITIVITY,\
        _MAG_VREF, _MAG_BITWIDTH, _MAG_SENSITIVITY
    # convert raw accelerometer data
    acc = data_raw[:3]
    acc = (acc - _ACC_VZEROG) / _ACC_SENSITIVITY
    # conver raw gyroscope data
    gyr = data_raw[3:6]
    gyr = (gyr - _GYR_VZEROG) / _GYR_SENSITIVITY
    # check for 9 DoF
    mag = None
    if _DOF == 9:
        mag = glm.vec3(data_raw[6:9])
        # TODO: Implement magnitometer raw value conversion
    return acc, gyr, mag


def update_time_series():
    global _ACC_TIME_SERIES, _GYR_TIME_SERIES, _MAG_TIME_SERIES,\
        _DOF, _UPDATE_TIME
    data = get_data()
    if len(data) == _DOF:
        acc_data, gyr_data, mag_data = convert_raw_data(data)
        _ACC_TIME_SERIES.add(acc_data)
        _GYR_TIME_SERIES.add(gyr_data)
        _MAG_TIME_SERIES.add(mag_data)
    _UPDATE_TIME = time.time()


def init_serial_connection():
    global _SERIAL, _PORT, _BAUD, _SUCCESS_STR, _SERIES_SIZE,\
        _ACC_TIME_SERIES, _GRAV_MAGNITUDE, _GRAV_VECTOR
    _SERIAL = serial.Serial(_PORT, _BAUD, timeout=1)
    # check for successful connection
    while True:
        data = get_data()
        if len(data) == 3 and data[2] == _SUCCESS_STR:
            break
    # initialize time series
    for i in range(_SERIES_SIZE):
        update_time_series()
    # initialize gravity vector and magnitude
    acceleration = _ACC_TIME_SERIES.calc_ewma()
    _GRAV_MAGNITUDE = np.linalg.norm(acceleration)
    _GRAV_VECTOR = np.ones((4), c_float)
    _GRAV_VECTOR[:3] = glm.normalize(acceleration)


def get_data():
    global _SERIAL
    success = False
    while not success:
        try:
            line = _SERIAL.readline().decode('ascii')
            success = True
        except UnicodeDecodeError as e:
            print(e)
    data = line.strip().split(" ")
    if len(data) == _DOF:
        data = np.array(data, c_int)
    return data


def main():
    global _PROJECTION_MTRX, _VIEW_LOOKAT, _ASPECT_RATIO, _FRAME_TIME
    init_serial_connection()
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
    # gl.glEnable(gl.GL_LIGHTING)   # NOTE: Leave light disabled for now
    # gl.glShadeModel(gl.GL_SMOOTH) #
    # set display callback function
    glut.glutDisplayFunc(draw)
    # create perspective & look-at transformation matrices
    _PROJECTION_MTRX = glm.perspective(
        glm.radians(45.0), _ASPECT_RATIO, 0.1, 100.0)
    _VIEW_LOOKAT = glm.lookAt(glm.vec3((0.0, 2.0, -4), dtype=c_float),   # eye
                              glm.vec3((0.0, 1.0, 0.0),
                                       dtype=c_float),  # center
                              glm.vec3((0.0, 1.0, 0.0), dtype=c_float))  # up
    # Begin main loop.
    init_object()
    _FRAME_TIME = time.time()
    glut.glutMainLoop()


if __name__ == '__main__':
    main()
