#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(Eigen3 CONFIG REQUIRED)

add_executable(EigenTest main.cpp)

target_compile_definitions(EigenTest PRIVATE EIGEN_MPL2_ONLY)
target_compile_features(EigenTest PRIVATE cxx_std_14)

target_link_libraries(EigenTest PRIVATE Eigen3::Eigen)

enable_testing()

add_test(
    NAME
        eigen_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        EigenTest
)
