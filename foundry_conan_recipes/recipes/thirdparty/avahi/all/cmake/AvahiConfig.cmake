include(FindPkgConfig)
pkg_check_modules(dbus REQUIRED dbus-1)

# Compute the installation prefix relative to this file.
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH) # remove one directory level i.e. "cmake/"
message(STATUS "Found Avahi: ${_IMPORT_PREFIX}")

if(NOT TARGET Avahi::Client)
    add_library(Avahi::Core SHARED IMPORTED)
    set_target_properties(Avahi::Core
        PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
            IMPORTED_LOCATION "${_IMPORT_PREFIX}/lib/libavahi-core.so"
    )

    add_library(Avahi::Common SHARED IMPORTED)
    set_target_properties(Avahi::Common
        PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
            IMPORTED_LOCATION "${_IMPORT_PREFIX}/lib/libavahi-common.so"
            INTERFACE_LINK_LIBRARIES "Avahi::Core"
    )    

    add_library(Avahi::Client SHARED IMPORTED)
    set_target_properties(Avahi::Client
        PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
            IMPORTED_LOCATION "${_IMPORT_PREFIX}/lib/libavahi-client.so"
            INTERFACE_LINK_LIBRARIES "Avahi::Common;${dbus_LIBRARIES}"
    )

    add_library(Avahi::DnsSD SHARED IMPORTED)
    set_target_properties(Avahi::DnsSD
        PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
            IMPORTED_LOCATION "${_IMPORT_PREFIX}/lib/libdns_sd.so"
            INTERFACE_LINK_LIBRARIES "Avahi::Client"
    )

    add_library(Avahi::Qt5 SHARED IMPORTED)
    set_target_properties(Avahi::Qt5
        PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
            IMPORTED_LOCATION "${_IMPORT_PREFIX}/lib/libavahi-qt5.so"
            INTERFACE_LINK_LIBRARIES "Avahi::Client"
    )
endif()

unset(_IMPORT_PREFIX)
