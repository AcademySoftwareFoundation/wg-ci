cmake_minimum_required(VERSION 3.0)
project(GlfwPackageTest CXX)

find_package(glfw REQUIRED)

add_executable(test_glfw test_package.cpp)
target_link_libraries(test_glfw glfw::glfw)

enable_testing()
add_test(NAME test_glfw
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_glfw)

if(shared_glfw)
    if (MSVC)
        set_tests_properties(test_glfw
            PROPERTIES
            ENVIRONMENT "PATH=${CONAN_GLFW_ROOT}/bin;$ENV{PATH}")
    endif()
endif()
