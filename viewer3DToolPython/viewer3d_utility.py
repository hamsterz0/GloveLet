#!../venv/bin/python
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLUT.freeglut
import numpy as np
import glm
import time
import sys
import argparse
import atexit
from ctypes import c_float, c_int, c_uint, c_void_p


from glovelet.viewer3DToolPython.worldobject import WorldObject
from glovelet.viewer3DToolPython.shaders import Shader
from glovelet.viewer3DToolPython.shadermanager import ShaderProgramManager
from glovelet.viewer3DToolPython.mesh import RectPrismMesh
from glovelet.utility.timeseries import DataTimeSeries
from glovelet.sensorapi.sensorstream import SensorStream
from glovelet.sensorapi.glovelet_sensormonitor import GloveletBNO055IMUSensorMonitor
from glovelet.eventapi.event import EventDispatcherManager
from glovelet.eventapi.glovelet_hardware_events import GloveletImuEventDispatcher, GloveletImuListener


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
_ACC_SENSITIVITY = 16384  # 16384, 8192, 4096, 2048
_GYR_VRO = np.array([0.2, 0.2, 4.0], c_float)
_GYR_BITWIDTH = 16
_GYR_VREF = 3.46
_GYR_SENSITIVITY = 131  # 131, 65.5, 32.8, 16.4
_MAG_BITWIDTH = 16
_MAG_VREF = 3.46
_MAG_SENSITIVITY = 16384
# time series & pre-processing
_UPDATE_TIME = time.time()
_SERIES_SIZE = 10
_DATA_SERIES = None
_PREV_ATT = None
_YAW_NORM = None
_GRAV_MAGNITUDE = 0.0
_GRAV_VECTOR = glm.vec3(0, dtype=c_float)
_VELOCITY = np.zeros((3), c_float)
# SensorStream
_SENSOR_STREAM = None
_IMU_MONITOR = GloveletBNO055IMUSensorMonitor()
# Event API
_EVENT_DISPATCHER = None
_LISTENER = GloveletImuListener()
_EVENT_MANAGER = EventDispatcherManager()


def on_exit():
    print('='*10 + 'END' + '='*10)
    _EVENT_MANAGER.end_dispatcher()
    while not _EVENT_DISPATCHER.is_deployed:
        continue


def print_fps(tdelta):
    print('fps: ' + '{:.2f}'.format(1 / tdelta) + '\r')


def draw():
    global _OBJ, _FRAME_TIME, _PROJECTION_MTRX, _VIEW_LOOKAT, _VELOCITY
    # pre-process data
    # vel, rot, att = get_motion_data()
    # _SENSOR_STREAM.update()
    # rot = _IMU_MONITOR.get_rotation()
    # vel = _IMU_MONITOR.get_velocity()
    # _OBJ.move(vel)
    # sys.stdout.write('is_moving = {}                           \r'.format(int(_IMU_MONITOR.is_moving())))
    _EVENT_MANAGER.invoke_dispatch()
    print(_LISTENER.orientation[0])
    _OBJ.set_local_rotation(_LISTENER.orientation[0])
    tdelta = time.time() - _FRAME_TIME
    if tdelta > _MAX_TDELTA:
        # rot = np.zeros(3, c_float)
        # rot[:] = glm.eulerAngles(_OBJ.local_rotation)[:]
        # rot = np.degrees(rot)
        # print(np.array2string(rot, precision=4, sign=' ', floatmode='fixed'))
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


def get_motion_data():
    """
    Returns current velocity and rotation as a tuple.
    """
    global _DOF, _GRAV_MAGNITUDE, _GRAV_VECTOR, _FRAME_TIME, _DATA_SERIES
    update_time_series()
    data = _DATA_SERIES[0]
    acc, gyr = data[:3], data[3:6]
    mag = None
    if _DOF == 9:
        mag = data[6:9]
    tdelta = _DATA_SERIES.get_tdelta()
    # acc_norm = np.linalg.norm(acc)
    # print(acc_norm)
    # gyr_norm = np.linalg.norm(gyr)
    # print(gyr_norm)
    print(np.array2string(acc, precision=4) + " :: " + np.array2string(gyr, precision=4))
    attitude_est = attitude_estimation(acc)
    rotation = complementary_filter(attitude_est)
    attitude_est[1] = 0
    rotation = glm.tquat(glm.vec3(rotation))
    rot_mat4 = glm.mat4_cast(rotation)
    grav = _GRAV_VECTOR * rot_mat4
    grav[0] = -grav[0]
    grav[2] = -grav[2]
    # print(acc - grav[:3])
    # velocity = (acc - grav[:3]) * tdelta * 9.8
    velocity = (acc - grav[:3]) * tdelta
    # print(np.linalg.norm(velocity))
    velocity[0] = 0
    velocity[1] = -velocity[1]
    velocity[2] = 0
    if _DOF == 9:
        # rotation = glm.tquat(glm.vec3((0, 0, 0), dtype=c_float))
        # TODO: implement magnetometer rotation
        # 'rotation' quat multiplied by magnitometer rotation
        pass
    # rotation[1] = 0
    # rotation = glm.normalize_quat(rotation)
    return velocity, rotation, attitude_est


def attitude_estimation(acc):
    global _DATA_SERIES, _PREV_ATT
    rad = np.pi / 2
    # pitch = np.math.atan(acc[2] / np.math.sqrt(acc[0]**2 + acc[1]**2))
    pitch = np.math.atan2(acc[2], np.math.sqrt(acc[0]**2 + acc[1]**2))
    yaw = 0.0
    roll = np.math.atan2(acc[1], acc[0])
    att_rot = glm.vec3([pitch, yaw, roll - rad * 3], dtype=c_float)
    return att_rot


def complementary_filter(att_est, alpha=1.0):
    global _DATA_SERIES, _PREV_ATT
    data = _DATA_SERIES[0][3:6]
    dt = _DATA_SERIES.get_tdelta()
    data *= dt
    result = np.zeros(3, c_float)
    for i in range(3):
        result[i] = (1 - alpha) * (_PREV_ATT[i] + data[i]) + alpha * att_est[i]
    _PREV_ATT = att_est
    return result


def convert_raw_data(data_series):
    """
    Callback function to be used with DataTimeSeries post_filter constructor argument.
    \t
    \tdata_series:    DataTimeSeries callback requires this parameter
    """
    global _ACC_VZEROG, _ACC_SENSITIVITY,\
        _GYR_VRO, _GYR_SENSITIVITY,\
        _MAG_SENSITIVITY
    # get filtered data
    data = data_series[0]
    # convert raw accelerometer data
    data[:3] = (data[:3] - _ACC_VZEROG) / _ACC_SENSITIVITY
    data[2] = -data[2]                   # invert z
    data[1], data[2] = data[2], data[1]  # swap y and z
    # convert raw gyroscope data
    data[3:6] = (data[3:6] - _GYR_VRO) / _GYR_SENSITIVITY
    data[3:6] = np.radians(data[3:6])    # degrees -> radians
    data[4] = -data[4]                   # invert y (roll)
    data[4], data[5] = data[5], data[4]  # swap y and z
    # check for 9 DoF
    mag = None
    if data_series.shape[1] == 9:
        # TODO: Implement magnitometer raw value conversion
        pass
    return data


def update_time_series():
    global _DATA_SERIES, _DOF, _UPDATE_TIME
    data = read_data()
    while len(data) != _DOF:
        data = read_data()
    _DATA_SERIES.add(data)


def init_serial_connection():
    global _SENSOR_STREAM, _IMU_MONITOR, _PORT, _BAUD
    _SENSOR_STREAM = SensorStream(_PORT, _BAUD)
    _SENSOR_STREAM.register_monitor(_IMU_MONITOR)
    _SENSOR_STREAM.open()

# def init_serial_connection():
#     global _SERIAL, _PORT, _BAUD, _SUCCESS_STR, _SERIES_SIZE,\
#         _GRAV_MAGNITUDE, _GRAV_VECTOR, _DATA_SERIES
#     _SERIAL = serial.Serial(_PORT, _BAUD, timeout=1)
#     # check for successful connection
#     while True:
#         data = read_data()
#         if len(data) == 3 and data[2] == _SUCCESS_STR:
#             break
#     # initialize time series
#     _GRAV_VECTOR = np.zeros(4, c_float)
#     # Values of IMU don't stablize until after about _SERIES_SIZE records.
#     # Do extra updates of the time series in order to insure correct mean calculations.
#     for i in range(_SERIES_SIZE * 3):
#         update_time_series()
#     _GRAV_VECTOR = glm.vec4()
#     _GRAV_VECTOR[:3] = _DATA_SERIES.calc_sma()[:3]


def read_data():
    global _SERIAL
    success = False
    line = None
    data = None
    while not success:
        try:
            line = _SERIAL.readline().decode('ascii')
            success = True
        except UnicodeDecodeError as e:
            print(e)
            continue
        data = line.strip().split(" ")
        if len(data) == _DOF:
            try:
                data = np.array(data, c_int)
                success = True
            except ValueError as e:
                print(e)
                continue
    return data


def init_object():
    global _OBJ, _IMU_MONITOR
    color = np.array([[1.0, 0.0, 0.0, 1.0],
                      [0.5, 0.0, 0.0, 1.0],
                      [0.0, 1.0, 0.0, 1.0],
                      [0.0, 0.5, 0.0, 1.0],
                      [0.0, 0.0, 1.0, 1.0],
                      [0.0, 0.0, 0.5, 1.0]], c_float)
    mesh = RectPrismMesh(0.05, 0.01, 0.05, face_colors=color)
    _OBJ = WorldObject(mesh)
    _OBJ.set_local_rotation(_LISTENER.orientation[0])


# def init_object():
#     global _OBJ, _PREV_ATT, _DATA_SERIES
#     color = np.array([[1.0, 0.0, 0.0, 1.0],
#                       [0.5, 0.0, 0.0, 1.0],
#                       [0.0, 1.0, 0.0, 1.0],
#                       [0.0, 0.5, 0.0, 1.0],
#                       [0.0, 0.0, 1.0, 1.0],
#                       [0.0, 0.0, 0.5, 1.0]], c_float)
#     mesh = RectPrismMesh(0.05, 0.01, 0.05, face_colors=color)
#     _OBJ = WorldObject(mesh)
#     acc = _DATA_SERIES[0][:3]
#     _PREV_ATT = np.zeros(3, c_float)
#     att_est = attitude_estimation(acc)
#     _OBJ.set_local_rotation(glm.tquat(glm.vec3(att_est)))
#     _PREV_ATT = att_est


def init_shaders():
    global _SHADER, _VERTEX_SHADER_SOURCE, _FRAGMENT_SHADER_SOURCE
    vertex_shader = Shader(gl.GL_VERTEX_SHADER,
                           _SHADER_DIR + _VERTEX_SHADER_SOURCE)
    fragment_shader = Shader(gl.GL_FRAGMENT_SHADER,
                             _SHADER_DIR + _FRAGMENT_SHADER_SOURCE)
    vertex_shader.compile()
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
    glut.glutHideWindow()


def main():
    global _PROJECTION_MTRX, _VIEW_LOOKAT, _ASPECT_RATIO, _FRAME_TIME, _DATA_SERIES, _EVENT_DISPATCHER
    _DATA_SERIES = DataTimeSeries(_SERIES_SIZE, 6, auto_filter=True, post_filter=convert_raw_data)
    atexit.register(on_exit)
    # OpenGL initialization.
    print(sys.argv)
    glut.glutInit(sys.argv)
    OpenGL.GLUT.freeglut.glutSetOption(OpenGL.GLUT.GLUT_ACTION_ON_WINDOW_CLOSE, OpenGL.GLUT.GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    # Initialize buffer and OpenGL settings.
    # glut.glutInitDisplayMode(
    #     glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    init_window()
    # init_serial_connection()
    _EVENT_DISPATCHER = GloveletImuEventDispatcher(_PORT, _BAUD)
    _EVENT_MANAGER.register_dispatcher(_EVENT_DISPATCHER)
    _EVENT_MANAGER.register_listener(_LISTENER)
    _EVENT_MANAGER.deploy_dispatcher()
    while _LISTENER.acceleration is None:
        _EVENT_MANAGER.invoke_dispatch()
    init_object()
    glut.glutShowWindow()
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
    _FRAME_TIME = time.time()
    glut.glutMainLoop()
    _EVENT_MANAGER.end_dispatcher()
    exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', default='/dev/ttyACM0', type=str, help='the serial port to read from.')
    parser.add_argument('--baud', '-b', default=115200, type=int, help='the baudrate of the serial port device.')
    args = parser.parse_args()
    _PORT = args.port
    _BAUD = args.baud
    main()
