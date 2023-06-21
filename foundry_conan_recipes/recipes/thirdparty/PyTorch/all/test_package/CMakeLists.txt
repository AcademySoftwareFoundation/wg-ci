cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(Torch REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_pytorch test_package.cpp)
target_include_directories(test_pytorch INTERFACE torch)
target_link_libraries(test_pytorch torch)
target_compile_features(test_pytorch PRIVATE cxx_std_14)

enable_testing()
add_test(NAME test_pytorch
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_pytorch)

if (WIN32)
    set_tests_properties(test_pytorch
        PROPERTIES ENVIRONMENT "PATH=${CONAN_PYTORCH_ROOT}/lib\;${CONAN_CUDA_ROOT}/bin\;${CONAN_CUDNN_ROOT}/bin\;${CONAN_MKL_ROOT}/bin\;$ENV{PATH}"
    )
endif()
