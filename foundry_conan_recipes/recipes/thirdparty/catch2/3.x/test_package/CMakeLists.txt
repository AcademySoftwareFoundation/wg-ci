cmake_minimum_required(VERSION 3.0.0)
project(PackageTest)

find_package(Catch2 CONFIG REQUIRED)

add_executable(test_package test.cxx)

target_link_libraries(test_package PRIVATE Catch2::Catch2WithMain)

enable_testing()
add_test(
  NAME test_package
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMAND test_package)
if(${shared_catch2})
  if(MSVC)
    set_tests_properties(
      test_package PROPERTIES ENVIRONMENT
                              "PATH=${CONAN_CATCH2_ROOT}/lib;$ENV{PATH}")
  endif()
endif()
