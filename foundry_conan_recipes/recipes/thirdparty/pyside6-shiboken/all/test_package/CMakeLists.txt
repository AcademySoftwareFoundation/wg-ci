cmake_minimum_required(VERSION 3.13)

project(PackageTest)

find_program(
    shiboken
    NAME
        shiboken6.exe
    PATHS
        ${CONAN_PYSIDE6-SHIBOKEN_ROOT}/bin
    REQUIRED
)
message(STATUS "Found shiboken executable at ${shiboken}")

enable_testing()

add_test(
    NAME run_shiboken
    COMMAND ${shiboken} --version
)
