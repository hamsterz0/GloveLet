#pragma once

#include <iostream>
#include <GL/glut.h>
#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glm/gtx/quaternion.hpp>

#include "src/Polygon.h"

using namespace glm;

void draw(void);
void idle(void);
void specialKeys(int key, int x, int y);
void specialUpKeys(int key, int x, int y);
void mouseMotionHandler(int x, int y);
void buildCube(Polygon* c[]);

float rotate_y = 0.0f;
float rotate_x = 0.0f;
float size = 1.0f;
bool isMouseChgInit = false;
bool upKeyPressed = false;
bool downKeyPressed = false;
bool leftKeyPressed = false;
bool rightKeyPressed = false;
glm::vec3 obj_pos(0.0f, 0.0f, 0.0f);
glm::vec2 mouse_prev(0.0f, 0.0f);
glm::vec2 mouse_chg(0.0f, 0.0f);
glm::vec2 mouse_pos(0.0f, 0.0f);
glm::fquat q(1.0f, 0.0f, 0.0f, 0.0f);

Polygon* cube[6];

int main(int argc, char* argv[]) {
    buildCube(cube);

    glutInit(&argc, argv);
    // Simple buffer
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowPosition(500,250);
    glutInitWindowSize(1000,500);
    glutCreateWindow("Glut Test");
    glEnable(GL_TEXTURE_2D);
    glEnable(GL_DEPTH_TEST);
    glShadeModel(GL_SMOOTH);
    glDepthFunc(GL_LEQUAL);
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
//    glutSetKeyRepeat(GLUT_KEY_REPEAT_OFF);
    // Call to the drawing function
    glutDisplayFunc(draw);
    glutSpecialFunc(specialKeys);
    glutSpecialUpFunc(specialUpKeys);
    glutPassiveMotionFunc(mouseMotionHandler);
    glutIdleFunc(idle);
    glutMainLoop();
    return 0;
}

void draw(void) {
    // Background color
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);

    // reset transformations
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glFrustum(-2.67, 2.67, -1.5, 1.5, 6.0, 600.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.0f,0.0f,-10.0f);

    mat4 rot_mat = mat4_cast(q); // cast quaternion to 4x4 rotation matrix

    glPushMatrix();
    glTranslatef(obj_pos.x,obj_pos.y,obj_pos.z);
    glMultMatrixf(value_ptr(rot_mat));
    // FRONT
    for(int i = 0; i < 6; i++) {
        cube[i]->draw();
    }
    glPopMatrix();

    // Draw order
    glFlush();
    glutSwapBuffers();
}

void idle() {
    if(upKeyPressed) obj_pos.z += 0.075f;
    if(downKeyPressed) obj_pos.z -= 0.075f;
    if(rightKeyPressed) obj_pos.x += 0.075f;
    if(leftKeyPressed) obj_pos.x -= 0.075f;
    glutPostRedisplay();
}

void specialKeys(int key, int x, int y) {
    switch (key) {
        case GLUT_KEY_RIGHT:
            rightKeyPressed = true;
            break;
        case GLUT_KEY_LEFT:
            leftKeyPressed = true;
            break;
        case GLUT_KEY_DOWN:
            downKeyPressed = true;
            break;
        case GLUT_KEY_UP:
            upKeyPressed = true;
            break;
        case GLUT_KEY_HOME:
            obj_pos.y += 0.5f;
            break;
        case GLUT_KEY_END:
            obj_pos.y -= 0.5f;
            break;
        default:
            break;
    }
}

void specialUpKeys(int key, int x, int y) {
    switch (key) {
        case GLUT_KEY_RIGHT:
            rightKeyPressed = false;
            break;
        case GLUT_KEY_LEFT:
            leftKeyPressed = false;
            break;
        case GLUT_KEY_DOWN:
            downKeyPressed = false;
            break;
        case GLUT_KEY_UP:
            upKeyPressed = false;
            break;
        default:
            break;
    }
}

void mouseMotionHandler(int x, int y) {
    if(!isMouseChgInit) {
        isMouseChgInit = true;
        mouse_prev.x = x;
        mouse_prev.y = y;
    }

    mouse_chg.x = (x - mouse_prev.x);
    mouse_chg.y = (y - mouse_prev.y);

    if(mouse_chg.x > 0)
        mouse_pos.x += 0.025f;
    else if(mouse_chg.x <= 0)
        mouse_pos.x -= 0.025f;

    if(mouse_chg.y > 0)
        mouse_pos.y += 0.025f;
    else if(mouse_chg.y <= 0)
        mouse_pos.y -= 0.025f;

    vec3 euler_angles(mouse_chg.y * 0.025f, mouse_chg.x * 0.025f, 0.0f);
    fquat rot = fquat(euler_angles);

    // The below order of multiplication will result in the world rotation transform.
    // Reversing the order to (q * rot) results in the local transform.
    // IE in the local transform, the rotation stays true to the object's origin axis,
    //      which the object's origin axis is changing relative to the world origin axis.
    // The
    q = rot * q;

    mouse_prev.x = x;
    mouse_prev.y = y;
}

void buildCube(Polygon* c[]) {
    Polygon* p;
    fvec3 v;
    Vertex* v1;
    Vertex* v2;
    Vertex* v3;
    Vertex* v4;
    fvec3 color;

    // FRONT
    v = fvec3(-size,-size,-size);
    v1 = new Vertex(v);
    v = fvec3(size,-size,-size);
    v2 = new Vertex(v);
    v = fvec3(size,size,-size);
    v3 = new Vertex(v);
    v = fvec3(-size,size,-size);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    c[0] = p;
    color = fvec3(1.0f, 1.0f, 1.0f);
    c[0]->setColor(color);
    // BACK
    v = fvec3(-size,-size,size);
    v1 = new Vertex(v);
    v = fvec3(-size,size,size);
    v2 = new Vertex(v);
    v = fvec3(size,size,size);
    v3 = new Vertex(v);
    v = fvec3(size,-size,size);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    c[1] = p;
    color = fvec3(1.0f, 0.0f, 1.0f);
    c[1]->setColor(color);
    // RIGHT
    v = fvec3(size,-size,-size);
    v1 = new Vertex(v);
    v = fvec3(size,-size,size);
    v2 = new Vertex(v);
    v = fvec3(size,size,size);
    v3 = new Vertex(v);
    v = fvec3(size,size,-size);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    c[2] = p;
    color = fvec3(1.0f, 0.0f, 0.0f);
    c[2]->setColor(color);
    // LEFT
    v = fvec3(-size,-size,-size);
    v1 = new Vertex(v);
    v = fvec3(-size,size,-size);
    v2 = new Vertex(v);
    v = fvec3(-size,size,size);
    v3 = new Vertex(v);
    v = fvec3(-size,-size,size);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    c[3] = p;
    color = fvec3(0.0f, 0.0f, 1.0f);
    c[3]->setColor(color);
    // TOP
    v = fvec3(-size,size,-size);
    v1 = new Vertex(v);
    v = fvec3(-size,size,size);
    v2 = new Vertex(v);
    v = fvec3(size,size,size);
    v3 = new Vertex(v);
    v = fvec3(size,size,-size);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    c[4] = p;
    color = fvec3(0.0f, 1.0f, 0.0f);
    c[4]->setColor(color);
    // BOTTOM
    v = fvec3(-size,-size,-size);
    v1 = new Vertex(v);
    v = fvec3(size,-size,-size);
    v2 = new Vertex(v);
    v = fvec3(size,-size,size);
    v3 = new Vertex(v);
    v = fvec3(-size,-size,size);
    v4 = new Vertex(v);

    p = new Polygon(*v1);
    p->addVertex(*v2);
    p->addVertex(*v3);
    p->addVertex(*v4);
    c[5] = p;
    color = fvec3(0.0f, 1.0f, 0.0f);
    c[5]->setColor(color);
}
