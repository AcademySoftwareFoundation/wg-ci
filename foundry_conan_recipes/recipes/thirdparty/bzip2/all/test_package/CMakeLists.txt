cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(bzip2 REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_bzip2 example.cpp)
target_link_libraries(test_bzip2 bz2::bz2)

enable_testing()
add_test(NAME test_version
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_bzip2)
if (${shared_bzip})
  if (MSVC)
    set_tests_properties(test_version PROPERTIES ENVIRONMENT "PATH=${CONAN_BZIP2_ROOT}/bin;$ENV{PATH}")
  endif()
endif()
