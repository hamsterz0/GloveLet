//
// Created by joseph on 11/9/17.
//

#include "Axis.h"

/*!
 * Construct \c Axis object. Displays an X, Y, & Z axis.
 * \attention
 * X => red<br>
 * Y => green<br>
 * Z => blue
 * @param axis_length - \c float - the length of the axis lines
 */
Axis::Axis(float axis_length) {
    length = axis_length;
    auto origin = glm::fvec3(0.0f, 0.0f, 0.0f);
    auto x = glm::fvec3(length, 0.0f, 0.0f);
    auto y = glm::fvec3(0.0f, length, 0.0f);
    auto z = glm::fvec3(0.0f, 0.0f, length);
    glm::fvec3 color;
    // create vertices
    Vertex* v1 = new Vertex(origin);
    x_axis = new Vertex(x);
    Vertex* v3 = new Vertex(origin);
    y_axis = new Vertex(y);
    Vertex* v5 = new Vertex(origin);
    z_axis = new Vertex(z);
    // create polygons
    Polygon* poly_x = new Polygon(*v1);
    poly_x->addVertex(*x_axis);
    color = glm::normalize(x);
    poly_x->setColor(color);
    Polygon* poly_y = new Polygon(*v3);
    poly_y->addVertex(*y_axis);
    color = glm::normalize(y);
    poly_y->setColor(color);
    Polygon* poly_z = new Polygon(*v5);
    poly_z->addVertex(*z_axis);
    color = glm::normalize(z);
    poly_z->setColor(color);
    // add polygons to mesh
    addPolygon(poly_x);
    addPolygon(poly_y);
    addPolygon(poly_z);
}
/*!
 * Construct \c Axis object. Displays an X, Y, & Z axis with axis line lengths of \c 1.0f.
 * \attention
 * X => red<br>
 * Y => green<br>
 * Z => blue
 */
Axis::Axis() : Axis(1.0f) {}
/*!
 * Set axis line length.
 * @param axis_length - \c float
 */
void Axis::setAxisLength(float axis_length) {
    length = axis_length;
    auto x = glm::fvec3(length, 0.0f, 0.0f);
    auto y = glm::fvec3(0.0f, length, 0.0f);
    auto z = glm::fvec3(0.0f, 0.0f, length);
    x_axis->setPos(x);
    y_axis->setPos(y);
    z_axis->setPos(z);
}
