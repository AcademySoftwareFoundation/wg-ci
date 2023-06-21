cmake_minimum_required(VERSION 3.18)
project(PackageTest CXX)

# Force the nvTools location, since this seems to be hardcoded to the default install location on Windows
set(NVTOOLEXT_HOME ${CONAN_CUDA_ROOT})
find_package(TorchText CONFIG REQUIRED)

add_executable(test_torchtext test_package.cpp)
target_link_libraries(test_torchtext PRIVATE TorchText::TorchText)

enable_testing()
add_test(NAME test_torchtext
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_torchtext)

if (WIN32)
    set_tests_properties(test_torchtext
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_TORCHTEXT_ROOT}/bin\;${CONAN_PYTORCH_ROOT}/lib\;${CONAN_PYTORCH_ROOT}/bin\;${CONAN_CUDA_ROOT}/bin\;${CONAN_CUDNN_ROOT}/bin\;${CONAN_MKL_ROOT}/bin\;$ENV{PATH}"
    )
endif()
