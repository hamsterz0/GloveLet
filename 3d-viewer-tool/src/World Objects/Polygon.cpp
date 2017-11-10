//
// Created by joseph on 11/4/17.
//
#include <GL/gl.h>
#include "Mesh.h"

Polygon::~Polygon() {
    Vertex* prev = nullptr;
    Vertex* next = start_vertex->getNextVertex();
    while(next != end_vertex) {
        prev = next;
        next = next->getNextVertex();
        prev->~Vertex();
    }
    if(start_vertex != end_vertex) {
        start_vertex->~Vertex();
        end_vertex->~Vertex();
    } else {
        start_vertex->~Vertex();
    }
}
/*!
 * Construct \c Polygon with \p start as the starting vertex.
 * @param start - starting vertex
 */
Polygon::Polygon(Vertex &start) {
    start_vertex = &start;
    end_vertex = start_vertex;
    start_vertex->setNextVertex(*end_vertex);
    end_vertex->setNextVertex(*start_vertex);
    return;
}
/*!
 * Construct \c Polygon with \p start as the starting vertex and RGB color \p color
 * @param start - \c Vertex - starting vertex
 * @param color - \c glm::fvec3 - RGB color vector
 */
Polygon::Polygon(Vertex &start, glm::fvec3 &color) {
    start_vertex = &start;
    end_vertex = start_vertex;
    start_vertex->setNextVertex(*end_vertex);
    end_vertex->setNextVertex(*start_vertex);
    this->color = color;
}
/*!
 * Constructs \c Polygon with the vertices passed as arguments.
 * \attention
 * \c Vertex arguments must be passed in counter-clockwise order. Polygon rendering makes the
 * assumption that vertices are in counter-clockwise order. Doing otherwise will produce unexpected results.
 * @param color - \c glm::fvec3 - RGB color vector
 * @param n_vert - \c size_t - number of \c Vertex objects
 * @param v - \c Vertex - starting vertex
 * @param ... - \c Vertex - any number of \c Vertex objects
 */
Polygon::Polygon(glm::fvec3 &color, size_t n_vert, Vertex &v, ...) {
// TODO define
}
/*!
 * Draws the polygon.
 * @param mode - \c RenderMode - *optional* sets the render mode.
 */
void Polygon::draw(RenderMode mode) {
    glBegin(mode);
    glColor3f(color.x, color.y, color.z);
    Vertex* next = start_vertex;
    while(*next != *end_vertex) {
        glVertex3f(next->getPos().x, next->getPos().y, next->getPos().z);
        next = next->getNextVertex();
    }
    glVertex3f(end_vertex->getPos().x, end_vertex->getPos().y, end_vertex->getPos().z);
    glEnd();
}
/*!
 * Add a vertex to the polygon.
 * \attention
 * Vertices must be added in counter-clockwise order. Polygon rendering makes the
 * assumption that vertices are in counter-clockwise order. Doing otherwise will produce unexpected results.
 * @param v
 */
void Polygon::addVertex(Vertex &v) {
    if(start_vertex == end_vertex) {
        start_vertex->setNextVertex(v);
        end_vertex = &v;
    } else {
        end_vertex->setNextVertex(v);
        end_vertex = &v;
    }

    end_vertex->setNextVertex(*start_vertex);
}
// TODO doc
Vertex * Polygon::getStartVertex() {
    // TODO define
}
// TODO doc
Vertex * Polygon::getEndVertex() {
    // TODO define
}
/*!
 * Set the color of the polygon.
 * @param c - \c glm::fvec3 - with elements representing (red, green, blue)
 */
void Polygon::setColor(glm::fvec3 &c) {
    color = c;
}
/*!
 * Get pointer reference to next polygon in mesh.
 * \attention If this is the last polygon of the mesh, \c nullptr will be returned.
 * @return \code Polygon* \endcode
 */
Polygon *Polygon::getNextPolygon() {
    return next_polygon;
}
/*!
 * Get pointer reference to previous polygon in mesh.
 * \attention If this is the first polygon of the mesh, \c nullptr will be returned.
 * @return \code Polygon* \endcode
 */
Polygon *Polygon::getPrevPolygon() {
    return prev_polygon;
}
// TODO doc
void Polygon::setNextPolygon(Polygon *poly) {
    next_polygon = poly;
}
// TODO doc
void Polygon::setPrevPolygon(Polygon *poly) {
    prev_polygon = poly;
}