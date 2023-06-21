cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED)

find_package(Flatbuffers CONFIG REQUIRED)
include(BuildFlatBuffers)

build_flatbuffers(${CMAKE_SCHEMA_FILE} "" FlatBuffersTarget "" "${CMAKE_CURRENT_BINARY_DIR}" "" "" "")

add_executable(test_package
  test_package.cpp
)
target_link_libraries(test_package
  PRIVATE
    flatbuffers::flatbuffers
)
target_compile_definitions(test_package
  PRIVATE
    -DSCHEMA_FILE="${CMAKE_SCHEMA_FILE}"
)
add_dependencies(test_package
  FlatBuffersTarget
)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)
