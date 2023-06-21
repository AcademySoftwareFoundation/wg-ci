cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(LittleCMS REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_littleCMS test_package.cpp)
target_link_libraries(test_littleCMS LittleCMS::LittleCMS)

enable_testing()
add_test(NAME test_littleCMS WORKING_DIRECTORY ${CMAKE_BINARY_DIR} COMMAND test_littleCMS)

get_target_property( LittleCMS_TYPE LittleCMS::LittleCMS TYPE )
if ( LittleCMS_TYPE STREQUAL "SHARED_LIBRARY" )
  if (MSVC)
    set_tests_properties(test_littleCMS PROPERTIES ENVIRONMENT "PATH=${CONAN_LITTLECMS_ROOT}/bin;$ENV{PATH}")
  endif()
endif()