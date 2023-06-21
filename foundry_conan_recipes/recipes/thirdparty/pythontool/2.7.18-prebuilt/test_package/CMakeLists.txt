cmake_minimum_required(VERSION 3.10)
project(PackageTest LANGUAGES C)

set(CONAN_PYTHON_VERSION "" CACHE STRING "Python version from conan")
if (NOT CONAN_PYTHON_VERSION)
    message(FATAL_ERROR "Conan version has not been specified.")
endif()


find_package(Python CONFIG REQUIRED COMPONENTS Interpreter Development)

Python_add_library(greetings MODULE greetings.c)

message(STATUS "Python executable testing is '${Python_EXECUTABLE}'")
if (NOT "${Python_EXECUTABLE}" STREQUAL "${CONAN_PYTHON_INTERPRETER}")
    message(FATAL_ERROR "Conan's user_info.interpreter (${CONAN_PYTHON_INTERPRETER}) doesn't match with found python (${Python_EXECUTABLE})")
endif()

set(PYHOME ${CONAN_PYHOME})

# only to show the sys.version in the test log
execute_process(
    COMMAND ${CMAKE_COMMAND} -E env "PYTHONHOME=${PYHOME}" ${Python_EXECUTABLE} -B -c "import sys; print('Testing Python version {}').format(sys.version)"
)

enable_testing()

macro(add_python_test CASE_NAME SCRIPT_FILE)
    # ignores user site for testing, so that machine setup is not influencing tests
    add_test(
        NAME ${CASE_NAME}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMAND $<TARGET_FILE:Python::Interpreter> -v -B -s ${CMAKE_CURRENT_SOURCE_DIR}/${SCRIPT_FILE}
    )
    set_tests_properties(${CASE_NAME} PROPERTIES ENVIRONMENT "PYTHONHOME=${PYHOME}")
endmacro()


add_python_test(no_readline_available_because_its_gpl check_no_gpl_readline.py)
add_python_test(no_lzma_available check_no_lzma.py)
add_python_test(ssl_hashlib_modules_work check_ssl_hashlib.py)
add_python_test(sqlite_module_works check_sqlite.py)
add_python_test(zlib_module_works check_zlib.py)
add_python_test(bz2_module_works check_bz2.py)
add_python_test(setuptools_is_available check_setuptools.py)
add_python_test(pip_is_available check_pip.py)
add_python_test(python_version_not_dirty check_for_dirty_version_number.py)

add_python_test(custom_module_works check_greetings.py)
set_tests_properties(custom_module_works
    PROPERTIES
        ENVIRONMENT "PYTHONPATH=$<TARGET_FILE_DIR:greetings>"
)
