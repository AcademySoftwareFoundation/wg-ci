#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(OpenVR CONFIG REQUIRED)

add_executable(OpenVRTest main.cpp)

target_link_libraries(OpenVRTest PRIVATE OpenVR::OpenVR)

enable_testing()

add_test(
    NAME
        openvr_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        OpenVRTest
)

if (WIN32)
    set_tests_properties(openvr_basic_test
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_OPENVR_ROOT}/lib\;$ENV{PATH}"
    )
endif()
