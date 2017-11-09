cmake_minimum_required(VERSION 3.7)
project(3d-viewer-tool)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES main.cpp "src/World Objects/Polygon.cpp" "src/World Objects/Vertex.cpp" "src/World Objects/WorldObject.cpp" "src/World Objects/Mesh.cpp" "src/World Objects/Mesh.h")
set(HEADERS "src/World Objects/WorldObject.h" "src/Template Objects/TemplateObjects.cpp" "src/Template Objects/TemplateObjects.h")
include_directories(./lib)
#add_library(MODULE lib/Polygon.h lib/WorldObject.h)
add_executable(3d-viewer-tool.exe ${SOURCE_FILES} ${HEADERS})
target_link_libraries(3d-viewer-tool.exe -lGL -lglut)
