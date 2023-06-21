cmake_minimum_required(VERSION 3.20.0)
project(PackageTest LANGUAGES C)

find_package(SWIG CONFIG REQUIRED)
find_package(LuaJIT CONFIG REQUIRED)

set(bindings_in "${CMAKE_CURRENT_LIST_DIR}/bindings.i")
set(bindings_src "bindings.c")

add_custom_command(
    OUTPUT "${bindings_src}"
    COMMAND "${SWIG_EXECUTABLE}" -lua -o "${bindings_src}" "${bindings_in}"
    DEPENDS "${bindings_in}"
)

add_library(library STATIC library.c)

add_library(bindings SHARED ${bindings_src} library.c)
target_link_libraries(bindings LuaJIT::LuaJIT library)
if (NOT WIN32)
    target_link_libraries(bindings m)
endif ()
set_target_properties(bindings PROPERTIES PREFIX "")

add_executable(main main.c)
target_link_libraries(main bindings LuaJIT::LuaJIT)

enable_testing()
add_test(NAME main
         WORKING_DIRECTORY "${CMAKE_BIN_DIR}"
         COMMAND "main" "${CMAKE_CURRENT_LIST_DIR}/example.lua")
