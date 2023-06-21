if (CMAKE_VERSION VERSION_LESS 3.10.0)
    message(FATAL_ERROR "Fontconfig requires at least CMake version 3.10.0")
endif()

if(TARGET Fontconfig::Fontconfig)
    return()
endif()

get_filename_component(_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
message(STATUS "Found Fontconfig: ${_install_prefix}.")

include(CMakeFindDependencyMacro)
find_dependency(EXPAT REQUIRED)
find_dependency(Freetype REQUIRED)

add_library(Fontconfig::Fontconfig INTERFACE IMPORTED)

file(GLOB _fontconfig_libs "${_install_prefix}/lib/*.[a|lib]")
set_target_properties(Fontconfig::Fontconfig
    PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${_install_prefix}/include"
    INTERFACE_LINK_LIBRARIES "${_fontconfig_libs};Freetype::Freetype;EXPAT::EXPAT"
)
unset(_fontconfig_libs)
unset(_install_prefix)
