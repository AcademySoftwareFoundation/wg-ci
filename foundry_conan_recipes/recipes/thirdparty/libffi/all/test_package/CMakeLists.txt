cmake_minimum_required(VERSION 3.1)
project(PackageTest)

find_package(libffi REQUIRED)

if(CONAN_SETTINGS_COMPILER_RUNTIME MATCHES ".*d")
    add_compile_definitions(DISABLE_FFI_CALL)
endif()

add_executable(test_libffi test_package.c)
target_link_libraries(test_libffi PRIVATE libffi::libffi)

enable_testing()
add_test(
    NAME test_libffi
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_libffi
)
