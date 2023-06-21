cmake_minimum_required(VERSION 3.15)
project(pybind11Test CXX)

find_package(Python CONFIG REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

pybind11_add_module(Pybind11TestModule test_module.cpp)

set_target_properties(Pybind11TestModule PROPERTIES DEBUG_POSTFIX "${_LIB_DEBUG_POSTFIX}")

enable_testing()
add_test(NAME python_module
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND $<TARGET_FILE:Python::Interpreter> -v -B ${CMAKE_CURRENT_SOURCE_DIR}/test_python.py
)
set_tests_properties(python_module PROPERTIES ENVIRONMENT "PYTHONPATH=$<TARGET_FILE_DIR:Pybind11TestModule>")
