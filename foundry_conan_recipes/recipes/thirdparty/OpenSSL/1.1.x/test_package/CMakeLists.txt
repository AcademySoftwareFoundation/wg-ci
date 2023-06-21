cmake_minimum_required(VERSION 3.0.0)
project(PackageTest C)

find_package(OpenSSL REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_crypto test_crypto.c)
target_link_libraries(test_crypto OpenSSL::Crypto)

add_executable(test_ssl test_ssl.c)
target_link_libraries(test_ssl OpenSSL::SSL)

enable_testing()
add_test(NAME test_crypto
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_crypto)
add_test(NAME test_ssl
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_ssl)

if (${shared_openssl})
  if (MSVC)
    set_tests_properties(test_crypto PROPERTIES ENVIRONMENT "PATH=${CONAN_OPENSSL_ROOT}/bin;$ENV{PATH}")
    set_tests_properties(test_ssl PROPERTIES ENVIRONMENT "PATH=${CONAN_OPENSSL_ROOT}/bin;$ENV{PATH}")
  endif()
endif()
