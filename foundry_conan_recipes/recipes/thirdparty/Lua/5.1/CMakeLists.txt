# 
cmake_minimum_required(VERSION 3.2)
project(lua-5.1)

include ("cmake/FnBuildHelpers.cmake")
FnEnableDebugSymbols()

option(LUA_USE_CXX_EXCEPTIONS
    "Set to TRUE to enable interoperability with C++ exceptions."
    TRUE)

set(common_sources
    src/lapi.c
    src/lauxlib.c
    src/lbaselib.c
    src/lcode.c
    src/ldblib.c
    src/ldebug.c
    src/ldo.c
    src/ldump.c
    src/lfunc.c
    src/lgc.c
    src/linit.c
    src/liolib.c
    src/llex.c
    src/lmathlib.c
    src/lmem.c
    src/loadlib.c
    src/lobject.c
    src/lopcodes.c
    src/loslib.c
    src/lparser.c
    src/lstate.c
    src/lstring.c
    src/lstrlib.c
    src/ltable.c
    src/ltablib.c
    src/ltm.c
    src/lundump.c
    src/lvm.c
    src/lzio.c
)

#-------------------------------------------------------------------------------
# Platform defines, see luaconf.h. (We don't need to add defines for Windows;
# luaconf.h handles that itself.
if (CMAKE_SYSTEM_NAME MATCHES Linux)
    # See luaconf.h. We don't set LUA_USE_LINUX, because that makes use of
    # libreadline.
    add_definitions(-DLUA_USE_POSIX -DLUA_USE_DLOPEN)

elseif (CMAKE_SYSTEM_NAME MATCHES Darwin)
    add_definitions(-DLUA_USE_MACOSX)
endif ()

#-------------------------------------------------------------------------------
add_library(lua.shared SHARED ${common_sources})
add_library(lua.static STATIC ${common_sources})

if (NOT MSVC)
    target_link_libraries(lua.shared PRIVATE -lm -ldl)
    target_link_libraries(lua.static PRIVATE -lm -ldl)
endif ()

add_executable(lua src/lua.c)
add_executable(luac src/luac.c src/print.c)

target_link_libraries(lua PRIVATE lua.static)
target_link_libraries(luac PRIVATE lua.static)

set_target_properties(lua.shared lua.static PROPERTIES
    POSITION_INDEPENDENT_CODE TRUE
    DEFINE_SYMBOL ""
)

set_target_properties(lua.static PROPERTIES
    C_VISIBILITY_PRESET hidden
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN 1
)

if (LUA_SHARED_ONLY)
    set(INSTALL_TARGET lua.shared)
elseif (LUA_STATIC_ONLY)
    set(INSTALL_TARGET lua.static)
endif ()
set_target_properties(${INSTALL_TARGET} PROPERTIES EXPORT_NAME "Lua")
target_include_directories(${INSTALL_TARGET} INTERFACE $<INSTALL_INTERFACE:include>)

if (NOT MSVC)
    add_compile_options(-Wall)
else ()
    # Remove irksome Windows-specific warnings from the CRT.
    add_definitions(
        -D_CRT_SECURE_NO_WARNINGS
        -D_CRT_SECURE_NO_DEPRECATE
    )
endif ()

if (CMAKE_SYSTEM_NAME MATCHES Windows)
    target_compile_definitions(lua.shared PUBLIC LUA_BUILD_AS_DLL=1)
    set_target_properties(lua.shared PROPERTIES OUTPUT_NAME lua51)
    set_target_properties(lua.static PROPERTIES OUTPUT_NAME lua51_static)
else ()
    set_property(TARGET lua.shared lua.static PROPERTY OUTPUT_NAME lua-5.1)
endif ()

if (LUA_USE_CXX_EXCEPTIONS)
    set_property(SOURCE ${common_sources} PROPERTY LANGUAGE CXX)
    foreach(target lua.shared lua.static)
        if (MSVC)
            # Allow extern "C" functions to throw exceptions; we need to scrub
            # CMAKE_CXX_FLAGS of any conflicting exeption flags first. See:
            # https://msdn.microsoft.com/en-us/library/1deeycx5.aspx
            string(REGEX REPLACE "(^| ) *[/-]EH[ascr-]+ *( |$)" "\\1\\2"
                CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
            target_compile_options("${target}" PRIVATE -EHs)
        else ()
            # g++, clang++ warn when compiling a .c file unless this is
            # specified.
            target_compile_options("${target}" PRIVATE -x c++)
        endif ()
    endforeach()
endif ()

#-------------------------------------------------------------------------------
# GNUInstallDirs default is lib64, but Foundry convention is just "lib".
set(CMAKE_INSTALL_LIBDIR lib)
include(GNUInstallDirs)

foreach(target lua luac ${INSTALL_TARGET})
    install(TARGETS "${target}"
        EXPORT lua-export
        # GNUInstallDirs default is lib64, but Foundry convention is just "lib".
        LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
        PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    )
    FnMSVCTargetInstallPDB("${target}")
endforeach()

install(FILES src/lua.h src/luaconf.h src/lualib.h src/lauxlib.h etc/lua.hpp
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
install(DIRECTORY doc/
    DESTINATION "${CMAKE_INSTALL_DOCDIR}"
    PATTERN *.1 EXCLUDE
)
install(DIRECTORY doc/
    DESTINATION "${CMAKE_INSTALL_MANDIR}/man1"
    FILES_MATCHING PATTERN *.1
)

install(
    EXPORT lua-export
    FILE
        LuaConfig.cmake
    NAMESPACE
        Lua::
    DESTINATION
        cmake
)

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/LuaConfigVersion.cmake"
    VERSION ${LUA_VERSION}
    COMPATIBILITY ExactVersion
)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/LuaConfigVersion.cmake"
        DESTINATION "cmake")
