cmake_minimum_required(VERSION 3.12)
project(PackageTest)

message(STATUS "prefix path: ${CMAKE_PREFIX_PATH}")

find_package(CUDA CONFIG REQUIRED)

add_executable(cudart-deviceCount cudart-deviceCount.cpp)
target_link_libraries(cudart-deviceCount PRIVATE CUDA::Headers CUDA::cudart)

enable_testing()
add_test(
    NAME cudart-deviceCount
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND cudart-deviceCount
)

if (WIN32)
    set_tests_properties(cudart-deviceCount
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_CUDA_ROOT}/bin;$ENV{PATH}"
    )
endif()

# Test that a CUDA source file can compile.
enable_language(CUDA)

add_library(cudaPtx OBJECT "example.cu")
set_target_properties(cudaPtx PROPERTIES CUDA_PTX_COMPILATION ON)
