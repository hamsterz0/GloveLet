//
// Created by joseph on 11/2/17.
//
#pragma once

#ifndef STD_STRING_H
#define STD_STRING_H
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

#ifndef AXIS_H
#include "Axis.h"
#endif // AXIS_H

#ifndef DEFAULT_AXIS_LEN
#define DEFAULT_AXIS_LEN 1.0f
#endif

#ifndef WORLDOBJECT_H
#define WORLDOBJECT_H

/*!
 * Provides generic, extensible 3-dimensional object class.
 */
class WorldObject {
protected:
    std::string name = "";
    bool doRenderAxis = false;
    float axis_length = 1.0f;
    Axis* axis = nullptr;
    RenderMode render_mode = polygon;
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
    Mesh* getMesh();
    void setMesh(Mesh &mesh);
    WorldObject* duplicate();
    void setRenderMode(RenderMode mode);
    void doAxisRender(bool b);
    void setAxisLength(float len);
};


#endif //WORLDOBJECT_H
