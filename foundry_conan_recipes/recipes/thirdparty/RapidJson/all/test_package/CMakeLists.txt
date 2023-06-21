project(RapidJsonTest CXX)
cmake_minimum_required(VERSION 3.0)

find_package(RapidJson CONFIG REQUIRED)

add_executable(test_RapidJson test_package.cpp)
target_link_libraries(test_RapidJson RapidJson::RapidJson)

enable_testing()
add_test(NAME test_RapidJson
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_RapidJson
)
