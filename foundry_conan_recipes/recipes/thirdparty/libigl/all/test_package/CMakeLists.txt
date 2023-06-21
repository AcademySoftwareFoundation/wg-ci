#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.16.0)
project(TestPackage)

find_package(Igl CONFIG REQUIRED)

add_executable(IglTest main.cpp)

target_link_libraries(IglTest
    PRIVATE
        Igl::Igl
)

enable_testing()

add_test(
    NAME
        igl_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        IglTest
)
