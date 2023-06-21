if(TARGET jemalloc::jemalloc)
  return()
endif()

# Compute the installation prefix relative to this file.
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)  # remove one directory level i.e. "cmake/"

add_library(jemalloc::jemalloc INTERFACE IMPORTED)

if(UNIX AND NOT APPLE)
	set(LIBS "${_IMPORT_PREFIX}/lib/libjemalloc.so")
elseif(WIN32)
  if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(LIBS "${_IMPORT_PREFIX}/lib/jemallocd.lib")
  else()
    set(LIBS "${_IMPORT_PREFIX}/lib/jemalloc.lib")
  endif()
endif()

set_target_properties(jemalloc::jemalloc PROPERTIES
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "${LIBS}"
)

unset(_IMPORT_PREFIX)
unset(LIBS)
