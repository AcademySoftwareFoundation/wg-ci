# Compute the installation prefix relative to this file.
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH) # remove one directory level i.e. "cmake/"
message(STATUS "Found see2neon: ${_IMPORT_PREFIX}")

if(NOT TARGET sse2neon::sse2neon)
    add_library(sse2neon INTERFACE)
    set_target_properties(sse2neon
        PROPERTIES
            INTERFACE_COMPILE_FEATURES cxx_std_14
            INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}"
    )
    add_library(sse2neon::sse2neon ALIAS sse2neon)
endif(NOT TARGET sse2neon::sse2neon)
