#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_SKIP_BUILD_RPATH TRUE)

find_package(embree ${EMBREE_VERSION} EXACT CONFIG REQUIRED)
find_package(TBB COMPONENTS tbb REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(EmbreeTest main.cpp)

target_link_libraries(EmbreeTest PRIVATE
    embree
    TBB::tbb
)

if(APPLE)
    set_property(TARGET EmbreeTest APPEND PROPERTY INSTALL_RPATH "@executable_path")
elseif(UNIX AND NOT APPLE)
    set_property(TARGET EmbreeTest APPEND PROPERTY INSTALL_RPATH "\$ORIGIN")
endif()

enable_testing()

add_test(
    NAME
        embree_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        EmbreeTest
)

if (WIN32)
    set_tests_properties(embree_basic_test
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_EMBREE_ROOT}/bin\;$ENV{PATH}"
    )
endif()
