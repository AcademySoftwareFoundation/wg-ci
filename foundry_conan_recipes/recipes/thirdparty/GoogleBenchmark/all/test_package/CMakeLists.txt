cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED)

find_package(benchmark CONFIG REQUIRED)

add_executable(test_package
  test_package.cpp
)
target_link_libraries(test_package PRIVATE benchmark::benchmark)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)
