#!venv/bin/python
from ctypes import sizeof, c_void_p, c_float, c_uint
import OpenGL.GL as gl
from OpenGL.arrays import vbo
import OpenGL.GLUT as glut
import numpy as np
import transforms3d as tf
import sys
import time
import math

from shaders import Shader, ShaderProgram

_vertex_shader_src = 'vertex_shader.glsl'
_fragment_shader_src = 'fragment_shader.glsl'
_shader_program = 0
_vao = 0
_vbo = 0
_ebo = 0
_log_buf_sz = 512


def idle():
    pass


def mouse_motion_handler(x, y):
    pass


def draw():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    # instruct to use shader program
    gl.glUseProgram(_shader_program)
    # bind Vertex Array Object
    gl.glBindVertexArray(_vao)
    gl.glEnableVertexAttribArray(0)
    gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
    glut.glutSwapBuffers()
    glut.glutPostRedisplay()


def init_shaders():
    global _shader_program, _vertex_shader_src, _fragment_shader_src
    vertex_shader = Shader(gl.GL_VERTEX_SHADER, _vertex_shader_src)
    fragment_shader = Shader(gl.GL_FRAGMENT_SHADER, _fragment_shader_src)
    _shader_program = ShaderProgram((vertex_shader, fragment_shader), True)
    print(vertex_shader.get_ID())
    print(fragment_shader.get_ID())
    result = _shader_program.is_linked()
    _shader_program = _shader_program.get_ID()
    return result


def init_window():
    disp_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
    disp_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)
    width_aspect = 1920.0 / 1080.0
    height_aspect = width_aspect**(-1)
    # Fixes an issue on where the display width/height of a multi-monitor
    # setup is calculated as a total of the width/height of all display
    # monitors.
    # Without the below, the result is a window with an aspect ratio
    # stretched across multiple monitors.
    if int(disp_w * height_aspect) > disp_h:
        disp_w = int(disp_h * width_aspect)
    elif int(disp_h * width_aspect) > disp_w:
        disp_h = int(disp_w * height_aspect)
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
    #                     positions      |      color
    vertices = np.array([[0.5, 0.5, 0.0], [1.0, 0.0, 0.0],
                         [0.5, -0.5, 0.0], [0.0, 1.0, 0.0],
                         [-0.5, -0.5, 0.0], [1.0, 0.0, 0.0],
                         [-0.5, 0.5, 0.0], [0.0, 0.0, 1.0]],
                        dtype=c_float)
    indices = np.array([[0, 1, 3], [1, 2, 3]], dtype=c_uint)
    # generate buffers
    _vao = gl.glGenVertexArrays(1)
    _vbo = gl.glGenBuffers(1)
    _ebo = gl.glGenBuffers(1)
    # bind Vertex Array Object
    gl.glBindVertexArray(_vao)
    # bind Vertex Buffer Object
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, _vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, gl.GL_STATIC_DRAW)
    # bind Element Buffer Object
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, _ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)
    vert_sz = vertices.shape[1]
    # configure vertex attributes for position
    gl.glVertexAttribPointer(0, vert_sz, gl.GL_FLOAT, False,
                             2 * vert_sz * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    # configure vertex attributes for color
    gl.glVertexAttribPointer(1, vert_sz, gl.GL_FLOAT, False,
                             2 * vert_sz * sizeof(c_float),
                             c_void_p(vert_sz * sizeof(c_float)))
    gl.glEnableVertexAttribArray(1)
    # Unbind the VAO so that other calls won't accidentally modify this VAO.
    # May be unnecessary, because another call will have to use
    # glBindVertexArray to modify a VAO anyway.
    gl.glBindVertexArray(0)


def main():
    # OpenGL initialization.
    glut.glutInit(sys.argv)
    # Initialize buffer and OpenGL settings.
    # glut.glutInitDisplayMode(
    #     glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    init_window()
    # Initialize shaders.
    if not init_shaders():
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
    # Begin main loop.
    init_test_object()
    glut.glutMainLoop()


if __name__ == '__main__':
    main()
