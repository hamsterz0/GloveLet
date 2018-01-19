/*!
 * @author: Joseph Tompkins
 * @date: November 10, 2017
 */
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
#include "src/utility/Serial.h"
#include "src/utility/debug.h"
#include "src/utility/DataTimeSeries.h"
//#include "src/utility/MadgwickAHRS/MadgwickAHRS.h"
//#include "src/utility/MahonyAHRS/MahonyAHRS.h"

#ifdef WINDOWS
    #include <direct.h>
    #define GetCurrentDir _getcwd
#else
    #include <unistd.h>
#define GetCurrentDir getcwd
#endif

#ifndef SAMPLE01
#define SAMPLE01_DOF 9
#define SAMPLE01_ACC_BITWIDTH 12
#define SAMPLE01_ACC_VREF 3.3f
#define SAMPLE01_ACC_VZEROGX 1.5f
#define SAMPLE01_ACC_VZEROGY 1.5f
#define SAMPLE01_ACC_VZEROGZ 1.5f
#define SAMPLE01_ACC_SENSITIVITY 4096.0f
#endif //SAMPLE01

#ifndef MPU6050
#define MPU6050_DOF 6
#define MPU6050_ACC_BITWIDTH 16
//#define MPU6050_ACC_VREF 1.71f
#define MPU6050_ACC_VREF 3.46f
#define MPU6050_ACC_VZEROGX 1.09375f
#define MPU6050_ACC_VZEROGY 1.09375f
#define MPU6050_ACC_VZEROGZ 1.09375f
//#define MPU6050_ACC_SENSITIVITY 16384.0f
//#define MPU6050_ACC_SENSITIVITY 8192.0f
#define MPU6050_ACC_SENSITIVITY 4096.0f
//#define MPU6050_ACC_SENSITIVITY 2048.0f
#endif //MPU6050

#ifndef SERIES_SIZE
#define SERIES_SIZE 64
#endif //SERIES_SIZE

using namespace glm;
namespace chrono = std::chrono;

// CALLBACK FUNCTIONS
void render(void);
void timer(int value);
void serial_timer(int value);
void idle(void);
void prgm_exit(int value, void *arg);

// OTHER FUNCTIONSdd
void process_data(float data[]);
bool parseArguments(int argc, char **argv);
bool readDataLine(float * p_data[]);
WorldObject* construct3DObject();
std::string getRuntimeDirectory();

// APPLICATION PARAMETERS
bool debug = false;
bool isSerial = false;
unsigned int sample_rate = 125;
unsigned short dof = SAMPLE01_DOF;
unsigned short adc_bit_width = SAMPLE01_ACC_BITWIDTH;
float vref = SAMPLE01_ACC_VREF;
float vzerogx = SAMPLE01_ACC_VZEROGX;
float vzerogy = SAMPLE01_ACC_VZEROGY;
float vzerogz = SAMPLE01_ACC_VZEROGZ;
float sensitivity = SAMPLE01_ACC_SENSITIVITY;


// PROGRAM GLOBALS
char delim = '\n';
unsigned int sample_count = 0;
float inv_sample_rate;
float g_mag = 0.0f;
std::ifstream stream;
Serial *serial;
DataTimeSeries<glm::fvec3, SERIES_SIZE> accTimeSeries = DataTimeSeries<glm::fvec3, SERIES_SIZE>(20);
DataTimeSeries<glm::fvec3, SERIES_SIZE> gyroTimeSeries = DataTimeSeries<glm::fvec3, SERIES_SIZE>(20);
WorldObject* obj = new RectangularPrism(1.0f, 0.25f, 1.0);
glm::fvec3 velocity = glm::fvec3(0.0f, 0.0f, 0.0f);
glm::fvec3 grav3 = glm::fvec3(0.0f, 0.0f, 0.0f);
glm::fvec4 gravity = glm::fvec4(0.0f, 0.0f, 0.0f, 0.0f);
chrono::time_point<chrono::system_clock> *initial = nullptr;
chrono::time_point<chrono::system_clock> *current = nullptr;
int count = 0;

int main(int argc, char* argv[]) {
    if(sample_rate > 0) inv_sample_rate = 1.0f / (float)sample_rate;

    // on-exit callback function
    on_exit(prgm_exit, nullptr);

    // parse GLUT arguments
    glutInit(&argc, argv);

    // parse program arguments
    if(!parseArguments(argc, argv))
        return 1;

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
    // is calculated as a total of the width/height of all display monitors.
    // Without the below, the result is a window with an aspect ratio stretched across multiple monitors.
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
    if(!isSerial && sample_rate > 0) glutTimerFunc((unsigned int)(inv_sample_rate * 1000.0f), timer, (unsigned int)(inv_sample_rate * 1000.0f));
    else {
        serial = new Serial();
        if(sample_rate == 0)
            glutIdleFunc(idle);
        else
            glutTimerFunc((unsigned int)(inv_sample_rate * 1000.0f), serial_timer, (unsigned int)(inv_sample_rate * 1000.0f));
    }

    // Start main loop
    glutMainLoop();
}

void idle(void) {
    std::string line = (*serial).read_data();
    std::stringstream stringstream(line);
    float data[dof];
    if(!line.empty()) {
        size_t i = 0;
        try {
            while(i < dof && stringstream >> data[i]) {
                i++;
            }
        }
        catch (std::ifstream::failure e) {
            std::cerr << e.what() << std::endl;
        }
        process_data(data);
    }
    glutPostRedisplay();
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
    glTranslatef(0.0f,-10.0f, -70.0f);

    // do rendering
    obj->render();
    if(debug) draw_vector(2.0f*glm::normalize(grav3) + obj->getPosition(), obj->getPosition());

    // flush and swap buffers
    glFlush();
    glutSwapBuffers();
}

void serial_timer(int value) {
    std::string line = (*serial).read_data();
    std::stringstream stringstream(line);
    float data[dof];
    if(!line.empty()) {
        size_t i = 0;
        try {
            while(i < dof && stringstream >> data[i]) {
                i++;
            }
        }
        catch (std::ifstream::failure e) {
            std::cerr << e.what() << std::endl;
        }
        process_data(data);
    }
    glutTimerFunc((unsigned int)value, serial_timer, value);
    glutPostRedisplay();
}

/*!
 * Timer callback function.
 * @param value - <code> unsigned int </code>
 */
void timer(int value) {
    float data[dof];
    float* p_data = data;
    if(readDataLine(&p_data)) {
        sample_count++;
        process_data(data);
    }
    glutTimerFunc((unsigned int)value, timer, value);
    glutPostRedisplay();
}

void process_data(float data[]) {
    count++;
    if(initial == nullptr) {
        initial = new chrono::system_clock::time_point;
        current = new chrono::system_clock::time_point;
        *initial = chrono::system_clock::now();
        *current = *initial;
    } else *current = chrono::system_clock::now();
    chrono::duration<float> time_diff = *current - *initial;
    float time_interval = inv_sample_rate;
    if(isSerial) time_interval = time_diff.count();
    // convert raw IMU accelerometer values & add to accelerometer time series
    glm::fvec3 a = glm::fvec3(0, 0, 0);
    int bit_width = (1 << adc_bit_width) - 1;
    glm::fvec3 acc_raw = glm::ivec3(data[0], data[2], data[1]);
    a.x = (data[0] - vzerogx) / sensitivity;
    a.y = (data[2] - vzerogy) / sensitivity;
    a.z = -(data[1] - vzerogz) / sensitivity;
    accTimeSeries.add(a);
    // convert raw IMU gyroscope values & add to gyroscope time series
    glm::fvec3 rot_euler = glm::fvec3(0, 0, 0);
    int k = (1 << adc_bit_width);
    rot_euler.x = ((data[3]) - vzerogx) / sensitivity;
    rot_euler.y = ((data[4]) - vzerogy) / sensitivity;
    rot_euler.z = ((data[5]) - vzerogz) / sensitivity;
    gyroTimeSeries.add(rot_euler);
    if(count > SERIES_SIZE) {
        // acceleration pre-processing
//        glm::fvec3 acceleration = accTimeSeries.calcEWMA();
        glm::fvec3 acceleration = accTimeSeries.calcEWMA();
        glm::fvec3 a_norm = glm::normalize(acceleration);
        if(glm::length(gravity) == 0.0f && count >= 10) {
            // Compute acceleration due to gravity.
            // Assumes IMU isn't moving in the first sample
            g_mag = glm::length(acceleration);
            gravity = glm::fvec4(acceleration, 1.0f);
        }
        // rotation pre-processing
        rot_euler = gyroTimeSeries.calcEWMA();
        rot_euler *= time_interval;
        glm::fquat rot = glm::fquat( rot_euler );
        // gravity
        glm::fmat4 grav_rot = glm::mat4_cast(glm::inverse(rot));
        glm::fmat4 rot_mat = glm::mat4_cast(rot);
        gravity = gravity * grav_rot * rot_mat;
        grav3 = -glm::fvec3(gravity);
        acceleration -= glm::fvec3(gravity);
        acceleration *= time_interval;
        // calculate velocity
        velocity = acceleration; // assumes velocity is initially zero
        // update 3D object's position and rotation
        obj->move(velocity);
        obj->rotate(rot);
        *initial = chrono::system_clock::now();
        if (debug) {
//          std::cout << a.x << " " << a.y << " " << a.z << std::endl;
//            std::cout << velocity.x << " " << velocity.y << " " << velocity.z << std::endl;
            std::cout << acceleration.x << " " << acceleration.y << " " << acceleration.z << " :: "
                      << acc_raw.x << " " << acc_raw.y << " " << acc_raw.z << std::endl;
            std::cout << rot_euler.x << " " << rot_euler.y << " " << rot_euler.z << std::endl;
        }
    }
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
                      << "   -d            Enables printing of debug information." << std::endl
                      << "   --serial      Enables reading from the serial port." << std::endl
                      << "   -i, --input   Set path to input file stream. When not" << std::endl
                      << "                   specified, the standard input is used" << std::endl
                      << "                   to support piping." << std::endl
                      << "   --dof         Set the degrees-of-freedom of the IMU. " << std::endl
                      << "                   Default is 9 DoF."
                      << "   --hz          Set the simulated sample rate in samples-" << std::endl
                      << "                   per-second. Ignored when reading from the" << std::endl
                      << "                   serial port. Default is 125.0 Hz." << std::endl;
            result = false;
        }
    }
    if(result) {
        // When help option not found, attempt to parse the arguments
        for(size_t i = 1; i < argc; i++) {
            if(argv[i][0] == '-') {
                std::string option(argv[i]);
                    std::string value;
                if(option.compare("-d") == 0) debug = true;
                else if(option.compare("--serial") == 0) isSerial = true;
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
                    } else if(option.compare("--dof") == 0) {
                        try {
                            dof = (unsigned short)std::stoi(value);
                            std::cout << "Degrees-of-freedom set to " << dof << "." << std::endl;
                            if(dof != 6 and dof != 9) {
                                std::cerr << "ERR: DoF must be either 9 or 6." << std::endl;
                                result = false;
                            }
                        } catch (std::invalid_argument e) {
                            std::cerr << "ERR: There must be a positive integer value following \'" << option << "\'." << std::endl;
                            result = false;
                        } catch (std::system_error e) {
                            std::cerr << e.what() << std::endl;
                            result = false;
                        }
                    } else if(option.compare("--imu") == 0) {
                        if(value.compare("sample01") == 0) {
                            dof = SAMPLE01_DOF;
                            adc_bit_width = SAMPLE01_ACC_BITWIDTH;
                            vref = SAMPLE01_ACC_VREF;
                            vzerogx = SAMPLE01_ACC_VZEROGX;
                            vzerogy = SAMPLE01_ACC_VZEROGY;
                            vzerogz = SAMPLE01_ACC_VZEROGZ;
                            sensitivity = SAMPLE01_ACC_SENSITIVITY;
                        } else if(value.compare("mpu6050") == 0) {
                            isSerial = true;
                            dof = MPU6050_DOF;
                            adc_bit_width = MPU6050_ACC_BITWIDTH;
                            vref = MPU6050_ACC_VREF;
                            vzerogx = MPU6050_ACC_VZEROGX;
                            vzerogy = MPU6050_ACC_VZEROGY;
                            vzerogz = MPU6050_ACC_VZEROGZ;
                            sensitivity = MPU6050_ACC_SENSITIVITY;
                        } else {
                            std::cerr << "ERR: Available options for IMU are: " << std::endl
                                      << "sample01" << std::endl
                                      << "mpu6050" << std::endl;
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
bool readDataLine(float * p_data[]) {
    float* data = *p_data;
    bool result = true;
    char buffer[1024];
    if(!std::cin.eof()) {
        std::cin.getline(buffer, 1024, delim);
        std::stringstream stringstream(buffer);
        int i = 0;
        try {
            while(i < dof && stringstream >> data[i]) i++;
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