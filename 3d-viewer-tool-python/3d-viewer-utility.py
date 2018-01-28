import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np
import glm
from ctypes import c_float, c_uint, c_void_p

from worldobject import WorldObject
from shadermanager import ShaderProgramManager


_SHADER_DIR = 'shaders/'
_VERTEX_SHADER_SOURCE = 'vertex_shader130.glsl'
_FRAGMENT_SHADER_SOURCE = 'fragment_shader130.glsl'
_SHADER = None
_ASPECT_RATIO = 1920.0 / 1080.0
_PROJECTION = None
_OBJ = None

def draw():
    pass


def init_shaders():
    global _SHADER, _VERTEX_SHADER_SOURCE, _FRAGMENT_SHADER_SOURCE
    vertex_shader = Shader(gl.GL_VERTEX_SHADER,
                           _SHADER_DIR + _VERTEX_SHADER_SOURCE)
    fragment_shader = Shader(gl.GL_FRAGMENT_SHADER,
                             _SHADER_DIR + _FRAGMENT_SHADER_SOURCE)
    _SHADER = ShaderProgramManager((vertex_shader, fragment_shader), True)
    return _shader.is_linked()


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
    global _PROJECTION, _ASPECT_RATIO
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
    _PROJECTION = glm.perspective(
        glm.radians(45.0), _ASPECT_RATIO, 0.1, 100.0)
    # Begin main loop.
    glut.glutMainLoop()


if __name__ == '__main__':
    main()
