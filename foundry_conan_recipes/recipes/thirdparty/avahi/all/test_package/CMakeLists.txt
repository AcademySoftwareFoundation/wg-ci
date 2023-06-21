#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(Avahi CONFIG REQUIRED)

add_executable(AvahiTest
    main.cpp
)

target_link_libraries(AvahiTest
    PRIVATE
        Avahi::Common
        Avahi::Client
        Avahi::Qt5
)

enable_testing()

add_test(
    NAME
        avahi_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        AvahiTest
)
