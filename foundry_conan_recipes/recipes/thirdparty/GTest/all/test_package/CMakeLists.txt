cmake_minimum_required(VERSION 3.10.0)
project(PackageTest C CXX)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(GTest REQUIRED CONFIG)

enable_testing()
add_executable(test_gmock test_gtest_and_gmock.cpp)
target_link_libraries(test_gmock PRIVATE GTest::gtest GTest::gmock)
add_test(
    NAME test_gmock
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_gmock
)
if (${shared_gtest})
    if (MSVC)
        set_tests_properties(test_gmock
            PROPERTIES
            ENVIRONMENT "PATH=${CONAN_GTEST_ROOT}/bin;$ENV{PATH}"
        )
    endif()
endif()