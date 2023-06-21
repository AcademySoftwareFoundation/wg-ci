cmake_minimum_required(VERSION 3.0)
project(PackageTest LANGUAGES C)

find_package(Fontconfig REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_package test_package.c)
target_link_libraries(test_package
    PRIVATE
        Fontconfig::Fontconfig
)

enable_testing()
add_test(NAME test_package
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_package
)
