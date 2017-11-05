cmake_minimum_required(VERSION 3.7)
project(3d-viewer-tool)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES main.cpp Polygon.cpp Vertex.cpp WorldObject.cpp)
add_executable(3d-viewer-tool.exe ${SOURCE_FILES})
target_link_libraries(3d-viewer-tool.exe -lGL -lglut)
