#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(RadeonImageFilters CONFIG REQUIRED)

# Check that RADEONIMAGEFILTERS_MODELS_DIR exists. This directory contains trained AI models required by the image
# filters.
if(NOT EXISTS ${RADEONIMAGEFILTERS_MODELS_DIR})
    message(FATAL_ERROR "RADEONIMAGEFILTERS_MODELS_DIR does not exist: ${RADEONIMAGEFILTERS_MODELS_DIR}")
endif()

add_executable(RadeonImageFiltersTest main.cpp)

target_link_libraries(RadeonImageFiltersTest PRIVATE RadeonImageFilters::RadeonImageFilters)

enable_testing()

add_test(
    NAME radeon_image_filters_test
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND RadeonImageFiltersTest)

if(WIN32)
    set_tests_properties(radeon_image_filters_test PROPERTIES ENVIRONMENT
                                                              "PATH=${CONAN_RADEONIMAGEFILTERS_ROOT}/bin;$ENV{PATH}")
endif()
