//
// Created by joseph on 11/9/17.
//
#pragma once

#ifndef GLM_GLM_H
#define GLM_GLM_H
#include <glm/glm.hpp>
#endif // GLM_GLM_H

#ifndef MESH_H
#include "../World Objects/Mesh.h"
#endif //MESH_H

#ifndef WORLDOBJECT_H
#include "../World Objects/WorldObject.h"
#endif //WORLDOBJECT_H

#ifndef TEMPLATE_OBJECTS_H
#define TEMPLATE_OBJECTS_H

class RectangularPrism : public WorldObject {
public:
    RectangularPrism(float length, float width, float height);
    RectangularPrism(float length, float width, float height, glm::fvec3 &position);
    RectangularPrism(float length, float width, float height, glm::fvec3 &position, glm::fquat &rotation);
};

class Cube : public RectangularPrism {
public:
    Cube(float side);
    Cube(float side, glm::fvec3 &position);
    Cube(float side, glm::fvec3 &position, glm::fquat &rotation);
};

class Line : public WorldObject {
private:
    Vertex* point1 = nullptr;
    Vertex* point2 = nullptr;
public:
    Line(glm::fvec3 point1, glm::fvec3 point2);
    Line(glm::fvec3 point1, glm::fvec3 point2, glm::fvec3 color);
    glm::fvec3 getPoint1();
    void setPoint1(glm::fvec3 point);
    glm::fvec3 getPoint2();
    void setPoint2(glm::fvec3 point);
};
#endif //TEMPLATE_OBJECTS_H
