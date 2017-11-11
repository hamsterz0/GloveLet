//
// Created by joseph on 11/5/17.
//

#ifndef GL_GL_H
#define GL_GL_H
#include <GL/gl.h>
#endif // GL_GL_H

#ifndef STDARG_H
#define STDARG_H
#include <stdarg.h>
#endif // STDARG_H

#ifndef CSTDDEF_H
#define CSTDDEF_H
#include <cstddef>
#endif // CSTDDEF_H

#ifndef GLM_GLM_H
#define GLM_GLM_H
#include <glm/glm.hpp>
#endif // GLM_GLM_H

#ifndef STD_VECTOR_H
#define STD_VECTOR_H
#include <vector>
#endif // STD_VECTOR_H

#ifndef MESH_H
#define MESH_H

typedef enum RenderMode {
    polygon=GL_POLYGON, wireframe=GL_LINE_LOOP, lines=GL_LINES, line_strip=GL_LINE_STRIP,
    triangles=GL_TRIANGLES, triangle_strip=GL_TRIANGLE_STRIP
};

class Polygon;
class Vertex;

class Vertex {
    friend class Polygon;
protected:
    /*!
     * List of pointers to \c Polygons this vertex is apart of.
     * Allows one vertex to be referenced by many polygons, reducing overhead.
     */
    std::vector<Polygon*> polygons;
    /*! position vector */
    glm::fvec3 pos;
    /*! the vertex normal, used in lighting */
    glm::fvec3 normal;
private:
    void addPolygonReference(Polygon* poly);
    void removePolygonReference(Polygon* poly);
    size_t getPolyReferenceCount();
    void updateNormal();
public:
    Vertex();
    Vertex(glm::fvec3 position);
    glm::fvec3 getPos();
    void setPos(glm::fvec3 position);
    glm::fvec3 getNormal();
    // OPERATIONS
    bool operator== (const Vertex &v2);
    bool operator!= (const Vertex &v2);
};

class Polygon {
    friend class Mesh;
protected:
    Polygon* next_polygon = nullptr;
    Polygon* prev_polygon = nullptr;
    std::vector<Vertex*> vertices;
    glm::fvec3 normal = glm::fvec3(0.0f, 0.0f, 0.0f);
    glm::fvec3 color = glm::fvec3(1.0f, 1.0f, 1.0f);
private:
    friend void Vertex::addPolygonReference(Polygon* poly);
    friend void Vertex::removePolygonReference(Polygon *poly);
    friend size_t Vertex::getPolyReferenceCount();
    friend void Vertex::updateNormal();
    bool updateNormal = true;
    glm::fvec3 computeNormal();
    void setNextPolygon(Polygon* poly);
    void setPrevPolygon(Polygon* poly);
public:
    /*!
     * \warning Empty constructor. DO NOT USE.
     */
    Polygon() {};
    ~Polygon();
    Polygon(std::vector<Vertex*> vertices, glm::fvec3 color);
    Polygon(std::vector<Vertex*> vertices);
    void render(RenderMode mode = polygon);
    void addVertex(Vertex *v);
    void setColor(glm::fvec3 &c);
    Polygon* getNextPolygon();
    Polygon* getPrevPolygon();
    glm::fvec3 getNormal();
    /*! add vertex operator */
    void operator<<(Vertex* vertex);
};

class Mesh {
protected:
    Polygon* first_polygon = nullptr;
    Polygon* last_polygon = nullptr;
private:
    friend void Polygon::setNextPolygon(Polygon *poly);
    friend void Polygon::setPrevPolygon(Polygon *poly);
public:
    Mesh();
    ~Mesh();
    Mesh(std::vector<Polygon*> polygons);
    Mesh(Polygon* first_polygon);
    void render(RenderMode render_mode = polygon);
    void addPolygon(Polygon *poly);
};

class RectangularPrismMesh : public Mesh {
protected:
    float length = 1.0f;
    float width = 1.0f;
    float depth = 1.0f;
    RectangularPrismMesh() {};
public:
    RectangularPrismMesh(float length, float width, float depth);
};

class CubeMesh : public RectangularPrismMesh {
public:
    CubeMesh(float side);
};

#endif // MESH_H
