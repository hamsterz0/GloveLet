from shaders import Shader, ShaderProgram
import OpenGL.GL as gl
import glm
import numpy as np
from ctypes import c_uint

_UNIFORM_TYPE_MAT4 = 0
_UNIFORM_TYPE_UINT = 1


class ShaderProgramManager(ShaderProgram):
    _model_index = 0

    def __init__(self, shaders=[], do_link=False):
        ShaderProgram(shaders=[], do_link=False)

    def set_lookat(self, matrix):
        """
        Right-multiplied by the view matrix.
        Intended to be used to perform the 'look-at' transformation of the
        view/camera.
        """
        self._push_uniform(matrix, 'view_lookat')

    def set_view_mat4(self, matrix):
        """
        Left-multiplied against the 'look-at' transformation matrix.
        Should be used to perform any view/camera translations.
        """
        self._push_uniform(matrix, 'view')

    def push_model_mat4(self, matrix):
        """
        Push a transformation matrix to the model transformation.
        The Model Transformation occurs prior to the View Transformation.
        """
        self._push_uniform(matrix, 'model[' + str(self._model_index) + ']')
        self._push_uniform(c_uint(self._model_index + 1),
                           'model_ct', uniform_type=_UNIFORM_TYPE_UINT)
        self._model_index += 1

    def pop_model_mat4(self, count=1):
        self._model_index -= count
        if self._model_index < 0:
            self._model_index = 0

    def _push_uniform_mat4(self, data, uniform, uniform_type=_UNIFORM_TYPE_MAT4):
        result = False
        if type(data) is not np.matrixlib.defmatrix.matrix:
            return result
        loc = gl.glGetUniformLocation(self._id, uniform)
        if loc != -1:
            if uniform_type == _UNIFORM_TYPE_MAT4:
                gl.glUniformMatrix4fv(loc, 1, False, data)
                result = True
            elif uniform_type == _UNIFORM_TYPE_UINT:
                gl.glUniform1ui(loc, data)
                result = True
        return result
