cmake_minimum_required(VERSION 3.0.0)
project(PackageTest)

find_package(Catch2 CONFIG REQUIRED)

add_executable(test_package test.cxx)

target_link_libraries(test_package PRIVATE Catch2::Catch2)

# Let Catch2 provide `main` implementation.
set_property(SOURCE test.cxx PROPERTY COMPILE_DEFINITIONS "CATCH_CONFIG_MAIN")

enable_testing()
add_test(
  NAME test_package
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMAND test_package)
