cmake_minimum_required( VERSION 3.10 )
project( SQLCipher VERSION 3.1.0 )

find_package( OpenSSL REQUIRED )

add_library( SQLCipher STATIC SQLCipher_src/sqlcipher.c )
add_library( SQLCipher::SQLCipher ALIAS SQLCipher )

target_include_directories( SQLCipher
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/SQLCipher_src/include>
    $<INSTALL_INTERFACE:include> )

target_compile_definitions( SQLCipher
  PUBLIC
    SQLITE_HAS_CODEC=1
    SQLITE_ENABLE_FTS3=1
    D_FOUNDRY_SQLCIPHERHEADER=1
    HAVE_STDINT_H=1 )

target_link_libraries( SQLCipher PUBLIC OpenSSL::SSL OpenSSL::Crypto )

install( TARGETS SQLCipher EXPORT SQLCipherTargets ARCHIVE DESTINATION libs )
install( EXPORT SQLCipherTargets NAMESPACE SQLCipher:: DESTINATION cmake )
install( DIRECTORY SQLCipher_src/include/ DESTINATION include )

configure_file( SQLCipherConfigVersion.cmake.in SQLCipherConfigVersion.cmake @ONLY )
install(
  FILES
    SQLCipherConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/SQLCipherConfigVersion.cmake
  DESTINATION cmake )
