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
    std::vector<Vertex*> vertices;
    // build vertices and polygons
    Vertex* vertex = new Vertex(origin);
    vertices.push_back(vertex);

    x_axis = new Vertex(x);
    vertices.push_back(x_axis);
    Polygon* poly_x = new Polygon(vertices);
    color = glm::normalize(x);
    poly_x->setColor(color);
    vertices.pop_back();

    y_axis = new Vertex(y);
    vertices.push_back(y_axis);
    Polygon* poly_y = new Polygon(vertices);
    color = glm::normalize(y);
    poly_y->setColor(color);
    vertices.pop_back();

    z_axis = new Vertex(z);
    vertices.push_back(z_axis);
    Polygon* poly_z = new Polygon(vertices);
    color = glm::normalize(z);
    poly_z->setColor(z);
    vertices.pop_back();

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
/*!
 * Renders mesh using current render mode.
 */
void Axis::render(RenderMode render_mode) {
    bool isLightEnabled = glIsEnabled(GL_LIGHTING);
    if(isLightEnabled) glDisable(GL_LIGHTING);
    auto next_poly = first_polygon;
    if(showVertNorms) for(auto v : vertices) v->renderNormal();
    while(next_poly != nullptr) {
        next_poly->render(render_mode, showPolyNorms);
        next_poly = next_poly->getNextPolygon();
    }
    if(isLightEnabled) glEnable(GL_LIGHTING);
}