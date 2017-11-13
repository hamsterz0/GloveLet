//
// Created by joseph on 11/4/17.
//
#include <GL/gl.h>
#include <glm/gtc/quaternion.hpp>
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
 * @param showNormal - \c bool - *optional* displays polygon normal vector when \c true
 */
void Polygon::render(RenderMode mode, bool showNormal) {
    glBegin(mode);
    glColor3f(color.x, color.y, color.z);
    for(Vertex* v : vertices) {
        glVertex3f(v->getPos().x, v->getPos().y, v->getPos().z);
    }
    glEnd();
    if(showNormal) {
        glBegin(lines);
        glColor3f(1.0f, 1.0f, 0.0f);
        glVertex3f(centroid.x, centroid.y, centroid.z);
        glVertex3f(centroid.x - 0.5f*normal.x, centroid.y - 0.5f*normal.y, centroid.z - 0.5f*normal.z);
        glEnd();
    }
}
/*!
 * Add a vertex to the polygon.
 * \attention
 * Vertices must be added in counter-clockwise order. Polygon rendering makes the
 * assumption that vertices are in counter-clockwise order. Doing otherwise will produce unexpected results.
 * @param v - \c Vertex*
 */
void Polygon::addVertex(Vertex* v) {
    vertices.push_back(v);
    computeNormal();
    computeCentroid();
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
    return normal;
}
// TODO doc
void Polygon::computeNormal() {
    // Polygon must have at least 3 vertices to compute normal.
    if(vertices.size() < 3)
        return;

    glm::fvec3 a, b;
    a = vertices[0]->getPos() - vertices[1]->getPos();
    b = vertices[0]->getPos() - vertices[2]->getPos();

    glm::fvec3 norm = glm::cross(a, b);

    normal = glm::normalize(norm);
}
/*!
 * Computes the centroid of the polygon.
 * \attention
 * Algorithm derived based barycenter of the boundary. Referenced the link below:<br><br>
 * https://stackoverflow.com/questions/18305712/how-to-compute-the-center-of-a-polygon-in-2d-and-3d-space
 */
void Polygon::computeCentroid() {
    float sx = 0.0f, sy = 0.0f, sz = 0.0f, sL = 0.0f;
    size_t N = vertices.size();
    for(size_t i = 0; i < N; i++) {
        auto v1 = vertices[N - 1 - i];
        auto v2 = vertices[i];
        auto L = glm::pow(v1->getPos().x - v2->getPos().x, 2) +
                glm::pow(v1->getPos().y - v2->getPos().y, 2) +
                glm::pow(v1->getPos().z - v2->getPos().z, 2);
        L = glm::sqrt(L);
        sx += (v1->getPos().x + v2->getPos().x)/2.0f * L;
        sy += (v1->getPos().y + v2->getPos().y)/2.0f * L;
        sz += (v1->getPos().z + v2->getPos().z)/2.0f * L;
        sL += L;
    }
    centroid.x = sx / sL;
    centroid.y = sy / sL;
    centroid.z = sz / sL;
}
// TODO doc
void Polygon::operator<<(Vertex* vertex) {
    addVertex(vertex);
}
