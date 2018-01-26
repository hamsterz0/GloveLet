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

from shaders import Shader, ShaderProgram
from shadermanager import ShaderProgramManager
from shadermanager import CURRENT_PROGRAM, _UNIFORM_TYPE_VEC4

_SHADER_DIR = 'shaders/'
_vertex_shader_src = 'vertex_shader130.glsl'
_fragment_shader_src = 'fragment_shader130.glsl'
_shader_program = None
_shader = None
_vao = 0
_vbo = 0
_ebo = 0
_log_buf_sz = 512
_aspect_ratio = 1920.0 / 1080.0
_projection = None
_rotation = None
_position = glm.vec3(0.0, 0.0, 0.0, dtype=c_float)
_rot_mat4 = None
_angle = 0.0


def idle():
    pass


def mouse_motion_handler(x, y):
    pass


def draw():
    global _angle, _rotation, _position, _rot_mat4, _time_dif
    # tdelta = (datetime.now() - _time_dif).total_seconds()
    tdelta = time.time() - _time_dif
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glEnable(gl.GL_DEPTH_TEST)
    # use shader program
    _shader.use()
    # load GLSL transformation matrix uniform locations # FIXME: obsolete documentation
    _shader.set_projection(_projection.value)
    _shader.set_view_mat4(glm.translate(
        glm.mat4(1.0), glm.vec3(0.0, 0.0, -4.0)).value)
    _rotation = glm.tquat(glm.vec3(0.0, 90.0 * tdelta, 0.0)) * _rotation
    _angle += 135.0 * tdelta
    _position[0] = math.sin(_angle)
    translate = glm.translate(glm.mat4(1.0), _position).value
    _rot_mat4 = glm.mat4_cast(_rotation).value
    _shader.push()
    _shader.model_mat4(glm.mat4(1.0).value)
    _shader.model_mat4(translate)
    _shader.model_mat4(_rot_mat4)
    # bind Vertex Array Object
    gl.glBindVertexArray(_vao)
    sz = sizeof(c_uint)
    _shader.color_vec4(np.array([0.5, 0.0, 0.0, 1.0]))
    gl.glDrawElements(gl.GL_QUADS, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 0))
    _shader.color_vec4(np.array([0.0, 0.0, 1.0, 1.0]))
    gl.glDrawElements(gl.GL_QUADS, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 4))
    _shader.color_vec4(np.array([1.0, 0.0, 0.0, 1.0]))
    gl.glDrawElements(gl.GL_QUADS, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 8))
    _shader.color_vec4(np.array([0.0, 0.0, 0.5, 1.0]))
    gl.glDrawElements(gl.GL_QUADS, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 12))
    _shader.color_vec4(np.array([0.0, 1.0, 0.0, 1.0]))
    gl.glDrawElements(gl.GL_QUADS, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 16))
    _shader.color_vec4(np.array([0.0, 0.5, 0.0, 1.0]))
    gl.glDrawElements(gl.GL_QUADS, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 20))
    glut.glutSwapBuffers()
    _shader.pop()
    glut.glutPostRedisplay()
    _time_dif = time.time()
    # print('fps: ' + str(1 / _time_dif.total_seconds()) + '\r')


def init_shaders():
    global _shader, _shader_program, _vertex_shader_src, _fragment_shader_src
    vertex_shader = Shader(gl.GL_VERTEX_SHADER,
                           _SHADER_DIR + _vertex_shader_src)
    fragment_shader = Shader(gl.GL_FRAGMENT_SHADER,
                             _SHADER_DIR + _fragment_shader_src)
    # _shader_program = ShaderProgram((vertex_shader, fragment_shader), True)
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
    global _vao, _vbo, _ebo
    vertices = np.array([[-0.5, -0.5, -0.5],
                         [-0.5, -0.5, 0.5],
                         [-0.5, 0.5, 0.5],
                         [-0.5, 0.5, -0.5],
                         [0.5, 0.5, 0.5],
                         [0.5, 0.5, -0.5],
                         [0.5, -0.5, -0.5],
                         [0.5, -0.5, 0.5]],
                        dtype=c_float)
    indices = np.array([[0, 1, 2, 3],   # left (-x)
                        [1, 7, 4, 2],   # front (+z)
                        [4, 5, 6, 7],   # right (+x)
                        [6, 0, 3, 5],   # back (-z)
                        [2, 4, 5, 3],   # top (+y)
                        [0, 1, 7, 6]],  # bottom (-y)
                       dtype=c_uint)
    # generate buffers
    _vao = gl.glGenVertexArrays(1)
    _vbo = gl.glGenBuffers(1)
    _ebo = gl.glGenBuffers(1)
    # bind Vertex Array Object
    gl.glBindVertexArray(_vao)
    # bind Vertex Buffer Object
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, _vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, gl.GL_DYNAMIC_DRAW)
    # bind Element Buffer Object
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, _ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_DYNAMIC_DRAW)
    # configure vertex attributes for position
    vert_sz = vertices.shape[1]
    gl.glVertexAttribPointer(0, vert_sz, gl.GL_FLOAT, False,
                             vert_sz * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    # Unbind the VAO so that other calls won't accidentally modify this VAO.
    # May be unnecessary, because another call will have to use
    # glBindVertexArray to modify a VAO anyway.
    gl.glBindVertexArray(0)


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
