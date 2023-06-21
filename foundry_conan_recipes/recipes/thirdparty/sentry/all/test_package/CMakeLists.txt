cmake_minimum_required(VERSION 3.20 FATAL_ERROR)
project(PackageTest CXX)

find_package(sentry REQUIRED)

if(NOT TARGET sentry_crashpad::crashpad_handler)
    message(FATAL_ERROR "Unable to find the target sentry_crashpad::crashpad_handler")
endif()

add_executable(example example.cpp)
target_link_libraries(example PRIVATE sentry::sentry)

enable_testing()

add_test(
    NAME example
    COMMAND example
)

if(WIN32)
    if(sentry_shared)
        set_tests_properties(example PROPERTIES ENVIRONMENT "PATH=${CONAN_SENTRY_ROOT}/bin;$ENV(PATH)")
    endif()
endif()
