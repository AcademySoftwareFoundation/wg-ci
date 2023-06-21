cmake_minimum_required(VERSION 3.1)
project(JemallocTest CXX)

find_package(jemalloc REQUIRED)

add_executable(jemallocTest jemallocTest.cpp)
target_link_libraries(jemallocTest
    PRIVATE
    jemalloc::jemalloc
)

enable_testing()
add_test(NAME jemallocTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND jemallocTest)

if (MSVC)
  set_tests_properties(jemallocTest PROPERTIES ENVIRONMENT "PATH=${CONAN_JEMALLOC_ROOT}/lib;$ENV{PATH}")
endif()
