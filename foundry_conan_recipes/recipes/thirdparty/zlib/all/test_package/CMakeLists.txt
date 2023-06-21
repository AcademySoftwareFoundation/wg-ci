cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(zlib REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

if(NOT TARGET ZLIB::ZLIB)
  message(FATAL_ERROR "Unable to locate import target ZLIB::ZLIB for compatibility with FindZLIB.cmake")
endif()

add_executable(test_zlib test_package.cpp)
target_link_libraries(test_zlib zlib::zlib)

enable_testing()
add_test(NAME test_zlib
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_zlib)
if (${shared_zlib})
  if (MSVC)
    set_tests_properties(test_zlib PROPERTIES ENVIRONMENT "PATH=${CONAN_ZLIB_ROOT}/lib;$ENV{PATH}")
  endif()
endif()
