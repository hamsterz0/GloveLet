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
 * Constructs mesh from list of polygons
 * @param polygons - \c std::vector
 */
Mesh::Mesh(std::vector<Polygon *> polygons) {
    for(Polygon* p : polygons) {
        addPolygon(p);
    }
}
/*!
 * Constructs mesh and sets reference to first polygon.
 */
Mesh::Mesh(Polygon *first_polygon) {
    this->first_polygon = first_polygon;
    this->last_polygon = first_polygon;
}
/*!
 * Renders mesh using current render mode.
 */
void Mesh::render(RenderMode render_mode) {
    auto next_poly = first_polygon;
    if(showVertNorms) for(auto v : vertices) v->renderNormal();
    while(next_poly != nullptr) {
        next_poly->render(render_mode, showPolyNorms);
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

    for(Vertex* v : poly->vertices) {
        vertices.insert(v);
        v->updateNormal();
    }
}
/*!
 * When \c true, the normal vectors of the mesh's polygons will be rendered as yellow lines.
 * @param b - \c bool
 */
void Mesh::showPolygonNormals(bool b) {
    showPolyNorms = b;
}
/*!
 * When \c true, the normal vectors of the mesh's vertices will be rendered as cyan lines.
 * @param b - \c bool
 */
void Mesh::showVertexNormals(bool b) {
    showVertNorms = b;
}
/*!
 * Constructs rectangular prism mesh.
 * @param length - \c float - side along x-axis
 * @param width - \c float - side along y-axis
 * @param depth - \c float - side along z-axis
 */
RectangularPrismMesh::RectangularPrismMesh(float length, float width, float depth) {
    Polygon* p;
    Vertex *v1, *v2, *v3, *v4, *v5, *v6, *v7, *v8;
    std::vector<Vertex*> vertices;
    glm::fvec3 color;
    // instantiate
    v1 = new Vertex(glm::fvec3(-length, -width, -depth) * 0.5f);
    v2 = new Vertex(glm::fvec3(length, -width, -depth) * 0.5f);
    v3 = new Vertex(glm::fvec3(length, width, -depth) * 0.5f);
    v4 = new Vertex(glm::fvec3(-length, width, -depth) * 0.5f);
    v5 = new Vertex(glm::fvec3(-length, -width, depth) * 0.5f);
    v6 = new Vertex(glm::fvec3(-length, width, depth) * 0.5f);
    v7 = new Vertex(glm::fvec3(length, width, depth) * 0.5f);
    v8 = new Vertex(glm::fvec3(length, -width, depth) * 0.5f);

    // FRONT
    vertices.push_back(v1);
    vertices.push_back(v2);
    vertices.push_back(v3);
    vertices.push_back(v4);
    p = new Polygon(vertices);
    vertices.clear();
    color = glm::fvec3(1.0f, 1.0f, 1.0f);
    p->setColor(color);
    this->addPolygon(p);
    // BACK
    vertices.push_back(v5);
    vertices.push_back(v6);
    vertices.push_back(v7);
    vertices.push_back(v8);

    p = new Polygon(vertices);
    vertices.clear();
    color = glm::fvec3(1.0f, 0.0f, 1.0f);
    p->setColor(color);
    this->addPolygon(p);
    // RIGHT
    vertices.push_back(v2);
    vertices.push_back(v8);
    vertices.push_back(v7);
    vertices.push_back(v3);

    p = new Polygon(vertices);
    vertices.clear();
    color = glm::fvec3(1.0f, 0.0f, 0.0f);
    p->setColor(color);
    this->addPolygon(p);
    // LEFT
    vertices.push_back(v1);
    vertices.push_back(v4);
    vertices.push_back(v6);
    vertices.push_back(v5);


    p = new Polygon(vertices);
    vertices.clear();
    color = glm::fvec3(0.0f, 0.0f, 1.0f);
    p->setColor(color);
    this->addPolygon(p);
    // TOP
    vertices.push_back(v4);
    vertices.push_back(v3);
    vertices.push_back(v7);
    vertices.push_back(v6);

    p = new Polygon(vertices);
    vertices.clear();
    color = glm::fvec3(0.0f, 1.0f, 0.0f);
    p->setColor(color);
    this->addPolygon(p);
    // BOTTOM
    vertices.push_back(v2);
    vertices.push_back(v1);
    vertices.push_back(v5);
    vertices.push_back(v8);

    p = new Polygon(vertices);
    vertices.clear();
    color = glm::fvec3(0.0f, 1.0f, 0.0f);
    p->setColor(color);
    this->addPolygon(p);
}

CubeMesh::CubeMesh(float side) : RectangularPrismMesh(side, side , side) {}
