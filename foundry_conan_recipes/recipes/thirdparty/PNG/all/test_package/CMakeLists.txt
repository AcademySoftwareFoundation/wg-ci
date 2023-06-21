cmake_minimum_required(VERSION 3.0.0)
project(PackageTest C)

find_package(PNG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_libpng test_package.c)
target_link_libraries(test_libpng PNG::PNG)

enable_testing()
add_test(NAME test_libpng
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_libpng)

