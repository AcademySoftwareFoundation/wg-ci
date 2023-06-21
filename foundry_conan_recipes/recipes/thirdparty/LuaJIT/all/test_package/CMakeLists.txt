cmake_minimum_required(VERSION 3.1)
project(LuaJITTest CXX)

find_package(LuaJIT REQUIRED)

add_executable(LuaJITTest LuaJITTest.cpp)
target_link_libraries(LuaJITTest
    PRIVATE
    LuaJIT::LuaJIT
)

enable_testing()
add_test(NAME LuaJITTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND LuaJITTest)

if (MSVC)
    set_tests_properties(LuaJITTest PROPERTIES ENVIRONMENT "PATH=${CONAN_LUAJIT_ROOT}/bin;$ENV{PATH}")
endif()
