if (CMAKE_VERSION VERSION_LESS 3.0.0)
  message(FATAL_ERROR "zlib requires at least CMake version 3.0.0")
endif()

if(TARGET OpenSubdiv::OpenSubdiv)
    return()
endif()

get_filename_component(_opensubdiv_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

message(STATUS "Found OpenSubdiv: ${_opensubdiv_install_prefix}")

add_library(OpenSubdiv::CPU STATIC IMPORTED)
add_library(OpenSubdiv::GPU STATIC IMPORTED)
add_library(OpenSubdiv::OpenSubdiv ALIAS OpenSubdiv::GPU)

set_target_properties(OpenSubdiv::CPU
  PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${_opensubdiv_install_prefix}/include"
)

set_target_properties(OpenSubdiv::GPU
  PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${_opensubdiv_install_prefix}/include"
    INTERFACE_LINK_LIBRARIES OpenSubdiv::CPU
)

if(WIN32)
  set_target_properties(OpenSubdiv::CPU
    PROPERTIES
      IMPORTED_LOCATION "${_opensubdiv_install_prefix}/lib/osdCPU.lib"
  )

  set_target_properties(OpenSubdiv::GPU
    PROPERTIES
      IMPORTED_LOCATION "${_opensubdiv_install_prefix}/lib/osdGPU.lib"
  )
else()
  set_target_properties(OpenSubdiv::CPU
    PROPERTIES
      IMPORTED_LOCATION "${_opensubdiv_install_prefix}/lib/libosdCPU.a"
  )

  set_target_properties(OpenSubdiv::GPU
    PROPERTIES
      IMPORTED_LOCATION "${_opensubdiv_install_prefix}/lib/libosdGPU.a"
  )
endif()
