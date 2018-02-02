from ctypes import c_uint, c_float, c_void_p, sizeof
import OpenGL.GL as gl
import numpy as np
import shadermanager as sm

DEFAULT_RENDER_MODE = gl.GL_TRIANGLES
DEFAULT_BUFFER_USAGE = gl.GL_DYNAMIC_DRAW
DEFAULT_COLOR = np.array([1.0, 1.0, 1.0, 1.0], c_float)


class Mesh:
    def __init__(self, vertices, elements,
                 render_mode=DEFAULT_RENDER_MODE,
                 buffer_usage=DEFAULT_BUFFER_USAGE,
                 color=DEFAULT_COLOR):
        # generate buffers
        self._vao = gl.glGenVertexArrays(1)
        self._vbo = gl.glGenBuffers(1)
        self._ebo = gl.glGenBuffers(1)
        # set rendering flags
        self._render_mode = render_mode
        self._buffer_usage = buffer_usage
        self._vert_sz = vertices.shape[1]
        self._elem_sz = elements.shape[1]
        self.vertices = vertices
        self.elements = elements
        self._color = color
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

    def set_render_mode(self, mode):
        if type(mode) == gl.constant.IntConstant:
            self._render_mode = mode
        else:
            print("ERR: Mesh.set_render_mode: argument must be an OpenGL constant.")


class RectPrismMesh(Mesh):
    _width = _height = _depth = 0.5
    _face_colors = None

    def __init__(self, width, height, depth,
                 buffer_usage=DEFAULT_BUFFER_USAGE,
                 face_colors=DEFAULT_COLOR):
        _width, _height, _depth = width, height, depth
        verts = np.array([[-width, -height, -depth],
                          [-width, -height, depth],
                          [-width, height, depth],
                          [-width, height, -depth],
                          [width, height, depth],
                          [width, height, -depth],
                          [width, -height, -depth],
                          [width, -height, depth]],
                         dtype=c_float)
        elems = np.array([[4, 5, 6, 7],   # right (+x)
                          [0, 1, 2, 3],   # left (-x)
                          [1, 7, 4, 2],   # front (+z)
                          [6, 0, 3, 5],   # back (-z)
                          [2, 4, 5, 3],   # top (+y)
                          [0, 1, 7, 6]],  # bottom (-y)
                         dtype=c_uint)
        if not type(face_colors) == np.ndarray and face_colors.shape == (6, 4):
            self._face_colors = np.zeros((6, 4), c_float)
            for i in range(face_colors.shape[0]):
                self._face_colors[i, :] = DEFAULT_COLOR
        else:
            self._face_colors = face_colors
        super().__init__(verts, elems, gl.GL_QUADS, buffer_usage)

    def render(self):
        # bind Vertex Array Object
        gl.glBindVertexArray(self._vao)
        sz = sizeof(c_uint)
        sm.CURRENT_PROGRAM.color_vec4(self._face_colors[0])
        gl.glDrawElements(self._render_mode, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 0))
        sm.CURRENT_PROGRAM.color_vec4(self._face_colors[1])
        gl.glDrawElements(self._render_mode, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 4))
        sm.CURRENT_PROGRAM.color_vec4(self._face_colors[4])
        gl.glDrawElements(self._render_mode, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 8))
        sm.CURRENT_PROGRAM.color_vec4(self._face_colors[5])
        gl.glDrawElements(self._render_mode, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 12))
        sm.CURRENT_PROGRAM.color_vec4(self._face_colors[2])
        gl.glDrawElements(self._render_mode, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 16))
        sm.CURRENT_PROGRAM.color_vec4(self._face_colors[3])
        gl.glDrawElements(self._render_mode, 4, gl.GL_UNSIGNED_INT, c_void_p(sz * 20))
