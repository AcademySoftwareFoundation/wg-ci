if (CMAKE_VERSION VERSION_LESS 3.10.0)
    message(FATAL_ERROR "FTGL requires at least CMake version 3.10.0")
endif()

if(TARGET FTGL::FTGL)
    return()
endif()

include(CMakeFindDependencyMacro)

get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH) # remove one directory level i.e. "cmake/"

message(STATUS "Found FTGL: ${_IMPORT_PREFIX}")

find_dependency(Freetype REQUIRED)
find_dependency(OpenGL REQUIRED)

include(${_IMPORT_PREFIX}/cmake/FTGLTargets.cmake)

unset(_IMPORT_PREFIX)
