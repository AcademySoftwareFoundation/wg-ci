# Just set it to something reasonable...
set(TEST_WORKING_DIRECTORY ${CMAKE_BINARY_DIR} PARENT_SCOPE)

find_package(Qt5
    CONFIG
    REQUIRED
    COMPONENTS
        X11Extras   # For Mari, Modo, Nuke.
    NO_SYSTEM_ENVIRONMENT_PATH
)

NonGuiTest(NAME QX11Extras LIBS Qt5::X11Extras)

GuiTest(NAME QMainWindowCheckFonts LIBS Qt5::Widgets QPA_PLATFORM offscreen) # TODO: can't remember why this was offscreen
