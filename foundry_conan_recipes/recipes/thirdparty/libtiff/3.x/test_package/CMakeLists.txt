cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(TIFF REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
find_package(zlib REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
find_package(JPEG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_libtiff test_package.cpp)
target_link_libraries(test_libtiff TIFF::TIFF zlib::zlib JPEG::JPEG)

enable_testing()
add_test(NAME test_libtiff
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_libtiff)
if (${shared_libtiff})
  if (MSVC)
    set_tests_properties(test_libtiff PROPERTIES ENVIRONMENT "PATH=${CONAN_LIBTIFF_ROOT}/lib;$ENV{PATH}")
  endif()
endif()

