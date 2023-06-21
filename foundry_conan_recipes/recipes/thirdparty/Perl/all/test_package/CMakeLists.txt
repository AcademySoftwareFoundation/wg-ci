cmake_minimum_required(VERSION 3.13)
project(PackageTest C)

find_package(Perl REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_perl test_package.c)
target_link_libraries(test_perl Perl::perl)
if (${shared_perl})
  if (APPLE)
    target_link_options(test_perl PRIVATE "-Wl,-rpath,${CONAN_PERL_ROOT}/lib")
  endif()
endif()

enable_testing()
add_test(NAME test_perl
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_perl)
if (${shared_perl})
  if (MSVC)
    set_tests_properties(test_perl PROPERTIES ENVIRONMENT "PATH=${CONAN_PERL_ROOT}/bin;$ENV{PATH}")
  endif()
endif()
