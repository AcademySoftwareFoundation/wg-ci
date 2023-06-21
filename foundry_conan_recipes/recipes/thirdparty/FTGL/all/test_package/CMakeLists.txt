cmake_minimum_required(VERSION 3.0.0)
project(PackageTest LANGUAGES CXX)

find_package(FTGL CONFIG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
find_package(FoundryGL QUIET)

add_executable(test_package
  test_package.cpp
)
target_link_libraries(test_package
  PRIVATE
    FTGL::FTGL
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

if(APPLE AND FOUNDRYGL_FOUND)
  set_tests_properties(test_package PROPERTIES ENVIRONMENT "DYLD_LIBRARY_PATH=${FOUNDRYGL_LIBRARY_DIR}")
endif()

