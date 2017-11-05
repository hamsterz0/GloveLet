cmake_minimum_required(VERSION 3.7)
project(3d-viewer-tool)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES main.cpp src/Polygon.cpp src/Vertex.cpp src/WorldObject.cpp src/Model.cpp src/Model.h)
set(HEADERS src/Polygon.h src/WorldObject.h)
include_directories(./lib)
#add_library(MODULE lib/Polygon.h lib/WorldObject.h)
add_executable(3d-viewer-tool.exe ${SOURCE_FILES} ${HEADERS})
target_link_libraries(3d-viewer-tool.exe -lGL -lglut)
