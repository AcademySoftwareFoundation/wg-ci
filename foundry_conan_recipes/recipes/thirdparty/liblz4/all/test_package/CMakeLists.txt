#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(LZ4 CONFIG REQUIRED)

add_executable(Lz4Test main.cpp)

target_link_libraries(Lz4Test PRIVATE lz4::lz4)

enable_testing()

add_test(
    NAME
        lz4_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        Lz4Test
)

if(WIN32 AND ${shared_lz4})
    set_tests_properties(lz4_basic_test PROPERTIES ENVIRONMENT "PATH=${CONAN_LIBLZ4_ROOT}/bin;$ENV{PATH}")
endif()
