#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(msgpack-cxx CONFIG REQUIRED)

add_executable(MessagePackTest main.cpp)

target_link_libraries(MessagePackTest PRIVATE
    msgpack-cxx::msgpack-cxx
)

enable_testing()

add_test(
    NAME
        msgpack_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        MessagePackTest
)
