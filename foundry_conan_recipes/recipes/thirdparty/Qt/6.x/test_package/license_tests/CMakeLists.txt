# verify that GPL licensed Qt modules cannot be located via CMake in the package

find_package(Qt6
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

if(NOT Qt6Core_DIR)
    message(FATAL_ERROR "Qt6Core_DIR library was NOT found - this is a very broken Qt6 package")
endif()

if(Qt6Charts_DIR)
    message(FATAL_ERROR "Qt6Charts library was found at '${Qt6Charts_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt6DataVisualization_DIR)
    message(FATAL_ERROR "Qt6DataVisualizationlibrary was found at '${Qt6DataVisualization_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt6NetworkAuth_DIR)
    message(FATAL_ERROR "Qt6NetworkAuth library was found at '${Qt6NetworkAuth_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt6VirtualKeyboard_DIR)
    message(FATAL_ERROR "Qt6VirtualKeyboard library was found at '${Qt6VirtualKeyboard_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt6Wayland_DIR)
    message(FATAL_ERROR "Qt6Wayland library was found at '${Qt6Wayland_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt6Lottie_DIR)
    message(FATAL_ERROR "Qt6Lottie library was found at '${Qt6Lottie_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt6Quick3D_DIR)
    message(FATAL_ERROR "Qt6Quick3D library was found at '${Qt6Quick3D_DIR}' - this is GPL licensed and must not be used")
endif()

if(Qt6QuickTimeline_DIR)
    message(FATAL_ERROR "Qt6QuickTimeline library was found at '${Qt6QuickTimeline_DIR}' - this is GPL licensed and must not be used")
endif()

# TODO: we can also check for plugins here, ala https://cmake.org/pipermail/cmake/2014-August/058371.html
# but I'm 99% sure that if the module associated with a plugin, e.g. wayland, isn't built, then the plugin isn't built

message(STATUS "Qt module CMake license checks complete")
