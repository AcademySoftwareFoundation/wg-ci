cmake_minimum_required(VERSION 3.0.0)
project(PackageTest C)

find_package(GLEW REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_glew test_package.c)
target_link_libraries(test_glew GLEW::GLEW)

enable_testing()
add_test(NAME test_glew
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_glew)
if (${shared_glew})
  if (MSVC)
    set_tests_properties(test_glew PROPERTIES ENVIRONMENT "PATH=${CONAN_GLEW_ROOT}/bin/;$ENV{PATH}")
  endif()
endif()

