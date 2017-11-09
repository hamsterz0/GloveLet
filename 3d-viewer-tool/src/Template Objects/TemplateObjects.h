//
// Created by joseph on 11/9/17.
//

#ifndef GLM_GLM_H
#define GLM_GLM_H
#include <glm/glm.hpp>
#endif // GLM_GLM_H

#ifndef MESH_H
#include "../World Objects/Mesh.h"
#endif

#ifndef RECTANGULAR_PRISM_H
#define RECTANGULAR_PRISM_H

#include "../World Objects/WorldObject.h"

class RectangularPrism : WorldObject {
public:
    RectangularPrism(float length, float width, float height);
    RectangularPrism(float length, float width, float height, glm::fvec3 &position);
    RectangularPrism(float length, float width, float height, glm::fvec3 &position, glm::fquat &rotation);
};

class Cube : RectangularPrism {
public:
    Cube(float side);
    Cube(float side, glm::fvec3 &position);
    Cube(float side, glm::fvec3 &position, glm::fquat &rotation);
};

#endif //RectangularPrism_H
