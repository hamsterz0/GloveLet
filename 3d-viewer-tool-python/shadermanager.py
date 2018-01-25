from shaders import ShaderProgram
import OpenGL.GL as gl
from sys import stderr

CURRENT_PROGRAM = None

_UNIFORM_TYPE_INT = 0
_UNIFORM_TYPE_UINT = 1
_UNIFORM_TYPE_VEC4 = 2
_UNIFORM_TYPE_MAT4 = 3


# TODO: Add support for switching shader programs
class ShaderProgramManager(ShaderProgram):
    _start = list()
    _end = 0
    _model_index = -1

    def __init__(self, shaders=[], do_link=False):
        super().__init__(shaders, do_link)

    def use(self):
        super().use()

    def set_projection(self, matrix):
        """
        Set the projection transformation matrix.
        """
        self._push_uniform(matrix, 'projection')

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

    def push(self):
        """
        Call before *any* calls to model_mat4().\n
        Indicates to the ShaderProgramManager to begin
        tracking the number of matrices pushed onto the stack.\n
        The paired call to pop() will pop all matrices pushed
        to the stack from the time push() is called.
        """
        self._start.append(self._model_index)

    def pop(self):
        """
        Pops all matrices from the stack that  were pushed to the stack
        from the time of the paired call to push().
        """
        start = self._start.pop()
        end = self._model_index
        self.pop_model_mat4(end - start)

    def model_mat4(self, matrix):
        """
        Push a transformation matrix to the model transformation.
        The Model Transformation occurs prior to the View Transformation.\n
        Attention:
        \t
        \tCall push() method prior to pushing matrices to the stack.
        \t
        \tOtherwise, matrices must be popped from the stack
        \tmanually with pop_model_mat4() method.
        """
        if len(self._start) == 0:
            print('ERR: ShaderProgamManager.push() method was not called before \
attempting to push a matrix.', file=stderr)
            return
        self._model_index += 1
        uniform = 'model[' + str(self._model_index) + ']'
        self._push_uniform(matrix, uniform)
        self._push_uniform(self._model_index, 'model_index',
                           uniform_type=_UNIFORM_TYPE_INT)

    def pop_model_mat4(self, count=1):
        self._model_index -= count
        while len(self._start) > 0 and self._start[-1] <= self._model_index:
            self._start.pop()
        if self._model_index < -1:
            self._model_index = -1

    def color_vec4(self, color):
        self._push_uniform(color, 'color', uniform_type=_UNIFORM_TYPE_VEC4)

    def _push_uniform(self, data, uniform, uniform_type=_UNIFORM_TYPE_MAT4):
        result = False
        loc = gl.glGetUniformLocation(self._id, uniform)
        if loc != -1:
            if uniform_type == _UNIFORM_TYPE_INT:
                gl.glUniform1i(loc, data)
                result = True
            elif uniform_type == _UNIFORM_TYPE_UINT:
                gl.glUniform1ui(loc, data)
                result = True
            elif uniform_type == _UNIFORM_TYPE_VEC4:
                gl.glUniform4fv(loc, 1, data)
            elif uniform_type == _UNIFORM_TYPE_MAT4:
                gl.glUniformMatrix4fv(loc, 1, False, data)
                result = True
        return result
