#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(sse2neon CONFIG REQUIRED)

if(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "x86_64" OR ${CMAKE_SYSTEM_PROCESSOR} STREQUAL "i386")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -maes -mpclmul -mssse3 -msse4.2")
elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "aarch64" OR ${CMAKE_SYSTEM_PROCESSOR} STREQUAL "arm64")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv8-a+fp+simd+crc")
elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "armv7l" OR ${CMAKE_SYSTEM_PROCESSOR} STREQUAL "arm")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mfpu=neon")
else()
    message(FATAL_ERROR "Unsupported architecture")
endif()

add_executable(Sse2NeonTest
    binding.cpp
    common.cpp
    impl.cpp
    main.cpp
)

target_compile_features(Sse2NeonTest
    PRIVATE
        cxx_std_14
)

target_compile_options(Sse2NeonTest
    PRIVATE
        -Wall -Wcast-qual
)

target_link_libraries(Sse2NeonTest PRIVATE
    sse2neon::sse2neon
)

enable_testing()

add_test(
    NAME
        sse2neon_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        Sse2NeonTest
)
