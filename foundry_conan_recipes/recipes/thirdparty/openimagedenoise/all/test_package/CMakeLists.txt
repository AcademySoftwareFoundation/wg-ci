#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(OpenImageDenoise CONFIG REQUIRED)
find_package(TBB COMPONENTS tbb REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(oidn_test main.cpp)

target_link_libraries(oidn_test PRIVATE OpenImageDenoise TBB::tbb)

enable_testing()

add_test(
    NAME oidn_test
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND oidn_test
)

if(WIN32)
    set_tests_properties(oidn_test PROPERTIES ENVIRONMENT "PATH=${CONAN_TBB_ROOT}/bin\;${CONAN_OPENIMAGEDENOISE_ROOT}/bin\;$ENV{PATH}")
endif()
