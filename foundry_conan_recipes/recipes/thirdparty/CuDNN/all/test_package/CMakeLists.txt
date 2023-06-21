cmake_minimum_required(VERSION 3.12)
project(PackageTest)

find_package(cuDNN REQUIRED)

add_executable(cudnn-test cudnn-test.cpp)
target_link_libraries(cudnn-test PRIVATE cuDNN::cuDNN)

if(UNIX)
    target_link_options(cudnn-test PRIVATE "-Wl,-rpath,${CONAN_CUDA_ROOT}/lib64")
endif()

enable_testing()
add_test(
    NAME cudnn-test
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND cudnn-test
)

if (WIN32)
    set_tests_properties(cudnn-test
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_CUDA_ROOT}/bin\;${CONAN_CUDNN_ROOT}/bin\;$ENV{PATH}"
    )
endif()
