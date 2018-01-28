#!venv/bin/python
from ctypes import sizeof, c_void_p, c_float, c_uint
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np
import sys
from datetime import datetime
import math
import time
import glm
from glm.gtc import quaternion as quat

from shaders import Shader
from shadermanager import ShaderProgramManager
from mesh import RectPrismMesh
from worldobject import WorldObject

_SHADER_DIR = 'shaders/'
_vertex_shader_src = 'vertex_shader130.glsl'
_fragment_shader_src = 'fragment_shader130.glsl'
_shader_program = None
_shader = None
_log_buf_sz = 512
_aspect_ratio = 1920.0 / 1080.0
_projection = None
_rotation = None
_rot2 = glm.tquat(glm.vec3(0.0, 0.0, 0.0))
_rot_mat4 = None
_angle = 0.0
_val = 0.0
_eye = glm.vec3((0.0, 0.0, -4.0), dtype=c_float)
_center = glm.vec3((0.0, 0.0, 0.0), dtype=c_float)
_up = glm.vec3((0.0, 1.0, 0.0), dtype=c_float)
_view_lookat = glm.lookAt(_eye, _center, _up)
_test_object = None
_child1 = None
_child2 = None
_child3 = None
_child4 = None


def idle():
    pass


def mouse_motion_handler(x, y):
    pass


def key_down_handler():
    pass


def key_up_handler():
    pass


def draw():
    global _angle, _val, _rotation, _time_dif, _test_object, _shader_program, _child1, _child2, _child3, _child4
    obj = _test_object
    # tdelta = (datetime.now() - _time_dif).total_seconds()
    tdelta = time.time() - _time_dif
    print(tdelta)
    if tdelta > 0.0070:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        # use shader program
        _shader.use()
        # load GLSL transformation matrix uniform locations # FIXME: obsolete documentation
        _shader.set_projection(_projection.value)
        _shader.set_lookat(_view_lookat.value)
        _rotation = glm.tquat(glm.vec3(0.0, 2.0 * tdelta, 0.0)) * _rotation
        a = 2.0 * tdelta
        _test_object.set_rotation(_rotation)
        _child1.rotate((0.0, 0.0, a))
        _child2.rotate_local((a, 0.0, 0.0))
        _child1.rotate_local((a, 0.0, 0.0))
        _child2.rotate((0.0, 0.0, a))
        _child3.rotate_local((a, 0, 0))
        _child3.rotate((0.0, 0.0, a))
        _child4.rotate_local((a, 0, 0))
        _child4.rotate((0.0, 0.0, a))
        # render object
        obj.render()
        _time_dif = time.time()
    glut.glutSwapBuffers()
    glut.glutPostRedisplay()
    # print('fps: ' + str(1 / _time_dif.total_seconds()) + '\r')


def init_shaders():
    global _shader, _shader_program, _vertex_shader_src, _fragment_shader_src
    vertex_shader = Shader(gl.GL_VERTEX_SHADER,
                           _SHADER_DIR + _vertex_shader_src)
    fragment_shader = Shader(gl.GL_FRAGMENT_SHADER,
                             _SHADER_DIR + _fragment_shader_src)
    _shader = ShaderProgramManager((vertex_shader, fragment_shader), True)
    return _shader.is_linked()


def init_window():
    global _aspect_ratio
    disp_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
    disp_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)
    # Fixes an issue on where the display width/height of a multi-monitor
    # setup is calculated as a total of the width/height of all display
    # monitors.
    # Without the below, the result is a window with an _aspect_ratio ratio
    # stretched across multiple monitors.
    if int(disp_w * _aspect_ratio**(-1)) > disp_h:
        disp_w = int(disp_h * _aspect_ratio)
    elif int(disp_h * _aspect_ratio) > disp_w:
        disp_h = int(disp_w * _aspect_ratio**(-1))
    # Set the window position & size, and create the window.
    width = int(disp_w / 2)
    height = int(disp_h / 2)
    win_x = width - int(width / 2)
    win_y = height - int(height / 2)
    glut.glutInitWindowSize(width, height)
    glut.glutInitWindowPosition(win_x, win_y)
    glut.glutCreateWindow('3D Viewer Tool - TEST PROGRAM')


def init_test_object():
    global _test_object, _child1, _child2, _child3, _child4
    color = np.array([[1.0, 0.0, 0.0, 1.0],
                      [0.5, 0.0, 0.0, 1.0],
                      [0.0, 1.0, 0.0, 1.0],
                      [0.0, 0.5, 0.0, 1.0],
                      [0.0, 0.0, 1.0, 1.0],
                      [0.0, 0.0, 0.5, 1.0]], c_float)
    long_rect = RectPrismMesh(0.25, 0.05, 0.05, face_colors=color)
    _child1 = WorldObject(long_rect)
    _child2 = WorldObject(long_rect)
    _child3 = WorldObject(long_rect)
    _child4 = WorldObject(long_rect)
    _child1.set_local_position((1.25, 0.0, 0.0))
    _child2.set_local_position((0.0, 1.25, 0.0))
    _child3.set_local_position((-1.25, 0.0, 0.0))
    _child4.set_local_position((0.0, -1.25, 0.0))
    _child1.set_local_rotation((0.0, 0.0, 0.0))
    _child2.set_local_rotation((0.0, 0.0, glm.radians(90.0)))
    _child3.set_local_rotation((0.0, 0.0, glm.radians(180.0)))
    _child4.set_local_rotation((0.0, 0.0, glm.radians(270.0)))
    cube = RectPrismMesh(0.5, 0.5, 0.5, face_colors=color)
    _test_object = WorldObject(cube)
    _test_object.set_render_mode(gl.GL_LINE_LOOP)
    _test_object.add_child(_child1)
    _test_object.add_child(_child2)
    _test_object.add_child(_child3)
    _test_object.add_child(_child4)


def main():
    global _projection, _rotation, _time_dif, _aspect_ratio
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
    # create perspective transformation matrix
    _projection = glm.perspective(
        glm.radians(45.0), _aspect_ratio, 0.1, 100.0)
    euler = glm.vec3(-45.0, 0.0, 0.0, dtype=c_float)
    _rotation = quat.tquat(euler, dtype=c_float)
    init_test_object()
    # _time_dif = datetime.now()
    _time_dif = time.time()
    # Begin main loop.
    glut.glutMainLoop()


if __name__ == '__main__':
    main()
