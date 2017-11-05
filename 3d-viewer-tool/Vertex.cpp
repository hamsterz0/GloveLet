//
// Created by joseph on 11/4/17.
//
#include "Polygon.h"

Vertex::Vertex(Vertex &v){
    pos = glm::fvec3(v.pos);
    next_vertex = v.next_vertex;
}
/*!
 * Constructs \c Vertex object with \c position as the position vector.
 * @param position the position vector
 */
Vertex::Vertex(glm::fvec3 &position) {
    pos = position;
}
/*!
 * Get position vector.
 * @return \code{.unparsed}
 * const fvec3
 * \endcode
 */
glm::fvec3 Vertex::getPos() {
    return pos;
}
/*!
 * Get next vertex in linked list.
 * @return \c Vertex
 */
Vertex* Vertex::getNextVertex() {
    return next_vertex;
}
/*!
 * Set vector position.
 * @param position the position vector
 */
void Vertex::setPos(glm::fvec3 &position) {
    pos = position;
}
/*!
 * Set next vertex in linked list.
 * \attention The next vertex should always be next counter-clockwise vertex when constructing a polygon.
 * <br><br> New vertices will be inserted into the linked list.
 * @param next
 */
void Vertex::setNextVertex(Vertex &next) {
    next_vertex = &next;
}
/*!
 * Compares reference addresses.
 * @param v1 first vertex
 * @param v2 second vertex
 * @return \c bool
 */
bool Vertex::operator==(const Vertex &v2) {
    return (this == &v2);
}
/*!
 * Inversely compares reference addresses.
 * @param v1 first vertex
 * @param v2 second vertex
 * @return \c bool
 */
bool Vertex::operator!=(const Vertex &v2) {
    return !(*this == v2);
}
/*!
 * \warning Empty constructor. DO NOT USE.
 */
Vertex::Vertex() {}
