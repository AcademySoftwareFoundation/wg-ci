cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(OpenMP REQUIRED)

add_executable(test_openmp test_package.cpp)
target_link_libraries(test_openmp OpenMP::OpenMP_CXX)

enable_testing()
add_test(
    NAME test_openmp
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_openmp
)
