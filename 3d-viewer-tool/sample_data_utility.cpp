//
// Created by joseph on 11/10/17.
//
#pragma once

#include <chrono>
#include <iostream>
#include <fstream>
#include <vector>
#include <GL/gl.h>
#include <GL/glut.h>
#include <glm/gtc/quaternion.hpp>
#include <glm/glm.hpp>
#include <glm/geometric.hpp>
#include "src/Template Objects/TemplateObjects.h"
#include "src/utility/MadgwickAHRS/MadgwickAHRS.h"
//#include "src/utility/MahonyAHRS/MahonyAHRS.h"

#ifdef WINDOWS
    #include <direct.h>
    #define GetCurrentDir _getcwd
#else
    #include <unistd.h>
    #define GetCurrentDir getcwd
#endif

// CALLBACK FUNCTIONS
void idle(void);
void render(void);
void timer(int value);
void prgm_exit(int value, void *arg);

using namespace glm;

// OTHER FUNCTIONS
bool parseArguments(int argc, char **argv);
WorldObject* construct3DObject();
std::string getRuntimeDirectory();

// APPLICATION PARAMETERS
std::ifstream stream;
unsigned int sample_rate = 100;
float inv_sample_rate = 1.0f / (float)sample_rate;
WorldObject* obj = new RectangularPrism(1.0f, 0.25f, 1.0);
glm::fvec3 velocity = glm::fvec3(0.0f, 0.0f, 0.0f);
float g = 0.0f;


int main(int argc, char* argv[]) {
    on_exit(prgm_exit, nullptr);
    int displayWidth = 0, displayHeight = 0,
            windowWidth = 0, windowHeight = 0,
            windowPosX = 0, windowPosY = 0;

    glutInit(&argc, argv);
    if(!parseArguments(argc, argv))
        return 1;
    // Double buffered, RGB color mode, render for depth
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    float width_aspect = 1920.0f / 1080.0f;
    float height_aspect = 1080.0f / 1920.0f;
    displayWidth = glutGet(GLUT_SCREEN_WIDTH);
    displayHeight = glutGet(GLUT_SCREEN_HEIGHT);
    // Fixes an issue on Linux where the display width/height of a multi-monitor setup
    // is calculated as a total of the width/height of all display monitors. Without the below,
    // the result is a window with an aspect ratio much different than a single monitor.
    if((int)(displayWidth * height_aspect) > displayHeight) displayWidth = (int)(displayHeight * width_aspect);
    else if((int)(displayHeight * width_aspect) > displayWidth) displayHeight = (int)(displayWidth * width_aspect);

//    cout << "displayWidth= " << displayWidth << ", displayHeight= " << displayHeight << endl; // FIXME DEBUG

    // Calculate & initialize window size and position
    windowWidth = displayWidth / 2;
    windowHeight = displayHeight / 2;
    windowPosX = windowWidth - (windowWidth / 2);
    windowPosY = windowHeight - (windowHeight / 2);
    glutInitWindowSize(windowWidth, windowHeight);
    glutInitWindowPosition(windowPosX, windowPosY);
    // Create window and initialize OpenGL settings
    glutCreateWindow("Sample Data Viewer");
    glEnable(GL_TEXTURE_2D);
    glEnable(GL_DEPTH_TEST);
    glShadeModel(GL_SMOOTH);
    glDepthFunc(GL_LEQUAL); // Instructs GL functions to render depth, not orthogonal
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
    // Set GLUT callback functions
    glutDisplayFunc(render);
    glutTimerFunc(10, timer, sample_rate / 10);
    // Start main loop
    glutMainLoop();
}

/*!
 * Idle callback function.
 */
void idle(void) {
//    glutPostRedisplay();
}

/*!
 * Display callback function.
 */
void render(void) {
    // Clear OpenGL buffers
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
    // Reset camera/projection transformation
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glFrustum(-2.67, 2.67, -1.5, 1.5, 6.0, 600.0);
    // Reset model transformation
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.0f,-10.0f,-50.0f);

    // do rendering
    obj->render();

    // flush and swap buffers
    glFlush();
    glutSwapBuffers();
}

/*!
 * Timer callback function.
 * @param value - <code> unsigned int </code>
 */
void timer(int value) {
    float data[9];
    char buf[256];
    if(!std::cin.eof()) {
        for(int i = 0; i < 9; i++) std::cin >> data[i];
        for(auto val : data) std::cout << val << " ";
        std::cout << std::endl;

        float rot_scale = 0.001953125f;
        glm::fquat gyro;
        glm::fvec3 gyro_euler = glm::fvec3(data[0]*rot_scale, data[1]*rot_scale, data[2]*rot_scale);
        gyro = glm::fquat(gyro_euler);
        glm::fquat magnet;
        glm::fvec3 magnet_euler = glm::fvec3(data[6], data[7], data[8]) * rot_scale;
        magnet = glm::fquat(magnet_euler);
        glm::fquat rotation = (gyro * magnet);
        rotation = normalize(rotation);
        // acceleration
        glm::fvec3 a = glm::fvec3(data[3], data[5], data[4]);
        glm::fvec3 a_norm = glm::normalize(a);
        if(g == 0) {
            // Compute acceleration due to gravity.
            // Assumes IMU isn't moving in first sample.
            g = glm::sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
        }
        glm::fvec3 v = ((a - (a_norm * g)) * 0.001953125f);
        velocity = v;
        obj->setLocalRotation(rotation);
        obj->move(velocity);
    }

    glutTimerFunc((unsigned int)value, timer, value);
    glutPostRedisplay();
}

/*!
 *
 * @param argc - <code> int </code>
 * @param argv - <code> char ** </code>
 * @return \code bool \endcode
 * Returns \c false if the help option was found or an option was incorrectly invoked by the user.
 * Otherwise, \c true is returned.
 */
bool parseArguments(int argc, char **argv) {
    bool result = true;
    for(size_t i = 1; i < argc; i++) {
        // Check for help option first
        std::string option(argv[i]);
        if(option.compare("-h") == 0 || option.compare("--help") == 0) {
            // print help options
            std::cout << "======== Sample IMU Data 3D Visualizer utility ========" << std::endl
                      << "usage:" << std::endl
                      << "   sample-data-utility.exe [-h|--help] [-i <path>|--input <path>]" << std::endl
                      << "                           [--hz <value>]" << std::endl
                      << std::endl
                      << "Help Options:" << std::endl
                      << "   -h, --help           Show help options" << std::endl
                      << std::endl
                      << "Application Options:" << std::endl
                      << "   -i, --input   Set path to input file stream. When not" << std::endl
                      << "                   specified, 'stdin' is used to support piping." << std::endl
                      << "   --hz          Set the simulated sample rate in samples-per-" << std::endl
                      << "                   second. Default is 100.0 Hz." << std::endl;
            result = false;
        }
    }
    if(result) {
        // When help option not found, attempt to parse the arguments
        for(size_t i = 1; i < argc; i++) {
            if(argv[i][0] == '-') {
                std::string option(argv[i]);
                std::string value;
                try {
                    value = std::string(argv[++i]); // the following option here will be value associated with previous option option
                } catch (std::logic_error e) {
                    std::cerr << "ERR: Expecting value following \'" << option << "\' option." << std::endl
                         << "Enter \'-h\' or \'--help\' to view help options." << std::endl;
                    result = false;
                }
                if(option.compare("-i") == 0 || option.compare("--input") == 0) {
                    std::string cmd;
                    std::string currentPath = getRuntimeDirectory();
                    cmd += currentPath + "/datalog-file-converter " + value + " ./temp.data";
                    if(system(cmd.c_str())) // creates temp.data file when successful
                        result = false;
                    stream = std::ifstream("temp.data");
                    std::cin.rdbuf(stream.rdbuf()); // redirect standard input read buffer
                    if(!stream) {
                        std::cerr << "Was unable to open the file \'" << value << "\'." << std::endl;
                        result = false;
                    }
                } else if(option.compare("--hz") == 0) {
                    try {
                        sample_rate = (unsigned int)std::stoi(value);
                        std::cout << "Sample rate set to " << sample_rate << " Hz." << std::endl;
                        inv_sample_rate = 1.0f / (float)sample_rate;
                    } catch (std::invalid_argument e) {
                        std::cerr << "ERR: There must be a positive integer value following \'" << option << "\'." << std::endl;
                        result = false;
                    } catch (std::system_error e) {
                        std::cerr << e.what() << std::endl;
                        result = false;
                    }
                }
            }
        }
    }
    return result;
}

std::string getRuntimeDirectory() {
    std::string result;
    char currentPath[FILENAME_MAX];
    GetCurrentDir(currentPath, sizeof(currentPath));
    result = std::string(currentPath);
    return result;
}

void prgm_exit(int value, void *arg) {
    stream.close();
    remove("temp.data");
    exit(value);
}

WorldObject* construct3DObject() {
    WorldObject* result = new RectangularPrism(1.0f, 0.25f, 1.0);
}