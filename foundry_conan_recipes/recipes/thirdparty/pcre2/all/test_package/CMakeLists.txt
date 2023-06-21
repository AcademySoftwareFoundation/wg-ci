cmake_minimum_required(VERSION 3.20.0)
project(PackageTest CXX)

find_package(PCRE2 CONFIG REQUIRED COMPONENTS 8BIT)

add_executable(test_package main.cpp)
target_link_libraries(test_package PCRE2::8BIT)
target_compile_features(test_package PRIVATE cxx_std_11)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)

if (WIN32)
    if (${shared_pcre2})
        set_tests_properties(test_package PROPERTIES ENVIRONMENT "PATH=${CONAN_PCRE2_ROOT}/bin\;$ENV{PATH}")
    endif()
endif()
