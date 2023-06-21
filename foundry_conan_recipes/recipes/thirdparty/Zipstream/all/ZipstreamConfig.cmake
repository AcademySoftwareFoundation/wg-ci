if(TARGET Zipstream::Zipstream)
    return()
endif()

include(CMakeFindDependencyMacro)
find_dependency(zlib CONFIG REQUIRED)

# Compute the installation prefix relative to this file.
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH) # remove one directory level i.e. "cmake/"

add_library(Zipstream::Zipstream INTERFACE IMPORTED)
set_target_properties(Zipstream::Zipstream 
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES ${_IMPORT_PREFIX}/include
        INTERFACE_LINK_LIBRARIES ZLIB::ZLIB)
unset(_IMPORT_PREFIX)
