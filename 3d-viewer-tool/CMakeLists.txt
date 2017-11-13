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
add_executable(3d-viewer-tool main.cpp ${SOURCE_FILES} ${HEADERS})
target_link_libraries(3d-viewer-tool -lGL -lglut)

set(SAMPLE_DATA_VIEWER_SOURCE
        "src/World Objects/Polygon.cpp"
        "src/World Objects/Vertex.cpp"
        "src/World Objects/WorldObject.cpp"
        "src/World Objects/Mesh.cpp"
        "src/World Objects/Axis.cpp"
        "src/Template Objects/TemplateObjects.cpp"
        "src/utility/MadgwickAHRS/MadgwickAHRS.cpp"
#        "src/utility/MahonyAHRS/MahonyAHRS.cpp"
        "src/utility/ahrs_common.h")
add_executable(sample-data-utility sample_data_utility.cpp ${SAMPLE_DATA_VIEWER_SOURCE})
target_link_libraries(sample-data-utility -lGL -lglut)

set(DATALOG_FILE_CONVERTER_SOURCE
        "src/utility/DatalogParser.cpp"
        "src/utility/DatalogReader.cpp")
add_executable(datalog-file-converter datalog_file_converter.cpp ${DATALOG_FILE_CONVERTER_SOURCE})