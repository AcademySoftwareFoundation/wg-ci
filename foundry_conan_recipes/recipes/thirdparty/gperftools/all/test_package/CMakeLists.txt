cmake_minimum_required(VERSION 3.1.0)
project(GPerfToolsTests)
set(CMAKE_CXX_STANDARD 11)

find_package(GPerfTools CONFIG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_tcmalloc test_tcmalloc.cpp)
target_link_libraries(test_tcmalloc PRIVATE GPerfTools::GPerfTools)

enable_testing()
add_test(
    NAME test_tcmalloc
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_tcmalloc
)

if (WIN32)
    set_tests_properties(test_tcmalloc
        PROPERTIES
            ENVIRONMENT "PATH=${CONAN_GPERFTOOLS_ROOT}/bin;$ENV{PATH}"
    )
endif()
