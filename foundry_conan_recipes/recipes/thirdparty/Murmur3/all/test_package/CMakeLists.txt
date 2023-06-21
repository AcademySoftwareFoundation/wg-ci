cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
project(Murmur3PackageTest)

find_package(Murmur3 REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_murmur3 test_package.c)
target_link_libraries(test_murmur3 PRIVATE Murmur3::Murmur3)

enable_testing()
add_test(
    NAME test_murmur3
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_murmur3
)

if (${shared_murmur3})
  if (MSVC)
    set_tests_properties(test_murmur3 PROPERTIES ENVIRONMENT "PATH=${CONAN_MURMUR3_ROOT}/bin;$ENV{PATH}")
  endif()
endif()
