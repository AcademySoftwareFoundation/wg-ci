cmake_minimum_required(VERSION 3.1.0)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 14)

find_package(PortAudio REQUIRED)

add_executable(test_portaudio test_package.cpp)

target_link_libraries(test_portaudio PRIVATE PortAudio::PortAudio)

enable_testing()
add_test(
    NAME test_portaudio
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_portaudio
)

if (${shared_portaudio})
if (WIN32)
    set_tests_properties(test_portaudio
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_PORTAUDIO_ROOT}/bin;$ENV{PATH}"
    )
endif()
endif()
