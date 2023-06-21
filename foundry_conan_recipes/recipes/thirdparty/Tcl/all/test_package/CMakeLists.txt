cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(TCL REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_tcl example.cpp)
target_link_libraries(test_tcl PRIVATE TCL::TCL)

if (APPLE)
    set_property(
        TARGET test_tcl
        APPEND PROPERTY
        BUILD_RPATH "${CONAN_TCL_ROOT}/lib"
    )
endif()

enable_testing()
add_test(
    NAME test_tcl
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_tcl
)
if (WIN32)
    set_tests_properties(test_tcl PROPERTIES ENVIRONMENT "PATH=${CONAN_TCL_ROOT}/bin;$ENV{PATH}")
endif()
