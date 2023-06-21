cmake_minimum_required(VERSION 3.0)

project(TinyXML)

set(INSTALL_BIN_DIR "${CMAKE_INSTALL_PREFIX}/bin"     CACHE PATH "Installation directory for executables")
set(INSTALL_LIB_DIR "${CMAKE_INSTALL_PREFIX}/lib"     CACHE PATH "Installation directory for libraries")
set(INSTALL_INC_DIR "${CMAKE_INSTALL_PREFIX}/include" CACHE PATH "Installation directory for headers")

if(BUILD_SHARED_LIBS)
    add_library(TinyXML SHARED)
else()
    add_library(TinyXML STATIC)
endif()

if(MSVC)
    if(BUILD_SHARED_LIBS)
        set_target_properties(TinyXML
            PROPERTIES
            WINDOWS_EXPORT_ALL_SYMBOLS ON)

        if(CMAKE_BUILD_TYPE MATCHES "Release")
            target_compile_options(TinyXML PRIVATE /Zi)
            set_target_properties(TinyXML
                PROPERTIES
                LINK_FLAGS "/INCREMENTAL:NO /DEBUG /OPT:REF /OPT:ICF"
            )
        endif()
    endif()
endif()

set(TINYXML_PUBLIC_HEADERS
    ${TINYXML_SOURCE_DIR}/tinystr.h
    ${TINYXML_SOURCE_DIR}/tinyxml.h
)

target_sources(TinyXML
    PUBLIC
    ${TINYXML_PUBLIC_HEADERS}

    PRIVATE
    ${TINYXML_SOURCE_DIR}/tinystr.cpp
    ${TINYXML_SOURCE_DIR}/tinyxml.cpp
    ${TINYXML_SOURCE_DIR}/tinyxmlerror.cpp
    ${TINYXML_SOURCE_DIR}/tinyxmlparser.cpp
    ${TINYXML_SOURCE_DIR}/xmltest.cpp
)
target_compile_definitions(TinyXML
    PUBLIC
    TIXML_USE_STL
)

if(NOT SKIP_INSTALL_LIBRARIES AND NOT SKIP_INSTALL_ALL)
    install(TARGETS TinyXML
        RUNTIME DESTINATION "${INSTALL_BIN_DIR}"
        ARCHIVE DESTINATION "${INSTALL_LIB_DIR}"
        LIBRARY DESTINATION "${INSTALL_LIB_DIR}"
    )

    if(MSVC)
        if (BUILD_SHARED_LIBS)
            install(FILES $<TARGET_PDB_FILE:TinyXML> DESTINATION "${INSTALL_BIN_DIR}")
        endif()
    endif()
endif()

if(NOT SKIP_INSTALL_HEADERS AND NOT SKIP_INSTALL_ALL)
    install(FILES ${TINYXML_PUBLIC_HEADERS} DESTINATION "${INSTALL_INC_DIR}/tinyxml")
endif()
