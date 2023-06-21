if (CMAKE_VERSION VERSION_LESS 3.0.0)
  message(FATAL_ERROR "Technocrane requires at least CMake version 3.0.0")
endif()

get_filename_component(_technocrane_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

message(STATUS "Found Technocrane: ${_technocrane_install_prefix}")

if (NOT TARGET Technocrane::Technocrane)

  add_library(Technocrane::Technocrane IMPORTED SHARED)
  set_target_properties(
    Technocrane::Technocrane
    PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${_technocrane_install_prefix}/include
    IMPORTED_LOCATION ${_technocrane_install_prefix}/bin/TechnocraneLib.dll
    IMPORTED_IMPLIB ${_technocrane_install_prefix}/lib/TechnocraneLib.lib
  )
  
endif()
