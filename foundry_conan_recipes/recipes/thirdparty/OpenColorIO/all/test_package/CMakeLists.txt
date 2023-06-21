cmake_minimum_required(VERSION 3.13)
project(PackageTest)

set(CMAKE_CXX_STANDARD 14)

find_package(OpenColorIO REQUIRED)
add_executable(ConfigTest test_library_v3.cpp)
target_compile_definitions(ConfigTest PRIVATE -DOCIO_CONFIGURED_VERSION="${ocio_configured_version}")

target_link_libraries(ConfigTest PRIVATE OCIO::OCIO)

enable_testing()
add_test(
    NAME load_config_into_cpp_application
    COMMAND ConfigTest
    WORKING_DIRECTORY ${CONAN_OPENCOLORIOCONFIGS_ROOT}/configs
)
if (MSVC)
    set_tests_properties(load_config_into_cpp_application
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_OPENCOLORIO_ROOT}/bin;$ENV{PATH}"
    )
endif()

# TODO: PyOpenColorIO requires to be placed in the RPATH, which is problematic with the stock Python

# find_package(Python CONFIG REQUIRED COMPONENTS Interpreter)
# 
# macro(add_python_test CASE_NAME SCRIPT_FILE)
#     add_test(
#         NAME ${CASE_NAME}
#         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
#         COMMAND $<TARGET_FILE:Python::Interpreter> -v -B ${CMAKE_CURRENT_SOURCE_DIR}/${SCRIPT_FILE}
#     )
#     set_tests_properties(${CASE_NAME} PROPERTIES ENVIRONMENT "PYTHONHOME=${PYHOME}")
# endmacro()
# 
# add_python_test(check_pyglue_module check_pyglue.py)
# set_tests_properties(check_pyglue_module
#     PROPERTIES
#         ENVIRONMENT "PYTHONPATH=${CONAN_OPENCOLORIO_ROOT}/lib"
# )
