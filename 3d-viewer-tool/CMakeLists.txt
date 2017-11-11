cmake_minimum_required(VERSION 3.7)
project(3d-viewer-tool)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        "src/World Objects/Polygon.cpp"
        "src/World Objects/Vertex.cpp"
        "src/World Objects/WorldObject.cpp"
        "src/World Objects/Mesh.cpp"
        "src/World Objects/Axis.cpp"
        "src/Template Objects/TemplateObjects.cpp")
set(HEADERS
        "src/World Objects/WorldObject.h"
        "src/World Objects/Axis.h"
        "src/World Objects/Mesh.h"
        "src/Template Objects/TemplateObjects.h")
#add_library(MODULE lib/Polygon.h lib/WorldObject.h)
add_executable(3d-viewer-tool.exe main.cpp ${SOURCE_FILES} ${HEADERS})
target_link_libraries(3d-viewer-tool.exe -lGL -lglut)
add_executable(sample-data-utility.exe sample-data-utility.cpp ${SOURCE_FILES} ${HEADERS})
target_link_libraries(sample-data-utility.exe -lGL -lglut)
