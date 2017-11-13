#pragma once

#include <iostream>
#include <GL/glut.h>
#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
#include "src/Template Objects/TemplateObjects.h"

#ifndef TEST_OBJ_SZ
#define TEST_OBJ_SZ 7
#endif

using namespace glm;

void draw(void);
void idle(void);
void specialKeys(int key, int x, int y);
void specialUpKeys(int key, int x, int y);
void mouseMotionHandler(int x, int y);
void createTestObject(WorldObject **obj, size_t sz);

bool isMouseChgInit = false;
bool upKeyPressed = false;
bool downKeyPressed = false;
bool leftKeyPressed = false;
bool rightKeyPressed = false;
glm::vec3 obj_pos(0.0f, 0.0f, 0.0f);
glm::vec2 mouse_prev(0.0f, 0.0f);
glm::vec2 mouse_chg(0.0f, 0.0f);
glm::vec2 mouse_pos(0.0f, 0.0f);

glm::fquat q = fquat(fvec3(0.0f, 0.0f, radians(1.0f)));
glm::fquat lq = fquat(fvec3(radians(1.0f), 0.0f, 0.0f));

WorldObject* test_obj[TEST_OBJ_SZ];

int main(int argc, char* argv[]) {
    createTestObject(test_obj, TEST_OBJ_SZ);

    glutInit(&argc, argv);
    // Simple buffer
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowPosition(500,250);
    glutInitWindowSize(1000,500);
    glutCreateWindow("3D Viewer Tool - TEST PROGRAM");
    glEnable(GL_TEXTURE_2D);
    glEnable(GL_DEPTH_TEST);
    glShadeModel(GL_SMOOTH);
    glDepthFunc(GL_LEQUAL);     // Instructs GL functions to render depth, not orthogonal
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
    glutSetKeyRepeat(GLUT_KEY_REPEAT_OFF);
    // Callback to the drawing function
    glutDisplayFunc(draw);
    // Callback to special key handler function
    glutSpecialFunc(specialKeys);
    // Callback to special key UP handler function
    glutSpecialUpFunc(specialUpKeys);
    // Callback to mouse motion handler function
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
    glFrustum(-2.67, 2.67, -1.5, 1.5, 5.0, 600.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.0f,0.0f,-15.0f);

    glPushMatrix();
    test_obj[0]->render();
    glPopMatrix();

    // Draw order
    glFlush();
    glutSwapBuffers();
}

void idle() {
    fvec3 mv = fvec3(0.0f, 0.0f, 0.0f);
    if(upKeyPressed) mv.z += 0.075f;
    if(downKeyPressed) mv.z -= 0.075f;
    if(rightKeyPressed) mv.x += 0.075f;
    if(leftKeyPressed) mv.x -= 0.075f;
    test_obj[0]->move(mv);

    for(int i = 1; i < TEST_OBJ_SZ; i++) {
        if(test_obj[i]) {
            test_obj[i]->rotate(q);
            test_obj[i]->rotate(lq, true);
        }
    }

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

    fvec3 euler_angles(mouse_chg.y * 0.025f, mouse_chg.x * 0.025f, 0.0f);
    auto rot = fquat(euler_angles);

    // The below order of multiplication will result in the world rotation transform.
    // Reversing the order to (q * rot) results in the local transform.
    // IE in the local transform, the rotation stays true to the object's origin axis,
    //      which the object's origin axis is changing relative to the world origin axis.
    test_obj[0]->rotate(rot);

    mouse_prev.x = x;
    mouse_prev.y = y;
}

void createTestObject(WorldObject * obj[], size_t sz) {
    auto pos = fvec3(0.0f, 0.0f, 0.0f);
    obj[0] = (WorldObject*)new Cube(1.0f, pos);
    auto rot = fquat(fvec3(0.0f, 0.0f, 0.0f));
    pos = fvec3(0.0f, 0.0f, 0.0f);
    obj[1] = (WorldObject*)new RectangularPrism(0.75f, 0.25f, 0.25f,
            pos, rot);
    pos = fvec3(2.5f, 0.0f, 0.0f);
    obj[1]->setLocalPosition(pos);

    rot = fquat(fvec3(0.0f, 0.0f, radians(90.0f)));
    pos = fvec3(0.0f, 2.5f, 0.0f);
    obj[2] = obj[1]->duplicate();
    obj[2]->setLocalPosition(pos);
    obj[2]->setLocalRotation(rot);

    rot = fquat(fvec3(0.0f, 0.0f, radians(-90.0f)));
    pos = fvec3(0.0f, -2.5f, 0.0f);
    obj[3] = obj[1]->duplicate();
    obj[3]->setLocalPosition(pos);
    obj[3]->setLocalRotation(rot);

    rot = fquat(fvec3(radians(180.0f), radians(180.0f), 0.0));
    pos = fvec3(-2.5f, 0.0f, 0.0f);
    obj[4] = obj[1]->duplicate();
    obj[4]->setLocalPosition(pos);
    obj[4]->setLocalRotation(rot);

    obj[5] = nullptr;
    obj[6] = nullptr;

    for(int i = 1; i < TEST_OBJ_SZ; i++) {
        obj[0]->addChild(*obj[i]);
        if(obj[i]) {
            obj[i]->getMesh()->showPolygonNormals(true);
            obj[i]->getMesh()->showVertexNormals(true);
//            obj[i]->setRenderMode(wireframe);
        }
    }
    obj[0]->doAxisRender(true);
    obj[0]->getMesh()->showPolygonNormals(true);
    obj[0]->getMesh()->showVertexNormals(true);
//    obj[0]->setRenderMode(wireframe);
}
