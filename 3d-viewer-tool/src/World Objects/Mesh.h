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

#endif //STDARG_H

#ifndef CSTDDEF_H
#define CSTDDEF_H

#include <cstddef>

#endif //CSTDDEF_H

#ifndef GLM_GLM_H
#define GLM_GLM_H

#include <glm/glm.hpp>

#endif // GLM_GLM_H

#ifndef MESH_H
#define MESH_H

typedef enum RenderMode {
    polygon=GL_POLYGON, wireframe=GL_LINE_LOOP, lines=GL_LINES,
    triangles=GL_TRIANGLES, triangle_strip=GL_TRIANGLE_STRIP
};

class Polygon;
class Vertex;

class Vertex {
protected:
    Vertex *next_vertex = nullptr;
    glm::fvec3 pos;
public:
    Vertex();
    Vertex(glm::fvec3 &position);
    Vertex(Vertex &v);
    glm::fvec3 getPos();
    Vertex* getNextVertex();
    void setPos(glm::fvec3 &position);
    void setNextVertex(Vertex &next);
    // OPERATIONS
    bool operator== (const Vertex &v2);
    bool operator!= (const Vertex &v2);
};


class Polygon {
    friend class Mesh;
protected:
    Vertex* start_vertex = nullptr;
    Vertex* end_vertex = nullptr;
    Polygon* next_polygon = nullptr;
    Polygon* prev_polygon = nullptr;
    glm::fvec3 color = glm::fvec3(1.0f, 1.0f, 1.0f);
private:
    void setNextPolygon(Polygon* poly);
    void setPrevPolygon(Polygon* poly);
public:
    /*!
     * \warning Empty constructor. DO NOT USE.
     */
    Polygon() {};
    ~Polygon();
    Polygon(Vertex &start);
    Polygon(Vertex &start, glm::fvec3 &color);
    Polygon(size_t n_vert, Vertex &v, ...);
    void draw(RenderMode mode = polygon);
    void addVertex(Vertex &v);
    const Vertex *getStartVertex();
    const Vertex *getEndVertex();
    void setColor(glm::fvec3 &c);
    Polygon* getNextPolygon();
    Polygon* getPrevPolygon();
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

#endif //MESH_H
