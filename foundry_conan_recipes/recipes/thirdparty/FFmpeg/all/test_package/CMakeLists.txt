cmake_minimum_required(VERSION 3.10.0)
project(PackageTest C)

find_package(FFmpeg REQUIRED)

add_executable(test_ffmpeg test_package.c)
target_link_libraries(test_ffmpeg PRIVATE FFmpeg::avformat)

enable_testing()
add_test(
    NAME test_ffmpeg
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_ffmpeg
)

# test that ffmpeg tool is available and working
add_test(NAME ffmpeg_tool_found COMMAND FFmpeg::ffmpeg -version)

if (WIN32)
  set_tests_properties(test_ffmpeg PROPERTIES ENVIRONMENT "PATH=${CONAN_FFMPEG_ROOT}/bin/;$ENV{PATH}")
endif()

