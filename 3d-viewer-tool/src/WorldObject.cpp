//
// Created by joseph on 11/2/17.
//
#pragma once

#include <GL/gl.h>
#include "glm/gtc/type_ptr.hpp"
#include "WorldObject.h"

using namespace glm;

WorldObject::~WorldObject() {
    if(parent) {
        if(prev_sibling) {
            prev_sibling->next_sibling = next_sibling;
            next_sibling->prev_sibling = prev_sibling;
        } else if(next_sibling) {
            next_sibling->prev_sibling = nullptr;
        }
    }

    if(first_child) {
        WorldObject* next = first_child;
        while(next != nullptr) {
            next->parent = this->parent;
            next->next_sibling;
        }
    }
}
/*!
 * Constructs a \c WorldObject with no mesh at world origin and default rotation.
 */
WorldObject::WorldObject() {
    position = fvec3(0.0f, 0.0f, 0.0f);
    local_pos = fvec3(position);
    rot = fquat(1.0f, 0.0f, 0.0f, 0.0f);
    local_rot = fquat(rot);
    mesh = nullptr;
}
/*!
 * Constructs a \c WorldObject with no mesh at \p position with default rotation.
 * @param position - the world position coordinate vector
 */
WorldObject::WorldObject(Mesh *mesh, glm::fvec3 &position) : WorldObject() {
    this->position = fvec3(position);
    local_pos = fvec3(0.0f, 0.0f, 0.0f);
    this->mesh = mesh;
}
/*!
 * Construct a \c WorldObject with no mesh at \p position and rotation defined by \p quaternion.
 * @param position - the world position coordinate vector
 * @param quaternion - the rotation of the object expressed in euler angles
 */
WorldObject::WorldObject(Mesh *mesh, glm::fvec3 &position, glm::fquat &quaternion)
        : WorldObject(mesh, position)
{
    rot = fquat(quaternion);
    local_rot = fquat(rot);
}
/*!
 * Construct a \c WorldObject with no mesh at \p position and rotation defined by \p euler_angles.
 * @param position - the world position coordinate vector
 * @param euler_angles - the rotation of the object expressed in euler angles
 */
WorldObject::WorldObject(Mesh *mesh, glm::fvec3 &position, glm::fvec3 &euler_angles)
        : WorldObject(mesh, position)
{
    rot = glm::fquat(euler_angles);
}
/*!
 * Render this object.
 */
void WorldObject::render() {
    mat4 rot_mat = mat4_cast(rot);
    mat4 local_rot_mat = mat4_cast(local_rot);
    auto next = first_child;
    glTranslatef(position.x, position.y, position.z);
    glMultMatrixf(glm::value_ptr(rot_mat));
    glTranslatef(local_pos.x, local_pos.y, local_pos.z);
    glMultMatrixf(glm::value_ptr(local_rot_mat));
    mesh->render();
    while( next != nullptr ) {
        glPushMatrix(); // separates rendering for each child.
        next->render();
        glPopMatrix();
        next = next->next_sibling;
    }
}
/*!
 * Moves the \c WorldObject by the amount in \p ds.
 * @param ds - the delta-position vector
 */
void WorldObject::move(glm::fvec3 &ds) {
    position += ds;
}
/*!
 * Rotates the object by the specified amount.
 * \attention Rotations are global by default. Local rotations will be made before
 * any translations, and will be relative to this \c WorldObject's local axis frame.
 * @param euler_angles - the euler angle rotation
 * @param doLocalRotation - *optional* performs rotation locally instead of globally
 */
void WorldObject::rotate(glm::fvec3 &euler_angles, bool doLocalRotation) {
    fquat new_rot = fquat(euler_angles);
    rotate(new_rot, doLocalRotation);
}
/*!
 * Rotates the object by the specified amount.
 * \attention Rotations are global by default. Local rotations will be made before
 * any translations, and will be relative to this \c WorldObject's local axis frame.
 * @param euler_angles - the quaternion rotation
 * @param doLocalRotation - *optional* performs rotation locally instead of globally
 */
void WorldObject::rotate(glm::fquat &quaternion, bool doLocalRotation) {
    if(doLocalRotation)
        local_rot = local_rot * quaternion;
    else
        rot = quaternion * rot;
}
/*!
 * Detaches the specified child from this object.
 * \attention Detaching a child does not affect the child's world position.
 * @param child - the child to detach
 */
void WorldObject::detachChild(WorldObject &child) {
    WorldObject* next = first_child;
    while(next != nullptr) {
        if(next == &child) {
            next->prev_sibling = next->next_sibling;
            next->prev_sibling = nullptr;
            next->next_sibling = nullptr;
            next->parent = nullptr;
            return;
        }
    }
}
/*!
 * Adds \p child as a child of this \c WorldObject.
 * @param child
 */
void WorldObject::addChild(WorldObject &child) {
    if(!(&child)) return;
    if(first_child == nullptr) {
        first_child = &child;
        last_child = &child;
    } else if(first_child == last_child) {
        last_child = &child;
        first_child->next_sibling = last_child;
        last_child->prev_sibling = first_child;
    } else {
        last_child->next_sibling = &child;  // set the current last_child->next_sibling to point to the new child
        child.prev_sibling = last_child;    // set child's previous sibling to point to the current last_child
        last_child = &child;                // set the new last_child to point to child
    }
    child.parent = this;
}
/*!
 * Attaches this \c WorldObject to the specified parent.
 * @param parent - \c WorldObject - the parent \c WorldObject
 */
void WorldObject::setParent(WorldObject &parent) {
    parent.addChild(*this);
}
/*!
 * Get position vector.
 * @return \code glm::fvec3 \endcode
 * <br>
 * Returns the relative global position vector of this \c WorldObject. If this \c WorldObject
 * is a child of another, the position returned will be relative to the axis
 * frame of the parent.
 */
glm::fvec3 WorldObject::getPosition() {
    return position;
}
/*!
 * Set position vector.
 * \attention Sets the relative global position vector of this \c WorldObject. If this \c WorldObject
 * is a child of another, the position will be relative to the axis
 * frame of the parent.
 * @param pos - \c glm::fvec3 - the position vector.
 */
void WorldObject::setPosition(glm::fvec3 &pos) {
    position = fvec3(pos);
}
/*!
 * Get local position vector.
 * @return \code glm::fvec3 \endcode
 * <br>
 * Returns the local position vector of this \c WorldObject.
 */
glm::fvec3 WorldObject::getLocalPosition() {
    return local_pos;
}
/*!
 * Set local position vector.
 * \attention Sets the local position vector of this \c WorldObject.
 * The position will be relative to the axis frame of this \c WorldObject.
 * @param pos - \c glm::fvec3 - the position vector.
 */
void WorldObject::setLocalPosition(glm::fvec3 &pos) {
    local_pos = fvec3(pos);
}
/*!
 * Get rotation.
 * @return \code glm::fquat \endcode
 * <br>
 * Returns the relative global rotation quaternion of this \c WorldObject.
 * If this \c WorldObject is a child of another, the quaternion returned will be
 * relative to the axis frame of the parent.
 */
glm::fquat WorldObject::getRotation() {
    return rot;
}
/*!
 * Set rotation.
 * \attention Sets the relative global rotation quaternion of this \c WorldObject.
 * If this \c WorldObject is a child of another, the rotation will be relative to
 * the axis frame of the parent.
 * @param rot - \c glm::fquat - the quaternion rotation
 */
void WorldObject::setRotation(glm::fquat &rot) {
    this->rot = fquat(rot);
}
/*!
 * Get rotation.
 * @return \code glm::fquat \endcode
 * <br>
 * Returns the local rotation quaternion of this \c WorldObject.
 * The quaternion returned will be relative to the axis of this \c WorldObject.
 */
glm::fquat WorldObject::getLocalRotation() {
    return local_rot;
}
/*!
 * Set local rotation.
 * \attention Sets the local rotation quaternion of this \c WorldObject.
 * The rotation will be relative to the axis frame of this \c WorldObject.
 * @param rot - \c glm::fquat - the quaternion rotation.
 */
void WorldObject::setLocalRotation(glm::fquat &rot) {
    local_rot = fquat(rot);
}
/*!
 * Get reference to previous sibling.
 * @return \code WorldObject* \endcode
 * Will be \c nullptr if this \c WorldObject doesn't have a parent, or is the
 * first child.
 */
WorldObject WorldObject::getPrevSibling() {
    if(parent == nullptr) return *parent;
    return *prev_sibling;
}
/*!
 * Get reference to next sibling.
 * @return \code WorldObject* \endcode
 * Will be \c nullptr if this \c WorldObject doesn't have a parent, or is the
 * last child.
 */
WorldObject WorldObject::getNextSibling() {
    if(parent == nullptr) return *parent;
    return *next_sibling;
}
/*!
 * Get reference to mesh.
 * @return \code Polygon** \endcode
 */
Mesh WorldObject::getMesh() {
    return *mesh;
}
/*!
 * Set reference of mesh
 * @param mesh
 */
void WorldObject::setMesh(Mesh &mesh) {
    this->mesh = &mesh;
}
/*!
 * Duplicates this \c WorldObject sharing the mesh.
 * @return \code WorldObject \endcode
 */
WorldObject * WorldObject::duplicate() {
    WorldObject *copy = new WorldObject(mesh, position, rot);
    return copy;
}
