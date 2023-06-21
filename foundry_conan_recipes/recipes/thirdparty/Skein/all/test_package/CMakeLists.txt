cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX C)
set(CMAKE_CXX_STANDARD 11)
set(CXX_STANDARD_REQUIRED ON)

find_package(Skein CONFIG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_package
  test_package.cpp
  SHA3api_ref.c
)
target_link_libraries(test_package PRIVATE Skein::Skein)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)
