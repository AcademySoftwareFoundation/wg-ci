# verify that GPL licensed Qt modules cannot be located via CMake in the package

find_package(Qt5
    CONFIG
    QUIET # otherwise it is very spammy on the log
    COMPONENTS
        Core
    OPTIONAL_COMPONENTS
        Charts
        DataVisualization
        NetworkAuth
        VirtualKeyboard
        Wayland
        # 5.15+
        Lottie
        Quick3D
        QuickTimeline
    NO_SYSTEM_ENVIRONMENT_PATH
)

if(NOT Qt5Core_DIR)
    message(FATAL_ERROR "Qt5Core_DIR library was NOT found - this is a very broken Qt5 package")
endif()

if(Qt5Charts_DIR)
    message(FATAL_ERROR "Qt5Charts library was found at '${Qt5Charts_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt5DataVisualization_DIR)
    message(FATAL_ERROR "Qt5DataVisualizationlibrary was found at '${Qt5DataVisualization_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt5NetworkAuth_DIR)
    message(FATAL_ERROR "Qt5NetworkAuth library was found at '${Qt5NetworkAuth_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt5VirtualKeyboard_DIR)
    message(FATAL_ERROR "Qt5VirtualKeyboard library was found at '${Qt5VirtualKeyboard_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt5Wayland_DIR)
    message(FATAL_ERROR "Qt5Wayland library was found at '${Qt5Wayland_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt5Lottie_DIR)
    message(FATAL_ERROR "Qt5Lottie library was found at '${Qt5Lottie_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt5Quick3D_DIR)
    message(FATAL_ERROR "Qt5Quick3D library was found at '${Qt5Quick3D_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt5QuickTimeline_DIR)
    message(FATAL_ERROR "Qt5QuickTimeline library was found at '${Qt5QuickTimeline_DIR}' - this is GPL licensed and must not be used")
endif()

# TODO: we can also check for plugins here, ala https://cmake.org/pipermail/cmake/2014-August/058371.html
# but I'm 99% sure that if the module associated with a plugin, e.g. wayland, isn't built, then the plugin isn't built

message(STATUS "Qt module CMake license checks complete")
