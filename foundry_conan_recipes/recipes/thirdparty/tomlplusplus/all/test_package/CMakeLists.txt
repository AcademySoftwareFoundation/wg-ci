cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(tomlplusplus REQUIRED CONFIG)

add_executable(TomlplusplusTest test_package.cpp)
target_link_libraries(TomlplusplusTest PRIVATE tomlplusplus::tomlplusplus)

enable_testing()

add_test(
    NAME
    tomlplusplus_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
    TomlplusplusTest ${CMAKE_CURRENT_LIST_DIR}/configuration.toml
)
