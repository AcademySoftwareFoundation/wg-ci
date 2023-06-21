cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

find_package(hdf5 REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_hdf5 test_package.cpp)
target_link_libraries(test_hdf5 hdf5 hdf5_cpp)

enable_testing()
add_test(NAME test_hdf5
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_hdf5)
if (${shared_hdf5})
  if (MSVC)
    set_tests_properties(test_hdf5 PROPERTIES ENVIRONMENT "PATH=${CONAN_HDF5_ROOT}/bin;$ENV{PATH}")
  endif()
endif()

