//
// Created by joseph on 11/2/17.
//
#pragma once

#ifndef STRING_H
#define STRING_H
#include <string>
#endif // STRING_H

#ifndef GLM_GLM_H
#define GLM_GLM_H

#include <glm/glm.hpp>

#endif // GLM_GLM_H

#ifndef GLM_GTX_QUATERNION_H
#define GLM_GTX_QUATERNION_H

#include <glm/gtx/quaternion.hpp>

#endif // GLM_GTC_QUATERNION_H

#ifndef MESH_H
#include "Mesh.h"
#endif

#ifndef WORLDOBJECT_H
#define WORLDOBJECT_H

/*!
 * Provides generic, extensible 3-dimensional object class.
 */
class WorldObject {
protected:
    std::string name = "";
    glm::fvec3 position;
    glm::fvec3 local_pos;
    glm::fquat rot = glm::fquat(1.0f, 0.0f, 0.0f, 0.0f);
    glm::fquat local_rot = glm::fquat(1.0f, 0.0f, 0.0f, 0.0f);
    WorldObject* parent = nullptr;
    WorldObject* first_child = nullptr;
    WorldObject* last_child = nullptr;
    WorldObject* prev_sibling = nullptr;
    WorldObject* next_sibling = nullptr;
    Mesh* mesh = nullptr;
public:
    WorldObject();
    ~WorldObject();
    WorldObject(Mesh *mesh, glm::fvec3 &position);
    WorldObject(Mesh *mesh, glm::fvec3 &position, glm::fvec3 &euler_angles);
    WorldObject(Mesh *mesh, glm::fvec3 &position, glm::fquat &quaternion);
    virtual void render();
    void move(glm::fvec3 &dv);
    void rotate(glm::fvec3 &euler_angles, bool doLocalRotation = false);
    void rotate(glm::fquat &quaternion, bool doLocalRotation = false);
    void detachChild(WorldObject &child);
    void addChild(WorldObject &child);
    void setParent(WorldObject &parent);
    glm::fvec3 getPosition();
    void setPosition(glm::fvec3 &pos);
    glm::fvec3 getLocalPosition();
    void setLocalPosition(glm::fvec3 &pos);
    glm::fquat getRotation();
    void setRotation(glm::fquat &rot);
    glm::fquat getLocalRotation();
    void setLocalRotation(glm::fquat &rot);
    WorldObject getPrevSibling();
    WorldObject getNextSibling();
    Mesh getMesh();
    void setMesh(Mesh &mesh);
    WorldObject * duplicate();
};


#endif //WORLDOBJECT_H
