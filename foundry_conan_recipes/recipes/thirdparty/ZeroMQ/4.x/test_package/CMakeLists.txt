cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(ZeroMQ REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_zeromq test_package.cpp)
target_link_libraries(test_zeromq ZeroMQ::ZeroMQ)

enable_testing()
add_test(NAME test_zeromq
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_zeromq)
if (${shared_zeromq})
  if (MSVC)
    set_tests_properties(test_zeromq PROPERTIES ENVIRONMENT "PATH=${CONAN_ZEROMQ_ROOT}/bin/;$ENV{PATH}")
  endif()
endif()

