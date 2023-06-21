#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)

project(fakeit_test)

find_package(FakeIt CONFIG REQUIRED)

add_executable(fakeit_test main.cpp)

target_compile_features(fakeit_test PRIVATE cxx_std_14)

target_link_libraries(fakeit_test PRIVATE FakeIt::FakeIt)

enable_testing()

add_test(
  NAME fakeit_test
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMAND fakeit_test)
