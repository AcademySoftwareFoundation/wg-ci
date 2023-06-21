cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

install( FILES "CMakeLists.txt" COMPONENT SomeContent DESTINATION resources )

################################################################################
# Installer options
################################################################################

set( CPACK_PACKAGE_NAME                   "WixTest" )
set( CPACK_PACKAGE_DESCRIPTION            "WixTest" ) # TODO: something longer
set( CPACK_PACKAGE_DESCRIPTION_SUMMARY    "WixTest" ) # TODO: something longer
set( CPACK_PACKAGE_HOMEPAGE_URL           "https://github.com/wixtoolset/wix3" )
set( CPACK_PACKAGE_INSTALL_DIRECTORY      "WixTest" )
set( CPACK_PACKAGE_INSTALL_REGISTRY_KEY   "WixTest" )
set( CPACK_PACKAGE_VENDOR                 "Foundry" )
set( CPACK_PACKAGE_VERSION                "1.0.0" )
set( CPACK_PACKAGE_VERSION_MAJOR          "1" )
set( CPACK_PACKAGE_VERSION_MINOR          "0" )
set( CPACK_PACKAGE_VERSION_PATCH          "0" )
set( CPACK_PACKAGE_FILE_NAME              "WixTest" )

set( CPACK_COMPONENTS_ALL                 "SomeContent" )
set( CPACK_PACKAGE_DIRECTORY              "${CMAKE_BINARY_DIR}/package" )
set( CPACK_OUTPUT_CONFIG_FILE             "${CMAKE_BINARY_DIR}/CPackConfig.cmake" )
set( CPACK_PACKAGING_INSTALL_PREFIX       "/" )
set( CPACK_GENERATOR                      "WIX" )
set( CPACK_STRIP_FILES ON )

include(CPack)
