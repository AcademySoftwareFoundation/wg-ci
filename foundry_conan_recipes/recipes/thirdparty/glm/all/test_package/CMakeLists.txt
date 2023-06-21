#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(glm CONFIG REQUIRED PATH_SUFFIXES "glm")

add_executable(GlmTest main.cpp)

target_link_libraries(GlmTest PRIVATE
    glm::glm
)

enable_testing()

add_test(
    NAME
        glm_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        GlmTest
)
