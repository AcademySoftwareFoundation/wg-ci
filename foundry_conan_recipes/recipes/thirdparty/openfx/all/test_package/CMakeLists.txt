cmake_minimum_required(VERSION 3.20.0)
project(PackageTest CXX)

find_package(OFX CONFIG REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package PRIVATE OFX::OFX)
target_compile_features(test_package PRIVATE cxx_std_11)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)
