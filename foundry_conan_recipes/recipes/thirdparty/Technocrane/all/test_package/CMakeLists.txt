cmake_minimum_required(VERSION 3.0)
project(TechnocraneTest CXX)

find_package(Technocrane REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)
add_executable(test_technocrane test_package.cpp)
target_link_libraries(test_technocrane Technocrane::Technocrane)

enable_testing()
add_test(NAME test_technocrane
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_technocrane)
if (MSVC)
  set_tests_properties(test_technocrane PROPERTIES ENVIRONMENT "PATH=${CONAN_TECHNOCRANE_ROOT}/bin;$ENV{PATH}")
endif()
