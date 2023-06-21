cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(EXPAT REQUIRED)

add_executable(test_expat test_package.cpp)
target_link_libraries(test_expat EXPAT::EXPAT)

enable_testing()
add_test(NAME test_expat
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_expat)
if (${shared_expat})
  if (MSVC)
    set_tests_properties(test_expat PROPERTIES ENVIRONMENT "PATH=${CONAN_EXPAT_ROOT}/bin;$ENV{PATH}")
  endif()
endif()

