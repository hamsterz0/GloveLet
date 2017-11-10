//
// Created by joseph on 11/9/17.
//

#include "TemplateObjects.h"
/*!
 * Constructs a \c WorldObject with a rectangular prism mesh.
 * @param length - \c float
 * @param width - \c float
 * @param height - \c float
 */
RectangularPrism::RectangularPrism(float length, float width, float height)
        : WorldObject()
{
    mesh = new RectangularPrismMesh(length, width, height);
}
/*!
 * Constructs a \c WorldObject with a rectangular prism mesh.
 * @param length - \c float
 * @param width - \c float
 * @param height - \c float
 * @param position - \c glm::fvec3 - the position vector
 */
RectangularPrism::RectangularPrism(float length,
                                   float width,
                                   float height,
                                   glm::fvec3 &position)
        : WorldObject(new RectangularPrismMesh(length, width, height), position) {}
/*!
 * Constructs a \c WorldObject with a rectangular prism mesh.
 * @param length - \c float
 * @param width - \c float
 * @param height - \c float
 * @param position - \c glm::fvec3 - the position vector
 * @param rotation - \c glm::fvec3 - the quaternion rotation
 */
RectangularPrism::RectangularPrism(float length,
                                   float width,
                                   float height,
                                   glm::fvec3 &position,
                                   glm::fquat &rotation)
        : WorldObject(new RectangularPrismMesh(length, width, height), position, rotation) {}
/*!
 * Constructs a \c WorldObject with a cube mesh.
 * @param side - \c float
 */
Cube::Cube(float side) : RectangularPrism(side, side, side) {}
/*!
 * Constructs a \c WorldObject with a rectangular prism mesh.
 * @param size - \c float
 * @param position - \c glm::fvec3 - the position vector
 */
Cube::Cube(float side, glm::fvec3 &position) : RectangularPrism(side, side, side, position) {}
/*!
 * Constructs a \c WorldObject with a rectangular prism mesh.
 * @param size - \c float
 * @param position - \c glm::fvec3 - the position vector
 * @param rotation - \c glm::fvec3 - the quaternion rotation
 */
Cube::Cube(float side, glm::fvec3 &position, glm::fquat &rotation)
        : RectangularPrism(side, side, side, position, rotation) {}