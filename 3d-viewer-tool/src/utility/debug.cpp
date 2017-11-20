//
// Created by joseph on 11/18/17.
//
#pragma once

#include <GL/gl.h>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>
#include <glm/gtc/type_ptr.hpp>
#include "../Template Objects/TemplateObjects.h"
#include "debug.h"

void draw_vector(glm::fvec3 vector, glm::fvec3 origin, glm::fvec3 color) {
    glPushMatrix();
    glBegin(lines);
    glColor3fv(glm::value_ptr(color));
    glVertex3fv(glm::value_ptr(vector));
    glVertex3fv(glm::value_ptr(origin));
    glEnd();
    glPopMatrix();
}
