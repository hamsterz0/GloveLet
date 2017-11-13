//
// Created by joseph on 11/4/17.
//
#include "Mesh.h"

/*!
 * Constructs \c Vertex object with \c position as the position vector.
 * @param position - \c glm::fvec3 - the position vector
 */
Vertex::Vertex(glm::fvec3 position) {
    pos = position;
}
/*!
 * Renders the normal vector of the \c Vertex as a cyan line.
 */
void Vertex::renderNormal() {
    glPushMatrix();
    glBegin(lines);
    glColor3f(0.0f, 1.0f, 1.0f);
    glVertex3f(pos.x, pos.y, pos.z);
    glVertex3f(pos.x - 0.25f*normal.x, pos.y - 0.25f*normal.y, pos.z - 0.25f*normal.z);
    glEnd();
    glPopMatrix();
}
/*!
 * Get position vector.
 * @return \code{.unparsed}
 * glm::fvec3
 * \endcode
 */
glm::fvec3 Vertex::getPos() {
    return pos;
}
/*!
 * Set vector position.
 * @param position the position vector
 */
void Vertex::setPos(glm::fvec3 position) {
    pos = position;
}
/*!
 * Get vertex normal vector.
 * @return \code glm::fvec3 \endcode
 */
glm::fvec3 Vertex::getNormal() {
    return normal;
}
/*!
 * \warning Empty constructor. DO NOT USE.
 */
Vertex::Vertex() {}
/*!
 * Adds \c Polygon pointer to this vertex's list of polygons.
 * @param poly - \c Polygon*
 */
void Vertex::addPolygonReference(Polygon *poly) {
    polygons.push_back(poly);
}
/*!
 * Removes the \c Polygon pointer to this vertex's list of polygons.
 * \attention This operation is slow, as it has to construct a new list without the specified \c Polygon
 * reference. This is only meant as a utility for when a polygon is being deconstructed.
 * @param poly - \c Polygon*
 */
void Vertex::removePolygonReference(Polygon *poly) {
    auto new_polygons = std::vector<Polygon*>();
    for(Polygon* p : polygons) {
        if(p != poly) new_polygons.push_back(p);
    }
    polygons = new_polygons;
}
// TODO doc
size_t Vertex::getPolyReferenceCount() {
    return polygons.size();
}
/*!
 * Update the normal of this vertex.
 */
void Vertex::updateNormal() {
    normal = glm::fvec3(0.0f, 0.0f, 0.0f);
    for(auto p : polygons) normal += p->getNormal();
    normal = glm::normalize(normal);
}
/*!
 * Compares reference addresses.
 * @param v2 - \c Vertex
 * @return \c bool
 */
bool Vertex::operator==(const Vertex &v2) {
    return (this == &v2);
}
/*!
 * Inversely compares reference addresses.
 * @param v2 - \c Vertex
 * @return \c bool
 */
bool Vertex::operator!=(const Vertex &v2) {
    return !(*this == v2);
}
