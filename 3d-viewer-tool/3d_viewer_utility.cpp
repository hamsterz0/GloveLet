//
// Created by joseph on 11/10/17.
//
#pragma once

#include <chrono>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <GL/gl.h>
#include <GL/glut.h>
#include <glm/gtc/quaternion.hpp>
#include <glm/glm.hpp>
#include "src/Template Objects/TemplateObjects.h"
#include "src/utility/debug.h"
//#include "src/utility/MadgwickAHRS/MadgwickAHRS.h"
//#include "src/utility/MahonyAHRS/MahonyAHRS.h"

#ifdef WINDOWS
    #include <direct.h>
    #define GetCurrentDir _getcwd
#else
    #include <unistd.h>
    #define GetCurrentDir getcwd
#endif

using namespace glm;

// CALLBACK FUNCTIONS
void render(void);
void timer(int value);
void prgm_exit(int value, void *arg);

// OTHER FUNCTIONS
char determineLineDelimiter();
bool parseArguments(int argc, char **argv);
bool readDataLine(float * p_data[9]);
WorldObject* construct3DObject();
std::string getRuntimeDirectory();


// APPLICATION PARAMETERS
bool debug = false;
unsigned int sample_rate = 125;

// PROGRAM GLOBALS
char delim = '\n';
unsigned int sample_count = 0;
float inv_sample_rate = 1.0f / (float)sample_rate;
float g = 0.0f;
std::ifstream stream;
WorldObject* obj = new RectangularPrism(1.0f, 0.25f, 1.0);
glm::fvec3 velocity = glm::fvec3(0.0f, 0.0f, 0.0f);
glm::fvec3 grav3 = glm::fvec3(0.0f, 0.0f, 0.0f);
glm::fvec4 gravity = glm::fvec4(0.0f, 0.0f, 0.0f, 0.0f);


int main(int argc, char* argv[]) {
    // on-exit callback function
    on_exit(prgm_exit, nullptr);

    // parse GLUT arguments
    glutInit(&argc, argv);

    // parse program arguments
    if(!parseArguments(argc, argv))
        return 1;

    // determine line delimiter character of input file
//    delim = determineLineDelimiter();

    // if debug, display 3D object local axis
    if(debug) obj->doAxisRender(true);

    // Initialize variables for determining window size
    int displayWidth = 0, displayHeight = 0,
            windowWidth = 0, windowHeight = 0,
            windowPosX = 0, windowPosY = 0;

    // Double buffered, RGB color mode, render for depth
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    float width_aspect = 1920.0f / 1080.0f;
    float height_aspect = 1080.0f / 1920.0f;
    displayWidth = glutGet(GLUT_SCREEN_WIDTH);
    displayHeight = glutGet(GLUT_SCREEN_HEIGHT);
    // Fixes an issue on where the display width/height of a multi-monitor setup
    // is calculated as a total of the width/height of all display monitors. Without the below,
    // the result is a window with an aspect ratio stretched across multiple monitors.
    if((int)(displayWidth * height_aspect) > displayHeight) displayWidth = (int)(displayHeight * width_aspect);
    else if((int)(displayHeight * width_aspect) > displayWidth) displayHeight = (int)(displayWidth * width_aspect);

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
    glutTimerFunc((unsigned int)(inv_sample_rate * 1000.0f), timer, (unsigned int)(inv_sample_rate * 1000.0f));

    // Start main loop
    glutMainLoop();
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
    glTranslatef(0.0f,-10.0f,-70.0f);

    // do rendering
    obj->render();
    if(debug) draw_vector(2.0f*glm::normalize(grav3) + obj->getPosition(), obj->getPosition());

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
    float* p_data = data;
    float time_interval = 0.008f;
    char buf[256];
    if(readDataLine(&p_data)) {
        sample_count++;
        // get intial values of accelerometer and initial acceleration-due-to-gravity
        glm::fvec3 a = glm::fvec3(data[3], data[5], data[4]);
        glm::fvec3 a_norm = glm::normalize(a);
        if(glm::length(gravity) == 0.0f) {
            // Compute acceleration due to gravity.
            // Assumes IMU isn't moving in first sample.
            g = glm::length(a);
            gravity = glm::fvec4(a, 0);
        }
        // get quaternion from gyroscope data
        glm::fquat gyro_quat;
        glm::fvec3 gyro_euler = glm::fvec3(data[0], data[1], data[2]) * time_interval;
        gyro_quat = glm::fquat(gyro_euler);
        // get quaternion for magnetometer (unsure this can even be interpreted as a "rotation")
        glm::fquat magnet_quat;
        glm::fvec3 magnet_euler = glm::fvec3(data[6], data[7], data[8]) * time_interval;
        magnet_quat = glm::fquat(magnet_euler);
        // calculate rotation
        glm::fquat rotation = (gyro_quat * magnet_quat);
        // calculate the new local orientation for the gravity vector
        glm::fquat grav_rotation = glm::inverse(rotation);
        glm::mat4 rot_mat = glm::mat4_cast(rotation);
        glm::mat4 inv_rot = glm::mat4_cast(grav_rotation);
        gravity = gravity * inv_rot * rot_mat;
        // subtract gravitational acceleration from total acceleration
        grav3 = -glm::fvec3(gravity);
        glm::fvec3 acceleration = a + grav3;
        // Calculate the inverse log of the magnitude of the acceleration vector
        // derived above. This is in an effort to combat the exponential drift
        // caused by integration.
        float accel_len = glm::length(acceleration);
        float accel_log = glm::log(accel_len) / glm::log(200.0f);
        if(accel_log < 1.0f) {
            accel_log = 1.0f;
        }
        else accel_log = 1.0f / accel_log;
        auto accel_sign = glm::fvec3(acceleration);
        // determine sign of components
        accel_sign.x /= glm::abs(accel_sign.x);
        accel_sign.y /= glm::abs(accel_sign.y);
        accel_sign.z /= glm::abs(accel_sign.z);
        // use inverse of natural log of the gravity vector magnitude
        acceleration.x = glm::pow(glm::abs(acceleration.x), accel_log) * accel_sign.x;
        acceleration.y = glm::pow(glm::abs(acceleration.y), accel_log) * accel_sign.y;
        acceleration.z = glm::pow(glm::abs(acceleration.z), accel_log) * accel_sign.z;
        // check for 'NAN' values and set to 0 if found
        if(isnanf(acceleration.x)) acceleration.x = 0.0f;
        if(isnanf(acceleration.y)) acceleration.y = 0.0f;
        if(isnanf(acceleration.z)) acceleration.z = 0.0f;
        // calculate velocity
        acceleration *= time_interval;
        velocity = acceleration; // assumes velocity is initially zero
        // update 3D object's position and rotation
        obj->move(velocity);
        obj->setLocalRotation(rotation);
        // print debug information
        if(debug) {
            auto accel_preinvlog = glm::fvec3(a + grav3);
            std::cout << "sample:  " << sample_count << std::endl;
            std::cout << "  raw data:  ";
            for(auto val : data) std::cout << val << " ";
            std::cout << std::endl;
            std::cout << "  accel_len= " << accel_len << ", accel_log= " << accel_log << std::endl;
            std::cout << "  acceleration:  " <<
                      acceleration.x << " " <<
                      acceleration.y << " " <<
                      acceleration.z << std::endl;
            std::cout << "  accel_preinvlog:  " <<
                      accel_preinvlog.x << " " <<
                      accel_preinvlog.y << " " <<
                      accel_preinvlog.z << std::endl;
        }
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
                      << "   -h, --help    Show help options" << std::endl
                      << std::endl
                      << "Application Options:" << std::endl
                      << "   -i, --input   Set path to input file stream. When not" << std::endl
                      << "                    specified, the standard input is used" << std::endl
                      << "                    to support piping." << std::endl
                      << "   --hz          Set the simulated sample rate in samples-per-" << std::endl
                      << "                   second. Default is 125.0 Hz." << std::endl;
            result = false;
        }
    }
    if(result) {
        // When help option not found, attempt to parse the arguments
        for(size_t i = 1; i < argc; i++) {
            if(argv[i][0] == '-') {
                std::string option(argv[i]);
                std::string value;
                if(option.compare("-d") == 0)
                    debug = true;
                else {
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
    return result;
}

/*!
 * Retrieves IMU data from standard input.
 * \attention Input is expected to be in the specified format,
 * enumerated by \c DatalogParser::LogType. If data is not in any defined
 * format, unexpected results may occur.
 * @param p_data - \c float** - pointer to \c float array of minimum size \c 9
 * @return \code bool \endcode
 * Returns \c true if IMU
 */
bool readDataLine(float * p_data[9]) {
    float* data = *p_data;
    bool result = true;
    char buffer[1024];
    if(!std::cin.eof()) {
        std::cin.getline(buffer, 1024, delim);
        std::stringstream stringstream(buffer);

        int i = 0;
        try {
            while(i < 9 && stringstream >> data[i]) i++;
        }
        catch (std::ifstream::failure e) {
            std::cerr << e.what() << std::endl;
            result = false;
        }

    } else result = false;

    return result;
}

char determineLineDelimiter() {
    char result = '\0';
    int ch_cnt = 0;
    while(true) {
        char c = (char)std::cin.get();
        ch_cnt++;
        switch(c) {
            case '\n':
                result = '\n';
                break;
            case '\r':
                result = '\r';
                break;
            case EOF:
                result = '\n';
                break;
            default:
                break;
        }
        if(result != '\0') break;
    }

    for(int i = 0; i < ch_cnt; i++) std::cin.unget();

    return result;
}