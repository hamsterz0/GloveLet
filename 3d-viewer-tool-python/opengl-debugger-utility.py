#!venv/bin/python

from ctypes import sizeof, c_void_p, c_float, c_uint
import OpenGL.GL as gl
from OpenGL.arrays import vbo
import OpenGL.GLUT as glut
import numpy as np
import transforms3d as tf
import sys


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
    gl.glUseProgram(_shader_program)
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    gl.glBindVertexArray(_vao)
    gl.glEnableVertexAttribArray(0)
    # gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
    gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
    gl.glFlush()
    glut.glutSwapBuffers()


def init_shaders():
    global _shader_program
    result = True
    try:
        # Load vertex shader source and compile.
        f = open('shaders/' + _vertex_shader_src)
        vertex_src = f.read()
        f.close()
        # create and compile
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, vertex_src)
        gl.glCompileShader(vertex_shader)
        # test for shader compile success
        success = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
        if not success:
            info_log = gl.glGetShaderInfoLog(vertex_shader)
            print(info_log.decode('utf-8'))
            result = False
        # Load fragment shader source and compile
        f = open('shaders/' + _fragment_shader_src)
        fragment_src = f.read()
        f.close()
        # create and compile
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, fragment_src)
        gl.glCompileShader(fragment_shader)
        # test for shader compile success
        success = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
        if not success:
            info_log = gl.glGetShaderInfoLog(fragment_shader)
            print(info_log.decode('utf-8'))
            result = False
    except IOError as e:
        print(e.strerror)
        return False
    # create shader program
    _shader_program = gl.glCreateProgram()
    # attach shaders to the shader program
    gl.glAttachShader(_shader_program, vertex_shader)
    gl.glAttachShader(_shader_program, fragment_shader)
    # link shader program
    gl.glLinkProgram(_shader_program)
    # check success of shader program linking
    success = gl.glGetProgramiv(_shader_program, gl.GL_LINK_STATUS)
    if not success:
        info_log = gl.glGetProgramInfoLog(_shader_program)
        print(info_log)
        result = False
    # free shader objects from GPU memory (no longer needed once they have been
    # linked to the shader program)
    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)
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
    global _vao, _vbo
    # gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    vertices = np.array([[0.5, 0.5, 0.0],
                         [0.5, -0.5, 0.0],
                         [-0.5, -0.5, 0.0],
                         [-0.5, 0.5, 0.0]], dtype=c_float)
    indices = np.array([[0, 1, 3],
                        [1, 2, 3]], dtype=c_uint)
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
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    indices, gl.GL_STATIC_DRAW)
    gl.glVertexAttribPointer(
        0, vertices.shape[1], gl.GL_FLOAT, False,
        vertices.shape[1] * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
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
    glut.glutPassiveMotionFunc(mouse_motion_handler)
    # set idle callback function
    glut.glutIdleFunc(idle)
    # Begin main loop.
    init_test_object()
    glut.glutMainLoop()


if __name__ == '__main__':
    main()
