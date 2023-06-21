cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
project(Murmur3)

if (BUILD_SHARED_LIBS)
  if (WIN32)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
  endif()
endif()

add_library(Murmur3 Murmur3_src/murmur3.c)
add_library(Murmur3::Murmur3 ALIAS Murmur3)

install(
  TARGETS Murmur3
  EXPORT Murmur3Targets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  INCLUDES DESTINATION include)

install(FILES
  Murmur3_src/murmur3.h
  DESTINATION include)

include(CMakePackageConfigHelpers)

set(cmake_package_name Murmur3)
set(targets_export_name ${cmake_package_name}Targets CACHE INTERNAL "")
set(generated_dir "${CMAKE_CURRENT_BINARY_DIR}/generated" CACHE INTERNAL "")
set(config_file "${generated_dir}/${cmake_package_name}Config.cmake")
set(cmake_files_install_dir "${CMAKE_INSTALL_LIBDIR}/cmake/${cmake_package_name}")
set(version_file "${generated_dir}/${cmake_package_name}ConfigVersion.cmake")

write_basic_package_version_file(${version_file} VERSION ${MURMUR3_VERSION} COMPATIBILITY AnyNewerVersion)

install(EXPORT ${targets_export_name}
  NAMESPACE ${cmake_package_name}::
  DESTINATION ${cmake_files_install_dir})

configure_package_config_file("${Murmur3_SOURCE_DIR}/Config.cmake.in"
    "${config_file}" INSTALL_DESTINATION ${cmake_files_install_dir})

install(FILES ${version_file} ${config_file}
  DESTINATION ${cmake_files_install_dir})
