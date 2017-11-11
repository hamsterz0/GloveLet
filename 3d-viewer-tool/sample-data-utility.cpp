//
// Created by joseph on 11/10/17.
//

#include <chrono>
#include <iostream>
#include <GL/gl.h>
#include <GL/glut.h>
#include <glm/glm.hpp>
#include "src/Template Objects/TemplateObjects.h"

using namespace std;

// CALLBACK FUNCTIONS
void render(void);
// OTHER FUNCTIONS
void build3DObject();

int main(int argc, char* argv[]) {
    int displayWidth = 0, displayHeight = 0,
            windowWidth = 0, windowHeight = 0,
            windowPosX = 0, windowPosY = 0;

    glutInit(&argc, argv);

    // Double buffered, RGB color mode, render for depth
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    displayWidth = glutGet(GLUT_SCREEN_WIDTH);
    displayHeight = glutGet(GLUT_SCREEN_HEIGHT);
    cout << "displayWidth= " << displayWidth << ", displayHeight= " << displayHeight << endl;
    windowWidth = displayWidth / 2;
    windowHeight = displayHeight / 2;
    windowPosX = windowWidth - (windowWidth / 2);
    windowPosY = windowHeight - (windowHeight / 2);
    glutInitWindowSize(windowWidth, windowHeight);
    glutInitWindowPosition(windowPosX, windowPosY);
//    glutFullScreen();
    glutCreateWindow("3D Viewer Tool - ");
    glEnable(GL_TEXTURE_2D);
    glEnable(GL_DEPTH_TEST);
    glShadeModel(GL_SMOOTH);
    glDepthFunc(GL_LEQUAL); // Instructs GL functions to render depth, not orthogonal
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);

    glutDisplayFunc(render);

    glutMainLoop();
}

void render(void) {
    // Background color
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);

    // reset transformations
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glFrustum(-2.67, 2.67, -1.5, 1.5, 6.0, 600.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.0f,0.0f,-15.0f);

    // flush and swap buffers
    glFlush();
    glutSwapBuffers();
}