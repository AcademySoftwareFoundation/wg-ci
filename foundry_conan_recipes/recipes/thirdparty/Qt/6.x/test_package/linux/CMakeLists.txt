# Just set it to something reasonable...
set(TEST_WORKING_DIRECTORY ${CMAKE_BINARY_DIR} PARENT_SCOPE)

find_package(Qt6 CONFIG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

GuiTest(NAME QMainWindowCheckFonts LIBS Qt6::Widgets QPA_PLATFORM offscreen) # TODO: can't remember why this was offscreen
