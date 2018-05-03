import OpenGL.GL as gl
import glm
import numpy as np
from ctypes import c_float

import glovelet.viewer3DToolPython.shadermanager as sm


def _convert2tvec3(arr3):
    if type(arr3) is glm.tvec3:
        return arr3
    elif type(arr3) is iter or type(arr3) is tuple or type(arr3) is np.ndarray:
        return glm.vec3((arr3[0], arr3[1], arr3[2]), dtype=c_float)


def _convert2tquat(rot):
    """
    Converts Python iterables and numpy arrays to the expected type.
    """
    if type(rot) is glm.tquat:
        return rot
    elif type(rot) is iter or type(rot) is tuple or type(rot) is glm.tvec3 or type(rot) is np.ndarray:
        if len(rot) == 3:
            return glm.tquat(glm.vec3(rot[0], rot[1], rot[2]), dtype=c_float)
        elif len(rot) == 4:
            return glm.tquat(rot[0], rot[1], rot[2], rot[3], dtype=c_float)
    else:
        return glm.tquat((0, 0, 0, 1), dtype=c_float)


class WorldObject:
    def __init__(self, mesh,
                 position=glm.vec3((0, 0, 0), dtype=c_float),
                 local_position=glm.vec3((0, 0, 0), dtype=c_float),
                 rotation=_convert2tquat((0, 0, 0)),
                 local_rotation=_convert2tquat((0, 0, 0)),
                 parent=None, children=[], axis=None, disable_depth=False):
        # TODO: type check for 'mesh', 'parent', 'children', and 'axis' kwargs
        self._axis = axis               # TODO: Implement axis object
        self._mesh = mesh
        self.position = _convert2tvec3(position)
        self.local_position = _convert2tvec3(local_position)
        self.rotation = _convert2tquat(rotation)
        self.local_rotation = _convert2tquat(local_rotation)
        self._parent = parent
        self._children = children.copy()
        self.disable_depth = disable_depth

    def render(self):
        trans_mat = glm.mat4(1.0, dtype=c_float)
        trans_mat = glm.translate(trans_mat, self.position)
        loc_trans_mat = glm.mat4(1.0, dtype=c_float)
        loc_trans_mat = glm.translate(loc_trans_mat, self.local_position)
        rot_mat = glm.mat4_cast(self.rotation)
        loc_rot_mat = glm.mat4_cast(self.local_rotation)
        # push transformations to stack
        sm.CURRENT_PROGRAM.push()
        # sm.CURRENT_PROGRAM.model_mat4(glm.mat4(1.0, dtype=c_float).value)
        sm.CURRENT_PROGRAM.model_mat4(trans_mat.value)
        sm.CURRENT_PROGRAM.model_mat4(rot_mat.value)
        sm.CURRENT_PROGRAM.model_mat4(loc_trans_mat.value)
        sm.CURRENT_PROGRAM.model_mat4(loc_rot_mat.value)
        # disable depth test if self.disable_depth is True
        gl.glEnable(gl.GL_DEPTH_TEST)
        # is_depth_enabled = gl.glIsEnabled(gl.GL_DEPTH_TEST)
        # if self.disable_depth and is_depth_enabled:
        #     gl.glDisable(gl.GL_DEPTH_TEST)
        # draw the mesh
        self._mesh.render()
        # re-enable depth test if depth test was enabled prior to disabling
        # if self.disable_depth and is_depth_enabled:
        #     gl.glEnable(gl.GL_DEPTH_TEST)
        # render children
        for i in range(len(self._children)):
            # pushing here separates the transformations of the children from the parent
            # sm.CURRENT_PROGRAM.push()
            self._children[i].render()
            # sm.CURRENT_PROGRAM.pop()
        # pop transformations from stack
        sm.CURRENT_PROGRAM.pop()

    def move(self, vec):
        """
        Move this object in its world space. This will be the local
        space of the parent if this object is a child of another object.
        """
        # TODO: Complete parameter documentation
        self.position += _convert2tvec3(vec)

    def move_local(self, vec):
        """
        Move this object in local space.
        """
        # TODO: Complete parameter documentation
        self.local_position += _convert2tvec3(vec)

    def set_position(self, vec):
        """
        Set this object's position in world space. This will be the local
        space of the parent if this object is a child of another object.
        """
        # TODO: Complete parameter documentation
        self.position = _convert2tvec3(vec)

    def set_local_position(self, vec):
        """
        Set this object's position in local space.
        """
        # TODO: Complete parameter documentation
        self.local_position = _convert2tvec3(vec)

    def rotate(self, rot):
        """
        Rotate the object by the specified amount in world space.
        This will be the local space of the parent if this object
        is a child of another object.
        """
        # TODO: Complete parameter documentation
        self.rotation = _convert2tquat(rot) * self.rotation

    def rotate_local(self, rot):
        """
        Rotate the object by the specified amount in local space.
        """
        # TODO: Complete parameter documentation
        self.local_rotation = self.local_rotation * _convert2tquat(rot)

    def set_rotation(self, rot):
        """
        Set this object's rotation in world space. This will be the local
        space of the parent if this object is a child of another object.
        """
        # TODO: Complete parameter documentation
        self.rotation = _convert2tquat(rot)

    def set_local_rotation(self, rot):
        """
        Set this object's rotation in local space.
        """
        # TODO: Complete parameter documentation
        self.local_rotation = _convert2tquat(rot)

    def add_child(self, child):
        """
        Adds the specified WorldObject to the children of this object.
        The 'set_parent' method of the child will be called.
        """
        if self is not child and child not in self._children:
            if child is not None and type(child) is WorldObject:
                self._children.append(child)
                child.set_parent(self)

    def detach_child(self, child):
        """
        Detaches the specified child from this object.
        The child's parent is set to None.

        :param child: a WorldObject
        """
        if type(child) is WorldObject and child in self._children:
            child.set_parent(None)
            self._children.remove(child)

    def set_parent(self, parent):
        """
        Sets the parent of this object. If this object already has
        a parent, the 'detach_child' of the parent method is called
        to detach this child.
        """
        if self._parent is not parent:
            if parent is None or type(parent) is WorldObject:
                if self._parent is not None:
                    self._parent.detach_child(self)
                self._parent = parent

    def set_render_mode(self, mode):
        """
        Set the OpenGL render mode of this object.
        :param mode:
        """
        self._mesh.set_render_mode(mode)

    def _count_childern(self):
        result = len(self._children)
        for i in range(len(self._children)):
            result += self._children[i].count_childern()
        return result


def draw_vector(pos1, pos2, length, color=(1.0, 1.0, 1.0, 1.0)):
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_DEPTH_TEST)
