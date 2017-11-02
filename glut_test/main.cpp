#include <iostream>
#include <GL/glut.h>

void draw(void);
void specialKeys(int key, int x, int y);

float rotate_y = 0.0f;
float rotate_x = 0.0f;
float size = 0.25f;
float mv_z = 0.0f;


int main(int argc, char* argv[]) {
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
    // Call to the drawing function
    glutDisplayFunc(draw);
    glutSpecialFunc(specialKeys);

    glutMainLoop();
    return 0;
}

void draw(void) {
    // Background color
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);

    // reset transformations
//    glMatrixMode(GL_PROJECTION);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glFrustum(-2.58, 2.58, -1.5, 1.5, 6.0, 600.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.0f,0.0f,-10.0f);


    glPushMatrix();
    glRotatef(rotate_x,1.0f,0.0f,0.0f);
    glRotatef(rotate_y,0.f,1.0f,0.0f);
    glTranslatef(0.0f,0.0f,mv_z);
    // FRONT
    glBegin(GL_QUADS);
    glColor3f(1.0f, 0.0f, 1.0f);
    glVertex3f(-size,-size,-size);      // P1
    glVertex3f(-size,size,-size);       // P2
    glVertex3f(size,size,-size);        // P3
    glVertex3f(size,-size,-size);        // P4
    glEnd();
    // BACK
    glBegin(GL_QUADS);
    glColor3f(1.0f, 1.0f, 1.0f);
    glVertex3f(-size,-size,size);      // P1
    glVertex3f(-size,size,size);       // P2
    glVertex3f(size,size,size);        // P3
    glVertex3f(size,-size,size);        // P4
    glEnd();
    // RIGHT
    glBegin(GL_QUADS);
    glColor3f(0.0f, 0.0f, 1.0f);
    glVertex3f(size,-size,-size);      // P1
    glVertex3f(size,size,-size);       // P2
    glVertex3f(size,size,size);        // P3
    glVertex3f(size,-size,size);        // P4
    glEnd();
    // LEFT
    glBegin(GL_QUADS);
    glColor3f(1.0f, 0.0f, 0.0f);
    glVertex3f(-size,-size,size);      // P1
    glVertex3f(-size,size,size);       // P2
    glVertex3f(-size,size,-size);        // P3
    glVertex3f(-size,-size,-size);        // P4
    glEnd();
    // TOP
    glBegin(GL_QUADS);
    glColor3f(0.0f, 1.0f, 0.0f);
    glVertex3f(-size,size,-size);      // P1
    glVertex3f(-size,size,size);       // P2
    glVertex3f(size,size,size);        // P3
    glVertex3f(size,size,-size);        // P4
    glEnd();
    // BOTTOM
    glBegin(GL_QUADS);
    glColor3f(1.0f, 1.0f, 0.0f);
    glVertex3f(size,-size,-size);      // P1
    glVertex3f(size,-size,size);       // P2
    glVertex3f(-size,-size,size);        // P3
    glVertex3f(-size,-size,-size);        // P4
    glEnd();
    glPopMatrix();

    // Draw order
    glFlush();
    glutSwapBuffers();
}

void specialKeys(int key, int x, int y) {
    switch (key) {
        case GLUT_KEY_RIGHT:
            rotate_y += 5.0f;
            break;
        case GLUT_KEY_LEFT:
            rotate_y -= 5.0f;
            break;
        case GLUT_KEY_DOWN:
            rotate_x -= 5.0f;
            break;
        case GLUT_KEY_UP:
            rotate_x += 5.0f;
            break;
        case GLUT_KEY_HOME:
            mv_z += 0.1f;
            break;
        case GLUT_KEY_END:
            mv_z -= 0.1f;
            break;
        default:
            break;
    }

    glutPostRedisplay();
}