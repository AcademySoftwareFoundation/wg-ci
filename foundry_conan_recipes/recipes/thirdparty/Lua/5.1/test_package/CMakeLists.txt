cmake_minimum_required(VERSION 3.1)
project(LuaTest CXX)

find_package(Lua REQUIRED NO_CMAKE_SYSTEM_PATH)

add_executable(LuaTest LuaTest.cpp)
target_link_libraries(LuaTest
    PRIVATE
    Lua::Lua
)

enable_testing()
add_test(NAME LuaTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND LuaTest)

if (${shared_lua})
    if (MSVC)
        set_tests_properties(LuaTest PROPERTIES ENVIRONMENT "PATH=${CONAN_LUA_ROOT}/bin;$ENV{PATH}")
    endif ()
endif ()
