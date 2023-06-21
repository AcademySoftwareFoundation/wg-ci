cmake_minimum_required(VERSION 3.13)
project(PackageTest CXX)

find_package(OpenColorIO REQUIRED)

add_executable(test_package test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_17)
target_link_libraries(test_package PRIVATE OCIO::OCIO)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CONAN_OPENCOLORIOCONFIGACES_ROOT}/configs
         COMMAND test_package)

