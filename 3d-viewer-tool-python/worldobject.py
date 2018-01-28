import OpenGL.GL as gl
import glm
import numpy as np
from ctypes import c_float

import mesh
import shadermanager as sm


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
    elif type(rot) is iter or type(rot) is iter or type(rot) is glm.tvec3 or type(rot) is np.ndarray:
        if len(rot) == 3:
            return glm.tquat(glm.vec3((rot[0], rot[1], rot[2])), dtype=c_float)
        elif len(rot) == 4:
            return glm.tquat(glm.vec3((rot[0], rot[1], rot[2], rot[3])), dtype=c_float)
    else:
        return glm.tquat((0, 0, 0, 1), dtype=c_float)


class WorldObject:
    _mesh = None
    _do_axis_render = False     # TODO: Implement axis object
    _axis = None                # TODO: Implement axis object
    _axis_length = 1.0          # TODO: Implement axis object
    _pos = None
    _loc_pos = None
    _rot = None
    _loc_rot = None
    _parent = None
    _children = list()

    def __init__(self, mesh_,
                 position=glm.vec3((0, 0, 0), dtype=c_float),
                 local_position=glm.vec3((0, 0, 0), dtype=c_float),
                 rotation=glm.tquat((0, 0, 0, 1), dtype=c_float),
                 local_rotation=glm.tquat((0, 0, 0, 1), dtype=c_float),
                 parent=None, children=list()):
        self._mesh = mesh_
        self._pos = position
        self._loc_pos = local_position
        self._rot = rotation
        self._loc_rot = local_rotation
        self._parent = parent
        self._children = children

    def render(self):
        trans_mat = glm.translate(glm.mat4(1.0, dtype=c_float), self._pos)
        loc_trans_mat = glm.translate(
            glm.mat4(1.0, dtype=c_float), self._loc_pos)
        rot_mat = glm.mat4_cast(self._rot)
        loc_rot_mat = glm.mat4_cast(self._loc_rot)
        # push transformations to stack
        sm.CURRENT_PROGRAM.push()
        sm.CURRENT_PROGRAM.model_mat4(trans_mat.value)
        sm.CURRENT_PROGRAM.model_mat4(rot_mat.value)
        sm.CURRENT_PROGRAM.model_mat4(loc_trans_mat.value)
        sm.CURRENT_PROGRAM.model_mat4(loc_rot_mat.value)
        # draw the mesh
        self._mesh.render()
        # render children
        for i in range(len(self._children)):
            # pushing here separates the transformations of the children from the parent
            sm.CURRENT_PROGRAM.push()
            self._children[i].render()
            sm.CURRENT_PROGRAM.pop()
        # pop transformations from stack
        sm.CURRENT_PROGRAM.pop()

    def move(self, vec):
        """
        Move this object in its world space. This will be the local
        space of the parent if this object is a child of another object.
        """
        # TODO: Complete parameter documentation
        self._pos += _convert2tvec3(vec)

    def move_local(self, vec):
        """
        Move this object in local space.
        """
        # TODO: Complete parameter documentation
        self._loc_pos += _convert2tvec3(vec)

    def set_position(self, vec):
        """
        Set this object's position in world space. This will be the local
        space of the parent if this object is a child of another object.
        """
        # TODO: Complete parameter documentation
        self._pos = _convert2tvec3(vec)

    def set_local_position(self, vec):
        """
        Set this object's position in local space.
        """
        # TODO: Complete parameter documentation
        self._loc_pos = _convert2tvec3(vec)

    def rotate(self, rot):
        """
        Rotate the object by the specified amount in world space.
        This will be the local space of the parent if this object
        is a child of another object.
        """
        # TODO: Complete parameter documentation
        self._rot = _convert2tquat(rot) * self._rot

    def rotate_local(self, rot):
        """
        Rotate the object by the specified amount in local space.
        """
        # TODO: Complete parameter documentation
        self._loc_rot = _convert2tquat(rot) * self._loc_rot

    def set_rotation(self, rot):
        """
        Set this object's rotation in world space. This will be the local
        space of the parent if this object is a child of another object.
        """
        # TODO: Complete parameter documentation
        self._rot = _convert2tquat(rot)

    def set_local_rotation(self, rot):
        """
        Set this object's rotation in local space.
        """
        # TODO: Complete parameter documentation
        self._loc_rot = _convert2tquat(rot)

    def add_child(self, child):
        """
        Adds the specified WorldObject to the children of this object.
        The 'set_parent' method of the child will be called.
        """
        if child not in self._children:
            if child is not None and type(child) is WorldObject:
                self._children.append(child)
                child.set_parent(child)

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
        if self._parent != parent:
            if parent is None or type(parent) is WorldObject:
                if self._parent is not None:
                    self._parent.detach_child(self)
                self._parent = parent

    def _count_childern(self):
        result = len(self._children)
        for i in range(len(self._children)):
            result += self._children[i].count_childern()
        return result
