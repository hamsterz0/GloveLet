//
// Created by joseph on 11/2/17.
//

#ifndef GLM_GLM_H
#define GLM_GLM_H

#include <glm/glm.hpp>

#endif // GLM_GLM_H

#ifndef GLM_GTC_QUATERNION_H
#define GLM_GTC_QUATERNION_H

#include <glm/gtc/quaternion.hpp>
#include "Polygon.h"

#endif // GLM_GLM_H

#ifndef WORLDOBJECT_H
#define WORLDOBJECT_H

class WorldObject {
protected:
    glm::fvec3 world_pos;
    glm::fvec3 local_pos;
    glm::fquat world_quat;
    glm::fquat local_quat;
    WorldObject* parent = nullptr;
    WorldObject* first_child = nullptr;
    WorldObject* last_child = nullptr;
    WorldObject* prev_sibling = nullptr;
    WorldObject* next_sibling = nullptr;
    Polygon** polygons;
public:
    WorldObject();
    ~WorldObject();
    WorldObject(glm::fvec3 position, glm::fvec3 rotation_euler);
    WorldObject(glm::fvec3 position, glm::fquat rotation_quaternion);
    void move(float dx, float dy, float dz);
    virtual void draw()=0;
    void detachChild(WorldObject &child);
    void addChild(WorldObject &child);
    void setParent(WorldObject &parent);
    void updateQuaternion(glm::fvec3 &euler_angles);
    glm::fvec3 getWorldPosition();
    void setWorldPosition(glm::fvec3 &pos);
    glm::fvec3 getLocalPosition();
    void setLocalPosition(glm::fvec3 &pos);
    glm::fquat getWorldRotation();
    void setWorldRotation(glm::fquat &rot);
    glm::fquat getLocalRotation();
    void setLocalRotation(glm::fquat &rot);
    WorldObject getPrevSibling();
    void setPrevSibling(WorldObject &wo);
    WorldObject getNextSibling();
    void setNextSibling(WorldObject &wo);
};


#endif //WORLDOBJECT_H
