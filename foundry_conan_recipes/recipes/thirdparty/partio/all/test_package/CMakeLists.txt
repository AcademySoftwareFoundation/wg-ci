cmake_minimum_required(VERSION 3.20)

project(TestPackage CXX)

find_package(Partio REQUIRED)

add_executable(testapp)
target_sources(testapp PRIVATE example.cpp)

target_link_libraries(testapp PRIVATE Partio::Partio)

enable_testing()
add_test(NAME testapp COMMAND testapp)
