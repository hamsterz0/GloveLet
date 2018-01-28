import OpenGL.GL as gl


class Shader:
    _is_compiled = False
    _failed_to_compile = False
    _type = None
    _path = str()
    _id = 0

    def __init__(self, shader_type, shader_source, do_compile=False):
        self._path = shader_source
        self._type = shader_type
        # create shader object and set source
        self._id = gl.glCreateShader(self._type)
        if do_compile:
            self.compile()

    def compile(self):
        result = True
        if self._is_compiled:
            return result
        try:
            # load vertex shader source
            f = open(self._path)
            source = f.read()
            f.close()
            # attach source code to shader object
            gl.glShaderSource(self._id, source)
            # compile shader source
            gl.glCompileShader(self._id)
            # test for shader compile success
            success = gl.glGetShaderiv(self._id, gl.GL_COMPILE_STATUS)
            if not success:
                info_log = gl.glGetShaderInfoLog(self._id)
                print(info_log.decode('utf-8'))
                result = False
        except IOError as e:
            print(e.strerror)
            result = False
            self._failed_to_compile = True
        self._is_compiled = result
        return result

    def is_compiled(self):
        return self._is_compiled

    def failed_compile(self):
        return self._failed_to_compile

    def get_ID(self):
        return self._id

    def get_type(self):
        return self._type

    def get_source_path(self):
        return self._path

    def delete_shader(self):
        gl.glDeleteShader(self._id)


class ShaderProgram:
    _is_linked = False
    _id = 0
    _shaders = dict()

    def __init__(self, shaders=[], do_link=False):
        self._id = gl.glCreateProgram()
        if len(shaders) <= 0:
            do_link = False
        else:
            for shader in shaders:
                self._shaders[shader.get_ID()] = shader
                self.attach_shader(shader)
        if do_link:
            self.link()

    def use(self):
        gl.glUseProgram(self._id)

    def link(self):
        result = True
        if self._is_linked:
            return result
        # compile and attach all shaders
        self._attach_all_shaders()
        gl.glBindAttribLocation(self._id, 0, "aPos")
        gl.glBindAttribLocation(self._id, 1, "debugColor")
        gl.glLinkProgram(self._id)
        # free shader objects from memory (no longer needed once they have been
        # compiled and attached to the shader program)
        # check success of shader program linking
        success = gl.glGetProgramiv(self._id, gl.GL_LINK_STATUS)
        if not success:
            info_log = gl.glGetProgramInfoLog(self._id)
            print(info_log)
            result = False
        if result:
            for ID in self._shaders:
                self._shaders[ID].delete_shader()
        self._is_linked = result
        return result

    def attach_shader(self, shader):
        if shader.get_ID() not in self._shaders:
            self._shaders[shader.get_ID()] = shader
        # must compile shader before attaching to program
        if not shader.is_compiled():
            shader.compile()
        # attach shaders to the shader program
        gl.glAttachShader(self._id, shader.get_ID())

    def _attach_all_shaders(self):
        if self.all_shaders_compiled():
            return
        for ID in self._shaders:
            if not self._shaders[ID].is_compiled():
                self.attach_shader(self._shaders[ID])

    def get_ID(self):
        return self._id

    def is_linked(self):
        return self._is_linked

    def all_shaders_compiled(self):
        result = True
        if self._is_linked:
            return result
        for ID in self._shaders:
            if not self._shaders[ID].is_compiled():
                result = False
                break
        return result

    def delete_program(self):
        gl.glDeleteProgram(self._id)
