#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(MuParser CONFIG REQUIRED)

add_executable(MuParserTest main.cpp)

target_link_libraries(MuParserTest MuParser::MuParser)

enable_testing()

add_test(
    NAME
        muparser_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        MuParserTest
)

if(WIN32 AND ${shared_muparser})
    set_tests_properties(muparser_basic_test PROPERTIES ENVIRONMENT "PATH=${CONAN_MUPARSER_ROOT}/bin;$ENV{PATH}")
endif()
