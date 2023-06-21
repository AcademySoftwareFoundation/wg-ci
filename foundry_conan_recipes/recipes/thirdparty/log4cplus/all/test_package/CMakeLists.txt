cmake_minimum_required(VERSION 3.1)
project(Log4cplusTest CXX)

find_package(Log4cplus REQUIRED)

add_executable(log4cplusTest log4cplusTest.cpp)
target_link_libraries(log4cplusTest
    PRIVATE
    Log4cplus::Log4cplus
)

enable_testing()
add_test(NAME log4cplusTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND log4cplusTest)
