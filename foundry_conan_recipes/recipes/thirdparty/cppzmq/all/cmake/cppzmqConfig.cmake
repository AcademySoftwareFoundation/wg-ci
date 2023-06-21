get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)

foreach (target cppzmq cppzmq::cppzmq)
  if (NOT TARGET ${target})
    add_library(${target} INTERFACE IMPORTED)
    set_target_properties(${target} PROPERTIES
      INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
    )
  endif ()
endforeach()

unset(_IMPORT_PREFIX)
