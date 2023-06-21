cmake_minimum_required(VERSION 3.0)

project(OpenTimelineIOTest CXX)

find_package(OpenTime CONFIG REQUIRED)
find_package(OpenTimelineIO CONFIG REQUIRED)
find_package(Imath CONFIG)

add_executable(test_otio test_package.cpp)
target_link_libraries(test_otio PRIVATE OTIO::opentimelineio OTIO::opentime)
target_compile_features(test_otio PRIVATE cxx_std_14)

enable_testing()
add_test(
    NAME test_otio
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_otio
)

if(WIN32)
    if(shared)
        set_tests_properties(test_otio PROPERTIES ENVIRONMENT "PATH=${OTIO_SHARED_LIBRARY_DIR}\;$ENV{PATH}")
    endif()
endif()

add_test(
    NAME test_otiopy
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND ${CONAN_PYTHON_INTERPRETER} -v -B ${CMAKE_CURRENT_LIST_DIR}/check_otio.py
)
if(WIN32)
    set_tests_properties(test_otiopy PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${PYTHON_PATH_FOR_MODULES};PATH=${OTIO_SHARED_LIBRARY_DIR}\;$ENV{PATH}")
elseif (APPLE)
    set_tests_properties(test_otiopy PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${PYTHON_PATH_FOR_MODULES};DYLD_LIBRARY_PATH=${CONAN_IMATH_ROOT}/lib:$ENV{DYLD_LIBRARY_PATH}")
else()
    set_tests_properties(test_otiopy PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${PYTHON_PATH_FOR_MODULES};LD_LIBRARY_PATH=${CONAN_IMATH_ROOT}/lib:$ENV{LD_LIBRARY_PATH}")
endif()
