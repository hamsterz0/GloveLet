//
// Created by joseph on 11/4/17.
//
#include <GL/gl.h>
#include "Mesh.h"

Polygon::~Polygon() {
    for(Vertex* v : vertices) {
        v->removePolygonReference(this);
        if(v->getPolyReferenceCount() == 0) delete v;
    }
}
/*!
 * Constructs \c Polygon with the vertices passed as arguments.
 * \attention
 * \c Vertex arguments must be passed in counter-clockwise order. Polygon rendering makes the
 * assumption that vertices are in counter-clockwise order. Doing otherwise will produce unexpected results.
 * @param vertices - \c std::vector`<Vertex*`> - the list of vertices the construct this polygon
 * @param color - \c glm::fvec3 - RGB color vector
 */
Polygon::Polygon(std::vector<Vertex*> vertices, glm::fvec3 color) {
    this->color = color;
    for(Vertex* v : vertices) addVertex(v);
    if(this->normal.length() == 0.0f) getNormal(); // dummy call to getNormal to update the normal vector for this polygon.
}
/*!
 * Constructs \c Polygon with the vertices passed as arguments.
 * \attention
 * \c Vertex arguments must be passed in counter-clockwise order. Polygon rendering makes the
 * assumption that vertices are in counter-clockwise order. Doing otherwise will produce unexpected results.
 * @param vertices - \c std::vector`<Vertex*`> - the list of vertices the construct this polygon
 */
Polygon::Polygon(std::vector<Vertex*> vertices)
        : Polygon(vertices, glm::fvec3(1.0f, 1.0f, 1.0f)) {}
/*!
 * Draws the polygon.
 * @param mode - \c RenderMode - *optional* sets the render mode.
 */
void Polygon::render(RenderMode mode) {
    glBegin(mode);
    glColor3f(color.x, color.y, color.z);
    for(Vertex* v : vertices) glVertex3f(v->getPos().x, v->getPos().y, v->getPos().z);
    glEnd();
}
/*!
 * Add a vertex to the polygon.
 * \attention
 * Vertices must be added in counter-clockwise order. Polygon rendering makes the
 * assumption that vertices are in counter-clockwise order. Doing otherwise will produce unexpected results.
 * @param v - \c Vertex*
 */
void Polygon::addVertex(Vertex* v) {
    if(vertices.size() < 3) updateNormal = true; // when getNormal is next called, the polygon's normal will be recomputed.
    vertices.push_back(v);
    vertices.back()->addPolygonReference(this);
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
// TODO doc
glm::fvec3 Polygon::getNormal() {
    if(updateNormal && vertices.size() > 2) {
        normal = computeNormal();
        updateNormal = false;
    }
    return normal;
}
// TODO doc
glm::fvec3 Polygon::computeNormal() {
    // Polygon must have at least 3 vertices to compute normal.
    if(vertices.size() < 3)
        return glm::fvec3(0.0f, 0.0f, 0.0f);

    glm::vec3 a, b;
    a = vertices[0]->getPos() - vertices[1]->getPos();
    b = vertices[0]->getPos() - vertices[2]->getPos();

    glm::fvec3 norm = glm::cross(a, b);

    return glm::normalize(norm);
}

void Polygon::operator<<(Vertex* vertex) {
    addVertex(vertex);
}
