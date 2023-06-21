# Compute the installation prefix relative to this file.
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH) # remove one directory level i.e. "cmake/"
message(STATUS "Found msgpack-cxx: ${_IMPORT_PREFIX}")

if(NOT TARGET msgpack-cxx::msgpack-cxx)
    add_library(msgpack-cxx INTERFACE)
    set_target_properties(msgpack-cxx
        PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
            INTERFACE_COMPILE_DEFINITIONS MSGPACK_NO_BOOST
    )

    add_library(msgpack-cxx::msgpack-cxx ALIAS msgpack-cxx)
endif()

unset(_IMPORT_PREFIX)
