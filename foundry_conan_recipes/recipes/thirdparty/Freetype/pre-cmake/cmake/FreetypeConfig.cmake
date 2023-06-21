if (CMAKE_VERSION VERSION_LESS 3.10.0)
    message(FATAL_ERROR "Freetype requires at least CMake version 3.10.0")
endif()

if(TARGET Freetype::Freetype)
    return()
endif()

get_filename_component(_freetype_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
message(STATUS "Found Freetype: ${_freetype_install_prefix}.")

add_library(Freetype::Freetype INTERFACE IMPORTED)

file(GLOB _freetype_libs "${_freetype_install_prefix}/lib/*")
set_target_properties(Freetype::Freetype
    PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${_freetype_install_prefix}/include"
    INTERFACE_LINK_LIBRARIES "${_freetype_libs}"
)
unset(_freetype_libs)
unset(_freetype_install_prefix)