cmake_minimum_required(VERSION 3.20)

project(TestPackage CXX)

find_package(PoissonRecon REQUIRED)

add_library(lib SHARED)
target_sources(lib PRIVATE lib.cpp)
target_link_libraries(lib PRIVATE PoissonRecon::PoissonRecon)

add_executable(testapp)
target_sources(testapp PRIVATE example.cpp)

target_link_libraries(testapp PRIVATE lib)

enable_testing()
add_test(NAME testapp
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND testapp)

if (WIN32)
    set_tests_properties(testapp
        PROPERTIES ENVIRONMENT "PATH=${CONAN_POISSONRECON_ROOT}/lib\;$ENV{PATH}"
    )
endif()