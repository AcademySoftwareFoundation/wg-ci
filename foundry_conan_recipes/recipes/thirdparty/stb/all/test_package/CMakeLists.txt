cmake_minimum_required(VERSION 3.0)
project(StbTestPackage C)

find_package(stb REQUIRED)

add_executable(test_stb test_package.c)
target_link_libraries(test_stb stb::stb)

enable_testing()
add_test(NAME test_stb
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMAND test_stb)
