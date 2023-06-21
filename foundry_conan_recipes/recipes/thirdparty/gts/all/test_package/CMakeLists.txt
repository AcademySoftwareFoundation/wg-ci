cmake_minimum_required(VERSION 3.13.0)
project(PackageTest LANGUAGES C)

find_package(GTS CONFIG REQUIRED)

add_executable(test_package main.c)
target_link_libraries(test_package PRIVATE GTS::GTS)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)

if (WIN32)
    set_tests_properties(test_package PROPERTIES ENVIRONMENT "PATH=${CONAN_GTS_ROOT}/lib\;${CONAN_GLIB_ROOT}/bin\;$ENV{PATH}")
endif()
