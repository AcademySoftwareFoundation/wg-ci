cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(TBB COMPONENTS tbb REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(tbb_fib example.cpp)
target_compile_features(tbb_fib PRIVATE cxx_lambdas)
target_link_libraries(tbb_fib TBB::tbb)

enable_testing()
add_test(NAME test_tbb_fib
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND tbb_fib)
if (MSVC)
set_tests_properties(test_tbb_fib PROPERTIES ENVIRONMENT "PATH=${CONAN_TBB_ROOT}/bin;$ENV{PATH}")
endif()

# Tests whether we will encounter a specific header issue with Windows MSVC2017
# as raised here: https://github.com/conda-forge/tbb-feedstock/pull/82/

add_executable(concurrent_vector concurrent_vector_test.cpp)
target_compile_features(concurrent_vector PRIVATE cxx_lambdas)
target_link_libraries(concurrent_vector TBB::tbb)
add_test(NAME test_concurrent_vector
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND concurrent_vector)
if (MSVC)
set_tests_properties(test_concurrent_vector PROPERTIES ENVIRONMENT "PATH=${CONAN_TBB_ROOT}/bin;$ENV{PATH}")
endif()
