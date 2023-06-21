cmake_minimum_required(VERSION 3.13.0)
project(PackageTest CXX)

find_package(LibXml2 REQUIRED)

include_directories(${LIBXML2_INCLUDE_DIR})

add_executable(test_libxml2 main.cpp)
target_link_libraries(test_libxml2 ${LIBXML2_LIBRARIES})

enable_testing()
add_test(NAME test_libxml2
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_libxml2)

if (MSVC)
  if (${shared_libxml2})
    set_tests_properties(test_libxml2 PROPERTIES ENVIRONMENT "PATH=${CONAN_LIBXML2_ROOT}/bin;$ENV{PATH}")
  endif()
endif()
