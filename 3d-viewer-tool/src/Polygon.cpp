//
// Created by joseph on 11/4/17.
//
#include <GL/gl.h>
#include <iostream>
#include "Polygon.h"

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
 * @param start - starting vertex
 * @param color
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
 * @param n_vert number of \c Vertex objects
 * @param v \c Vertex object
 * @param ... any number of \c Vertex objects
 */
Polygon::Polygon(size_t n_vert, Vertex &v, ...) {
// TODO define
}
/*!
 * Draws the polygon.
 */
void Polygon::draw() {
    glBegin(GL_POLYGON);
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
/*!
 *
 * @return
 */
const Vertex Polygon::getStartVertex() {
    // TODO define
}
/*!
 *
 * @return
 */
const Vertex Polygon::getEndVertex() {
    // TODO define
}
/*!
 *
 * @param v
 */
void Polygon::setStartVertex(Vertex &v) {
    // TODO define
}
/*!
 *
 * @param v
 */
void Polygon::setEndVertex(Vertex &v) {
    // TODO define
}
/*!
 * Set the color of the polygon.
 * @param c - glm::fvec3 with elements representing (red, green, blue)
 */
void Polygon::setColor(glm::fvec3 &c) {
    color = c;
}