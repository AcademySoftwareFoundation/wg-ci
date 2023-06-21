cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(fmt CONFIG REQUIRED)

add_executable(test_package
  test_package.cpp
)
target_link_libraries(test_package PRIVATE fmt::fmt)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)
