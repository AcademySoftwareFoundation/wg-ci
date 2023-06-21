cmake_minimum_required(VERSION 3.22)
project(test_package)

find_package(nlohmann_json REQUIRED CONFIG)

add_executable(nlohmann_json_test test_package.cpp)
target_link_libraries(nlohmann_json_test PRIVATE nlohmann_json::nlohmann_json)
set_target_properties(nlohmann_json_test PROPERTIES CXX_STANDARD 11)

enable_testing()
add_test(
    NAME nlohmann_json_test
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND nlohmann_json_test
)
