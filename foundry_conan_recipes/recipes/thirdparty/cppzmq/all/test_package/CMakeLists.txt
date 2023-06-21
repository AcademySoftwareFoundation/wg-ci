cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)

find_package(ZeroMQ REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
find_package(cppzmq REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
find_package(Threads REQUIRED)

add_executable(test_cppzmq example.cpp)
target_link_libraries(test_cppzmq ZeroMQ::ZeroMQ cppzmq::cppzmq Threads::Threads)

enable_testing()
add_test(NAME test_cppzmq
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_cppzmq)

if (${shared_zeromq})
  if (MSVC)
    set_tests_properties(test_cppzmq PROPERTIES ENVIRONMENT "PATH=${CONAN_ZEROMQ_ROOT}/bin/;$ENV{PATH}")
  endif()
endif()
