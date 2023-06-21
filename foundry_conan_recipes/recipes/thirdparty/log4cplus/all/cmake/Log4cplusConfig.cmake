
if(TARGET Log4cplus::Log4cplus)
    return()
endif()

include(CMakeFindDependencyMacro)
find_dependency(Threads)

add_library(Log4cplus::Log4cplus INTERFACE IMPORTED)

get_filename_component(_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

set_target_properties(Log4cplus::Log4cplus
    PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${_install_prefix}/include"
)

if(UNIX)
    set_target_properties(Log4cplus::Log4cplus
        PROPERTIES
        INTERFACE_LINK_LIBRARIES "${_install_prefix}/lib/liblog4cplus.a;Threads::Threads"
    )
elseif(WIN32)
    set_target_properties(Log4cplus::Log4cplus
        PROPERTIES
        INTERFACE_LINK_LIBRARIES "${_install_prefix}/lib/log4cplus.lib;Ws2_32"
    )
else()
    message( FATAL_ERROR "Unknown OS" )
endif()
