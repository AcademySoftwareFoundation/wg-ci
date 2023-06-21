cmake_minimum_required(VERSION 3.0.0)
project(PackageTest C)

find_package(TIFF REQUIRED) # uses CMake's FindTIFF

add_executable(test_libtiff test_package.c)
target_link_libraries(test_libtiff TIFF::TIFF)
if(NOT shared_libtiff)
  find_package(zlib REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
  find_package(JPEG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
  target_link_libraries(test_libtiff zlib::zlib JPEG::JPEG)
  if(UNIX AND NOT APPLE)
    target_link_libraries(test_libtiff m)
  endif()
endif()

enable_testing()
add_test(NAME test_libtiff
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_libtiff)
if (${shared_libtiff})
  if (MSVC)
    set_tests_properties(test_libtiff PROPERTIES ENVIRONMENT "PATH=${CONAN_LIBTIFF_ROOT}/bin;$ENV{PATH}")
  endif()
endif()

