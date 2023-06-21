cmake_minimum_required(VERSION 3.12)
project(PackageTest)

find_package(CUPTI CONFIG REQUIRED)

add_executable(test_cupti main.cpp)
target_link_libraries(test_cupti PRIVATE CUPTI::cupti)

enable_testing()
add_test(
    NAME test_cupti
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_cupti
)

if (WIN32)
  set_tests_properties(test_cupti PROPERTIES
    ENVIRONMENT "PATH=${CONAN_CUPTI_ROOT}/lib64;$ENV{PATH}")
endif()
