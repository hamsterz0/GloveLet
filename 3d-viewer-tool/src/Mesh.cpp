//
// Created by joseph on 11/5/17.
//

#include "Mesh.h"

/*!
 * Constructs an empty mesh with no polygons and default render mode of \c polygon.
 */
Mesh::Mesh() {}
/*!
 * Default deconstructor.
 */
Mesh::~Mesh() {
    Polygon* next = last_polygon;
    while(next != nullptr) {
        next = next->getPrevPolygon();
        delete last_polygon;
        last_polygon = next;
    }

    first_polygon = nullptr;
    last_polygon = nullptr;
}
/*!
 * Constructs mesh and sets reference to first polygon,
 * with default render mode of \c polygon.
 */
Mesh::Mesh(Polygon *first_polygon) {
    this->first_polygon = first_polygon;
    this->last_polygon = first_polygon;
}
/*!
 * Renders mesh using current render mode.
 */
void Mesh::render() {
    auto next_poly = first_polygon;
    while(next_poly != nullptr) {
        next_poly->draw(render_mode);
        next_poly = next_poly->getNextPolygon();
    }
}
/*!
 * Adds a polygon to the mesh.
 * @param poly - \c Polygon* - pointer reference to polygon
 */
void Mesh::addPolygon(Polygon *poly) {
    if(first_polygon == nullptr) {
        first_polygon = poly;
        last_polygon = poly;
        first_polygon->setNextPolygon(last_polygon);
        last_polygon->setPrevPolygon(first_polygon);
    } else if(first_polygon == last_polygon) {
        poly->setPrevPolygon(first_polygon);
        last_polygon = poly;
        first_polygon->setNextPolygon(poly);
    } else {
        last_polygon->setNextPolygon(poly);
        poly->setPrevPolygon(last_polygon);
        last_polygon = poly;
    }
}
/*!
 * Set vertex render mode.
 * @param mode - \c RenderMode - the vertex render mode
 */
void Mesh::setRenderMode(RenderMode mode) {
    render_mode = mode;
}
/*!
 * Constructs rectangular prism mesh.
 * @param length - \c float - side along x-axis
 * @param width - \c float - side along y-axis
 * @param depth - \c float - side along z-axis
 */
RectangularPrismMesh::RectangularPrismMesh(float length, float width, float depth) {
    Polygon* p;
    glm::fvec3 v;
    Vertex* v1;
    Vertex* v2;
    Vertex* v3;
    Vertex* v4;
    glm::fvec3 color;

    // FRONT
    v = glm::fvec3(-length,-width,-depth);
    v1 = new Vertex(v);
    v = glm::fvec3(length,-width,-depth);
    v2 = new Vertex(v);
    v = glm::fvec3(length,width,-depth);
    v3 = new Vertex(v);
    v = glm::fvec3(-length,width,-depth);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    color = glm::fvec3(1.0f, 1.0f, 1.0f);
    p->setColor(color);
    this->addPolygon(p);
    // BACK
    v = glm::fvec3(-length,-width,depth);
    v1 = new Vertex(v);
    v = glm::fvec3(-length,width,depth);
    v2 = new Vertex(v);
    v = glm::fvec3(length,width,depth);
    v3 = new Vertex(v);
    v = glm::fvec3(length,-width,depth);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    color = glm::fvec3(1.0f, 0.0f, 1.0f);
    p->setColor(color);
    this->addPolygon(p);
    // RIGHT
    v = glm::fvec3(length,-width,-depth);
    v1 = new Vertex(v);
    v = glm::fvec3(length,-width,depth);
    v2 = new Vertex(v);
    v = glm::fvec3(length,width,depth);
    v3 = new Vertex(v);
    v = glm::fvec3(length,width,-depth);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    color = glm::fvec3(1.0f, 0.0f, 0.0f);
    p->setColor(color);
    this->addPolygon(p);
    // LEFT
    v = glm::fvec3(-length,-width,-depth);
    v1 = new Vertex(v);
    v = glm::fvec3(-length,width,-depth);
    v2 = new Vertex(v);
    v = glm::fvec3(-length,width,depth);
    v3 = new Vertex(v);
    v = glm::fvec3(-length,-width,depth);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    color = glm::fvec3(0.0f, 0.0f, 1.0f);
    p->setColor(color);
    this->addPolygon(p);
    // TOP
    v = glm::fvec3(-length,width,-depth);
    v1 = new Vertex(v);
    v = glm::fvec3(-length,width,depth);
    v2 = new Vertex(v);
    v = glm::fvec3(length,width,depth);
    v3 = new Vertex(v);
    v = glm::fvec3(length,width,-depth);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    color = glm::fvec3(0.0f, 1.0f, 0.0f);
    p->setColor(color);
    this->addPolygon(p);
    // BOTTOM
    v = glm::fvec3(-length,-width,-depth);
    v1 = new Vertex(v);
    v = glm::fvec3(length,-width,-depth);
    v2 = new Vertex(v);
    v = glm::fvec3(length,-width,depth);
    v3 = new Vertex(v);
    v = glm::fvec3(-length,-width,depth);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    color = glm::fvec3(0.0f, 1.0f, 0.0f);
    p->setColor(color);
    this->addPolygon(p);
}


CubeMesh::CubeMesh(float side) : RectangularPrismMesh(side, side , side) {}
