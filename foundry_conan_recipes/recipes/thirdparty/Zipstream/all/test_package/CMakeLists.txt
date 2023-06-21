cmake_minimum_required(VERSION 3.1)
project(TestPackage)

find_package(Zipstream CONFIG REQUIRED)

add_executable(ZipstreamTest main.cpp)
target_link_libraries(ZipstreamTest
    PRIVATE
        Zipstream::Zipstream
)

enable_testing()
add_test(
    NAME
        zipstream_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        ZipstreamTest
)
