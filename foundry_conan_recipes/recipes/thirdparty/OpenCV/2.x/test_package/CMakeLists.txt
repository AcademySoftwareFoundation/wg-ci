cmake_minimum_required(VERSION 3.1)
project(OpenCVTest CXX)

find_package(OpenCV REQUIRED)

add_executable(OpenCVTest example.cpp)
target_link_libraries(OpenCVTest
    PRIVATE
    opencv_core
    opencv_imgproc
)

enable_testing()
add_test(NAME OpenCVTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND OpenCVTest)

if (shared_opencv)
    if (MSVC)
        set_tests_properties(OpenCVTest PROPERTIES ENVIRONMENT "PATH=${CONAN_OPENCV_ROOT}/bin;$ENV{PATH}")
    elseif (APPLE)
        set_tests_properties(OpenCVTest PROPERTIES ENVIRONMENT "DYLD_LIBRARY_PATH=${CONAN_OPENCV_ROOT}/lib;$ENV{DYLD_LIBRARY_PATH}")
    endif ()
endif ()
