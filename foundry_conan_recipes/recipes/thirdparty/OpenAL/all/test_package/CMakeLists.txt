#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(OpenAL CONFIG REQUIRED)

add_executable(OpenALTest main.cpp)
target_compile_features(OpenALTest PRIVATE cxx_std_11)

target_link_libraries(OpenALTest PRIVATE
    OpenAL::OpenAL
)

enable_testing()

add_test(
    NAME
        openal_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        OpenALTest
)

if (WIN32)
    set_tests_properties(openal_basic_test
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_OPENAL_ROOT}/bin\;$ENV{PATH}"
    )
endif()
