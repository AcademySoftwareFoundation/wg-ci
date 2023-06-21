cmake_minimum_required(VERSION 3.13)
project(PackageTest LANGUAGES C)

find_package(CURL CONFIG REQUIRED)

add_executable(CheckCurl check_curl.c)
target_link_libraries(CheckCurl PRIVATE CURL::CURL)

enable_testing()
add_test(NAME check_curl COMMAND $<TARGET_FILE:CheckCurl>)

get_target_property(CURL_LIBTYPE CURL::CURL TYPE)
if (CURL_LIBTYPE STREQUAL "SHARED_LIBRARY")
    set_tests_properties(check_curl PROPERTIES ENVIRONMENT "PATH=${CONAN_CURL_ROOT}/bin;$ENV{PATH}")
endif()
