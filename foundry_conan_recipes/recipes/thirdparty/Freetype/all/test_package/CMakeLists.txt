cmake_minimum_required(VERSION 3.0)
project(PackageTest LANGUAGES C)

find_package(Freetype REQUIRED)

add_executable(test_package test_package.c)
set_target_properties(test_package
    PROPERTIES
    C_STANDARD 99
)
target_link_libraries(test_package
    PRIVATE
        Freetype::Freetype
)
target_compile_definitions(test_package
 PRIVATE
  -DEXAMPLE_FONT_FILE="${CMAKE_EXAMPLE_FONT_FILE}"
)

enable_testing()
add_test(NAME test_package
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_package
)
