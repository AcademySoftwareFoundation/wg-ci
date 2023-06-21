cmake_minimum_required(VERSION 3.3.0)
project(PackageTest CXX)

option(RUN_PYTHON_BINDINGS_TESTS "Set to \"ON\" to run tests for MaterialX's Python bindings." OFF)
find_package(MaterialX REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_materialx test_package.cpp)
set_target_properties(test_materialx PROPERTIES CXX_STANDARD 11)
target_link_libraries(test_materialx MaterialXCore)

enable_testing()
add_test(NAME test_materialx
         COMMAND test_materialx)

if (RUN_PYTHON_BINDINGS_TESTS)
    find_package(OpenColorIO REQUIRED)
    find_package(Python CONFIG EXACT REQUIRED COMPONENTS Interpreter Development)

    set(PYHOME ${CONAN_PYTHON_ROOT})
    if (APPLE)
        set(PYHOME ${CONAN_PYTHON_ROOT}/Python.framework/Versions/Current)
    endif()

    macro(add_python_test CASE_NAME SCRIPT_FILE)
        add_test(
            NAME ${CASE_NAME}
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
            COMMAND $<TARGET_FILE:Python::Interpreter> -s ${CMAKE_CURRENT_SOURCE_DIR}/${SCRIPT_FILE} ${ARGN}
        )

        if (WIN32)
            set(PYPATH "${CONAN_MATERIALX_ROOT}/python\;$ENV{PYTHONPATH}")
        else()
            set(PYPATH "${CONAN_MATERIALX_ROOT}/python:$ENV{PYTHONPATH}")
        endif()
        set_tests_properties(${CASE_NAME} PROPERTIES ENVIRONMENT "PYTHONHOME=${PYHOME};PYTHONPATH=${PYPATH}")
    endmacro()

    add_python_test(bindings_and_ocio_test test_bindings_and_ocio.py)
endif()
