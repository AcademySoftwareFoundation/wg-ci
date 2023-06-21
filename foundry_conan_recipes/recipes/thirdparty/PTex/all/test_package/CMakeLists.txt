cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(PTex REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_ptex test_package.cpp)
target_link_libraries(test_ptex PTex::PTex)

enable_testing()
add_test(NAME test_ptex
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_ptex)
if (${shared_ptex})
  if (MSVC)
    set_tests_properties(test_ptex PROPERTIES ENVIRONMENT "PATH=${CONAN_PTEX_ROOT}/lib;$ENV{PATH}")
  endif()
endif()
