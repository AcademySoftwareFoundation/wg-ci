cmake_minimum_required(VERSION 3.10)

project(grpc_test VERSION 1.0 LANGUAGES CXX)

find_package(gRPC REQUIRED)

add_executable(
    grpc_test
    grpc.cpp
)

target_link_libraries(
    grpc_test
    PRIVATE
    gRPC::grpc
)

enable_testing()

add_test(
    NAME grpc_test
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND grpc_test
)
