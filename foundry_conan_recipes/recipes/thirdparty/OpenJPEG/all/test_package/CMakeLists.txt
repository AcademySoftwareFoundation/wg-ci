cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(OpenJPEG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_openjpeg test_package.cpp)
target_link_libraries(test_openjpeg ${openjpeg_import_target})

enable_testing()
add_test(NAME test_openjpeg
         WORKING_DIRECTORY ${CONAN_OPENJPEG_ROOT}/lib
         COMMAND test_openjpeg)
if (MSVC)
  if (${shared_openjpeg})
    set_tests_properties(test_openjpeg PROPERTIES ENVIRONMENT "PATH=${CONAN_OPENJPEG_ROOT}/bin;$ENV{PATH}")
  endif()
endif()

