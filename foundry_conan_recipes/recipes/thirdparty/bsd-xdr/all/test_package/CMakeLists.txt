cmake_minimum_required(VERSION 3.20.0)
project(PackageTest CXX)

find_package(BSDXdr 1.0.0 CONFIG REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package BSDXdr::BSDXdr)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)

if (MSVC)
    target_compile_definitions(test_package PRIVATE _CRT_SECURE_NO_WARNINGS=1)
endif ()
