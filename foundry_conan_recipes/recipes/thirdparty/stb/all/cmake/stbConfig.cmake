if(TARGET stb::stb)
	return()
endif()

get_filename_component(_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." PATH)
get_filename_component(_install_prefix "${_install_prefix}" PATH)
message(STATUS "Found stb: ${_install_prefix}.")

set(_interface_link_libraries)
if(UNIX AND NOT APPLE)
  list(APPEND _interface_link_libraries "m")
endif()

add_library(stb::stb INTERFACE IMPORTED)
set_target_properties(stb::stb
	PROPERTIES
	INTERFACE_INCLUDE_DIRECTORIES "${_install_prefix}/include"
	INTERFACE_LINK_LIBRARIES "${_interface_link_libraries}")
