from shadermanager import CURRENT_PROGRAM as shader
from ctypes import c_uint, c_float, c_void_p, sizeof
import OpenGL.GL as gl
import numpy as np

DEFAULT_RENDER_MODE = gl.GL_TRIANGLES
DEFAULT_BUFFER_USAGE = gl.GL_DYNAMIC_DRAW
DEFAULT_COLOR = np.array([1.0, 1.0, 1.0, 1.0], c_float)


class Mesh:
    _vao = -1
    _vbo = -1
    _ebo = -1
    _render_mode = DEFAULT_RENDER_MODE
    _buffer_usage = DEFAULT_BUFFER_USAGE
    _vert_sz = 3
    _elem_sz = 3
    _color = DEFAULT_COLOR
    vertices = None
    elements = None

    def __init__(self, vertices, elements,
                 render_mode=DEFAULT_RENDER_MODE,
                 buffer_usage=DEFAULT_BUFFER_USAGE,
                 color=DEFAULT_COLOR):
        self._render_mode = render_mode
        self._buffer_usage = buffer_usage
        self._vert_sz = vertices.shape[1]
        self._elem_sz = elements.shape[1]
        self.vertices = vertices
        self.elements = elements
        # generate buffers
        self._vao = gl.glGenVertexArrays(1)
        self._vbo = gl.glGenBuffers(1)
        self._ebo = gl.glGenBuffers(1)
        # bind Vertex Array Object
        gl.glBindVertexArray(self._vao)
        # bind Vertex Buffer Object
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, buffer_usage)
        # bind Element Buffer Object
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, elements, buffer_usage)
        # configure vertex attributes for position
        vert_sz = vertices.shape[1]
        gl.glVertexAttribPointer(0, vert_sz, gl.GL_FLOAT, False,
                                 vert_sz * sizeof(c_float), c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        # Unbind the VAO so that other calls won't
        # accidentally modify this VAO.
        # May be unnecessary, because another call will have to use
        # glBindVertexArray to modify a VAO anyway.
        gl.glBindVertexArray(0)

    def render(self):
        # bind Vertex Array Object
        sz = self.elements.size
        gl.glBindVertexArray(self._vao)
        gl.glDrawElements(self._render_mode, sz, gl.GL_UNSIGNED_INT, None)
