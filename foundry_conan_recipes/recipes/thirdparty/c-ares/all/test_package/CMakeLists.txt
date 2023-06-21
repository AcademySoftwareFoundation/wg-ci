cmake_minimum_required(VERSION 3.10)

project(c-ares_test VERSION 1.0 LANGUAGES C)

find_package(c-ares REQUIRED)

add_executable(c-ares_test test_c-ares.c)
target_link_libraries(
  c-ares_test
  PRIVATE
  c-ares::cares
)

enable_testing()
add_test(
  NAME c-ares_test
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMAND c-ares_test
)
if (${shared_c-ares})
  if (WIN32)
    set_tests_properties(c-ares_test PROPERTIES ENVIRONMENT "PATH=${CONAN_C-ARES_ROOT}/bin;$ENV{PATH}")
  endif()
endif()
