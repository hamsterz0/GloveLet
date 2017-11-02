cmake_minimum_required(VERSION 3.7)
project(glut_test)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES main.cpp)
add_executable(glut_test.exe ${SOURCE_FILES})
target_link_libraries(glut_test.exe -lGL -lglut)
