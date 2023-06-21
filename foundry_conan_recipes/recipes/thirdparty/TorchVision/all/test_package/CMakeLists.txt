cmake_minimum_required(VERSION 3.12)
project(PackageTest CXX)

find_package(TorchVision REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_torchvision test_package.cpp)
target_link_libraries(test_torchvision
    PRIVATE
        $<$<PLATFORM_ID:Linux>:MKL::RT>
        $<IF:$<PLATFORM_ID:Darwin>,torch_cpu,torch>
        TorchVision::TorchVision
)

if(NOT (CMAKE_SYSTEM_PROCESSOR MATCHES "arm64"))
    target_link_libraries(test_torchvision PRIVATE MKL::Intel)
endif()

enable_testing()
add_test(
    NAME test_torchvision
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_torchvision
)

if (UNIX AND NOT APPLE)
    add_test(
        NAME doesnt_link_against_cuda
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMAND ldd ${CONAN_TORCHVISION_ROOT}/lib/libtorchvision.so
    )
    set_tests_properties(doesnt_link_against_cuda
        PROPERTIES
            FAIL_REGULAR_EXPRESSION "libcuda\\.so"
    )
endif()

if (WIN32)
    set_tests_properties(test_torchvision
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_TORCHVISION_ROOT}/bin\;${CONAN_PYTORCH_ROOT}/lib\;${CONAN_PYTORCH_ROOT}/bin\;${CONAN_CUDA_ROOT}/bin\;${CONAN_CUDNN_ROOT}/bin\;${CONAN_MKL_ROOT}/bin\;$ENV{PATH}"
    )
endif()
