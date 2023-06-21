#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(mDNSResponder CONFIG REQUIRED)

add_executable(mDNSResponderTest main.cpp)

target_link_libraries(mDNSResponderTest PRIVATE
    mDNSResponder::mDNSResponder
)

enable_testing()

add_test(
    NAME
        mDNSResponder_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        mDNSResponderTest
)

if (WIN32)
    set_tests_properties(mDNSResponder_basic_test
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_MDNSRESPONDER_ROOT}/bin\;$ENV{PATH}"
    )
endif()
