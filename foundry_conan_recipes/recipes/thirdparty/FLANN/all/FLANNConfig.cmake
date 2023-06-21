if (CMAKE_VERSION VERSION_LESS 3.10.0)
    message(FATAL_ERROR "FLANN requires at least CMake version 3.10.0")
endif()

if(TARGET FLANN::FLANN)
    return()
endif()

# Compute the installation prefix relative to this file.
get_filename_component(_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
message(STATUS "Found FLANN: ${_install_prefix}.")

set(FLANN_FOUND True)

if(APPLE)
    set(FLANN_LIBRARIES "${_install_prefix}/lib/libflann_cpp_s.a" )
elseif(UNIX AND NOT APPLE)
    set(FLANN_LIBRARIES "${_install_prefix}/lib/libflann_cpp_s.a" )
elseif(WIN32)
    set(FLANN_LIBRARIES "${_install_prefix}/lib/flann_cpp_s.lib" )
else()
    message(FATAL_ERROR "Unknown OS")
endif()

add_library(FLANN::FLANN IMPORTED STATIC)
set_target_properties(FLANN::FLANN
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES
            ${_install_prefix}/include/
        IMPORTED_LOCATION
            ${FLANN_LIBRARIES}
)

unset(FLANN_LIBRARIES)
unset(_install_prefix)
