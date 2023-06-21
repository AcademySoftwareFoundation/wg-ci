cmake_minimum_required(VERSION 3.10)

project(re2_test VERSION 1.0 LANGUAGES CXX)

# Future iterations of the re2 config file would ideally have:
# * Threads found as a dependency
# * C++11 set as a required feature to use the headers

find_package(Threads REQUIRED) # needed by re2, but not easy to modify its CMake config file
find_package(re2 REQUIRED)

add_executable(re2_test test_re2.cpp)
target_compile_features(
  re2_test
  PRIVATE
  cxx_std_11
)
target_link_libraries(
  re2_test
  PRIVATE
  re2::re2
)

enable_testing()
add_test(
  NAME re2_test
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMAND re2_test
)
if (${shared_re2})
  if (WIN32)
    set_tests_properties(re2_test PROPERTIES ENVIRONMENT "PATH=${CONAN_RE2_ROOT}/bin;$ENV{PATH}")
  endif()
endif()
