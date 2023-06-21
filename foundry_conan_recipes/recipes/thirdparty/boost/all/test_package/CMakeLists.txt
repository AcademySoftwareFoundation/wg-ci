# 3.13's FindBoost.cmake does not work properly with namespaced boost
cmake_minimum_required(VERSION 3.14.3)
project(PackageTest CXX)

# set in the conan recipe
set(PYTHON_VERSION "" CACHE STRING "Python version for finding it in CMake properly")

find_package(Boost COMPONENTS chrono serialization locale system ${Boost_PYTHON_COMPONENT} REQUIRED)

enable_testing()

add_executable(test_chrono example.cpp)
target_compile_definitions(test_chrono PRIVATE ${Boost_COMPILE_DEFINITIONS})
target_link_libraries(test_chrono PRIVATE Boost::chrono)

add_test(
    NAME test_chrono
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_chrono
)
if (Boost_USE_STATIC_LIBS STREQUAL "OFF" AND WIN32)
    set_tests_properties(test_chrono PROPERTIES ENVIRONMENT "PATH=${CONAN_BOOST_ROOT}/lib;$ENV{PATH}")
endif()

add_executable(test_scientific_notation scientific.cpp)
target_compile_definitions(test_scientific_notation PRIVATE ${Boost_COMPILE_DEFINITIONS})
target_link_libraries(test_scientific_notation PRIVATE Boost::serialization)

add_test(
    NAME test_scientific_notation
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_scientific_notation
)
if (Boost_USE_STATIC_LIBS STREQUAL "OFF" AND WIN32)
    set_tests_properties(test_scientific_notation PROPERTIES ENVIRONMENT "PATH=${CONAN_BOOST_ROOT}/lib;$ENV{PATH}")
endif()

add_executable(test_icu_disabled locale_icu_check.cpp)
target_compile_definitions(test_icu_disabled PRIVATE ${Boost_COMPILE_DEFINITIONS})
target_compile_features(test_icu_disabled PUBLIC cxx_std_11)
target_link_libraries(test_icu_disabled PRIVATE Boost::locale)
if(Boost_USE_STATIC_LIBS)
    # FindBoost.cmake does not list a dependency on system from locale, but this is necessary
    target_link_libraries(test_icu_disabled PRIVATE Boost::system)
    if(APPLE)
        # iconv is found during configuration, and locale uses it
        find_package(iconv REQUIRED)
        target_link_libraries(test_icu_disabled PRIVATE Iconv::Iconv)
    endif()
endif()

add_test(
    NAME test_icu_disabled
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_icu_disabled
)
if (Boost_USE_STATIC_LIBS STREQUAL "OFF" AND WIN32)
    set_tests_properties(test_icu_disabled PROPERTIES ENVIRONMENT "PATH=${CONAN_BOOST_ROOT}/lib;$ENV{PATH}")
endif()


if (NOT PYTHON_VERSION STREQUAL "")
    find_package(Python CONFIG REQUIRED COMPONENTS Interpreter Development)

    if (Python_VERSION_MAJOR EQUAL 3 AND CMAKE_BUILD_TYPE STREQUAL "Debug" AND Boost_VERSION STREQUAL "106600")
        message(WARNING "skipping Boost.Python module testing due to issues with Python3 and Boost 1.66.0")
        return()
    endif()

    Python_add_library(greetings MODULE greetings.cpp)
    target_compile_definitions(greetings PRIVATE ${Boost_COMPILE_DEFINITIONS})
    target_link_libraries(greetings PRIVATE Boost::${Boost_PYTHON_COMPONENT})
    
    add_test(
        NAME python_module
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMAND $<TARGET_FILE:Python::Interpreter> -v -B ${CMAKE_CURRENT_SOURCE_DIR}/check_python_module.py
    )
    set_tests_properties(python_module PROPERTIES ENVIRONMENT "PYTHONPATH=$<TARGET_FILE_DIR:greetings>")

    if (Boost_USE_STATIC_LIBS STREQUAL "OFF" AND WIN32)
        set_property(TEST python_module APPEND PROPERTY ENVIRONMENT "PATH=${CONAN_BOOST_ROOT}/lib;$ENV{PATH}")
    endif()
endif()
