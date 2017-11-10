//
// Created by joseph on 11/9/17.
//
#pragma once

#ifndef MESH_H
#include "Mesh.h"
#endif // MESH_H

#ifndef AXIS_H
#define AXIS_H


class Axis : public Mesh {
private:
    float length = 1.0f;
    Vertex* x_axis;
    Vertex* y_axis;
    Vertex* z_axis;
public:
    Axis(float axis_length);
    Axis();
    void setAxisLength(float axis_length);
};


#endif //AXIS_H
