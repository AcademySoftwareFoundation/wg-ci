cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(range-v3 CONFIG REQUIRED)

add_executable(test_package test.cpp)
target_compile_features(test_package PRIVATE cxx_std_17)

target_link_libraries(test_package PRIVATE range-v3)

enable_testing()
add_test(
  NAME test_package
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMAND test_package)
