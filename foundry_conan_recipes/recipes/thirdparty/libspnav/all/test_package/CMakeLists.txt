#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(SpaceNav CONFIG REQUIRED)

add_executable(SpNavTest main.cpp)

target_link_libraries(SpNavTest PRIVATE SpaceNav::SpaceNav)

enable_testing()

add_test(
    NAME
        spacenav_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        SpNavTest
)
