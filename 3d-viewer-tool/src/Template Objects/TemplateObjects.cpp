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
/*!
 * Constructs a \c WorldObject that is a simple 3-dimensional line.
 * @param point1 - \c glm::fvec3
 * @param point2 - \c glm::fvec3
 * @param color - \c glm::fvec3 - RGB color vector
 */
Line::Line(glm::fvec3 point1, glm::fvec3 point2, glm::fvec3 color) {
    this->point1 = new Vertex(point1);
    this->point2 = new Vertex(point2);
    std::vector<Vertex*> vertices;
    vertices.push_back(this->point1);
    vertices.push_back(this->point2);
    Polygon* p = new Polygon(vertices);
    p->setColor(color);
    this->mesh = new Mesh(p);
    render_mode = lines;
}
/*!
 * Constructs a \c WorldObject that is a simple 3-dimensional line.
 * @param point1 - \c glm::fvec3
 * @param point2 - \c glm::fvec3
 */
Line::Line(glm::fvec3 point1, glm::fvec3 point2)
        : Line(point1, point2, glm::fvec3(1.0f, 1.0f, 1.0f)) {}
/*!
 * Get first point of line.
 * @return \code glm::fvec3 \endcode
 */
glm::fvec3 Line::getPoint1() {
    return point1->getPos();
}
/*!
 * Set first point of line.
 * @param point - \c glm::fvec3
 */
void Line::setPoint1(glm::fvec3 point) {
    this->point1->setPos(point);
}
/*!
 * Get second point of line.
 * @return \code glm::fvec3 \endcode
 */
glm::fvec3 Line::getPoint2() {
    return point2->getPos();
}
/*!
 * Set second point of line.
 * @param point - \c glm::fvec3
 */
void Line::setPoint2(glm::fvec3 point) {
    this->point2->setPos(point);
}
