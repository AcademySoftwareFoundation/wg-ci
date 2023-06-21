cmake_minimum_required(VERSION 3.1)

project(ImGui)

set(INSTALL_BIN_DIR "${CMAKE_INSTALL_PREFIX}/bin" CACHE PATH "Installation directory for executables")
set(INSTALL_LIB_DIR "${CMAKE_INSTALL_PREFIX}/lib" CACHE PATH "Installation directory for libraries")
set(INSTALL_INC_DIR "${CMAKE_INSTALL_PREFIX}/include" CACHE PATH "Installation directory for headers")

if (BUILD_SHARED_LIBS)
    add_library(imgui SHARED)
else()
    add_library(imgui STATIC)
endif()

if (MSVC)
    if (BUILD_SHARED_LIBS)
        set_target_properties(imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

        if (CMAKE_BUILD_TYPE MATCHES "Release")
            target_compile_options(imgui PRIVATE /Zi)
            set_target_properties(imgui PROPERTIES
                LINK_FLAGS "/INCREMENTAL:NO /DEBUG /OPT:REF /OPT:ICF"
            )
        endif()
    endif()
endif()

file(GLOB IMGUI_PUBLIC_HEADERS ${CMAKE_SOURCE_DIR}/*.h)
file(GLOB IMGUI_SOURCE_FILES ${CMAKE_SOURCE_DIR}/*.cpp)

target_sources(imgui
    PRIVATE
    ${IMGUI_SOURCE_FILES}
)

if (NOT SKIP_INSTALL_LIBRARIES AND NOT SKIP_INSTALL_ALL)
    install(TARGETS imgui
        RUNTIME DESTINATION "${INSTALL_BIN_DIR}"
        ARCHIVE DESTINATION "${INSTALL_LIB_DIR}"
        LIBRARY DESTINATION "${INSTALL_LIB_DIR}"
    )
    if (MSVC)
        if (BUILD_SHARED_LIBS)
            install(FILES $<TARGET_PDB_FILE:imgui> DESTINATION "${INSTALL_LIB_DIR}")
        endif()
    endif()
endif()

if (NOT SKIP_INSTALL_HEADERS AND NOT SKIP_INSTALL_ALL)
    install(FILES ${IMGUI_PUBLIC_HEADERS} DESTINATION "${INSTALL_INC_DIR}")
endif()
