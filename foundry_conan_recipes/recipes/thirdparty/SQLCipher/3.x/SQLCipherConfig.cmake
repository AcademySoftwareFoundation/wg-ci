include(CMakeFindDependencyMacro)
find_dependency( OpenSSL )

get_filename_component( _IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH )
include( ${_IMPORT_PREFIX}/SQLCipherTargets.cmake )
unset( _IMPORT_PREFIX )
