//
// Created by joseph on 11/4/17.
//

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

#ifndef POLYGON_H
#define POLYGON_H

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
protected:
    Vertex* start_vertex;
    Vertex* end_vertex;
    glm::fvec3 color = glm::fvec3(1.0f, 1.0f, 1.0f);
public:
    /*!
     * \warning Empty constructor. DO NOT USE.
     */
    Polygon() {};
    ~Polygon();
    Polygon(Vertex &start);
    Polygon(Vertex &start, glm::fvec3 &color);
    Polygon(size_t n_vert, Vertex &v, ...);
    void draw();
    void addVertex(Vertex &v);
    const Vertex getStartVertex();
    const Vertex getEndVertex();
    void setStartVertex(Vertex &v);
    void setEndVertex(Vertex &v);
    void setColor(glm::fvec3 &c);
};


#endif //POLYGON_H
