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
add_executable(opengl-debugger opengl-debugger-utility.cpp ${SOURCE_FILES} ${HEADERS})
target_link_libraries(opengl-debugger -lGL -lglut)

set(SAMPLE_DATA_VIEWER_SOURCE
        "src/World Objects/Polygon.cpp"
        "src/World Objects/Vertex.cpp"
        "src/World Objects/WorldObject.cpp"
        "src/World Objects/Mesh.cpp"
        "src/World Objects/Axis.cpp"
        "src/Template Objects/TemplateObjects.cpp"
        "src/utility/MadgwickAHRS/MadgwickAHRS.cpp"
#        "src/utility/MahonyAHRS/MahonyAHRS.cpp"
        "src/utility/ahrs_common.h" src/utility/debug.cpp src/utility/debug.h)
add_executable(3d-viewer-utility 3d_viewer_utility.cpp ${SAMPLE_DATA_VIEWER_SOURCE})
target_link_libraries(3d-viewer-utility -lGL -lglut)

set(DATALOG_FILE_CONVERTER_SOURCE
        "src/utility/DatalogParser.cpp"
        "src/utility/DatalogReader.cpp")
add_executable(datalog-file-converter datalog_file_converter.cpp ${DATALOG_FILE_CONVERTER_SOURCE})