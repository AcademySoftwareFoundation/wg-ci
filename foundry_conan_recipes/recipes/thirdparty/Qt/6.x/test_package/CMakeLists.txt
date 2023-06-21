cmake_minimum_required(VERSION 3.12)
project(PackageTest LANGUAGES CXX)

add_subdirectory(license_tests)

find_package(Qt6
    CONFIG
    REQUIRED
    COMPONENTS
        Concurrent
        Core
        DBus
        Designer
        Gui
        Help
        Multimedia
        MultimediaWidgets
        Network
        OpenGL
        Positioning
        PrintSupport
        Qml
        Quick
        QuickWidgets
        Sensors
        Sql
        SvgWidgets
        Test
        WebChannel
        Widgets
        Xml
    NO_SYSTEM_ENVIRONMENT_PATH
)

if(INCLUDES_WEBENGINE)
    find_package(Qt6
        CONFIG
        REQUIRED
        COMPONENTS
            WebEngine
            WebEngineCore
            WebEngineWidgets
        NO_SYSTEM_ENVIRONMENT_PATH
    )
endif()

set(TIMEOUT_FOR_QT_PROG 2000)   # Milliseconds.
set(TIMEOUT_FOR_CTEST 30)   # Seconds.

add_compile_definitions(
    TIMEOUT=${TIMEOUT_FOR_QT_PROG}
)

find_file(QtCONF_FILEPATH NAMES qt.conf PATHS ${CONAN_QT_ROOT}/bin/ NO_DEFAULT_PATH)
if(NOT QtCONF_FILEPATH)
    message(SEND_ERROR "The file qt.conf must exist in " ${CONAN_QT_ROOT} "/bin/ with the correct contents to make Qt relocatable.")
else()
    file(STRINGS ${QtCONF_FILEPATH} QtCONF_CONTENTS)
    list(LENGTH QtCONF_CONTENTS QtCONF_NUM_LINES)
    if(NOT(QtCONF_NUM_LINES EQUAL 2))
        message(SEND_ERROR "The " ${QtCONF_FILEPATH} " file is mal-formed.")
    endif()
endif()

enable_testing()

include(CMakeParseArguments)

if(APPLE)
    set(DEFAULT_QPA_PLATFORM "cocoa")
else()
    set(DEFAULT_QPA_PLATFORM "minimal")
endif()

# common test case creation
macro(_MakeTestCase NAME LIBS DEFS)

    add_executable(${NAME})
    if(EXISTS ${CMAKE_CURRENT_LIST_DIR}/${NAME}.cpp)
        # one test doesn't have a matching source name to the target
        target_sources(${NAME} PRIVATE ${NAME}.cpp)
    endif()

    target_link_libraries(${NAME} PRIVATE ${LIBS})

    target_compile_definitions(${NAME} PRIVATE ${DEFS})

    if(WIN32)
        # executables should be next to the Qt DLLs (and qt.conf) or it might pick up DLLs from your PATH
        set_target_properties(
            ${NAME}
            PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
        )
    endif()

    add_test(NAME ${NAME} WORKING_DIRECTORY ${TEST_WORKING_DIRECTORY} COMMAND ${NAME})

    set_tests_properties(${NAME} PROPERTIES TIMEOUT ${TIMEOUT_FOR_CTEST})

endmacro()

# Create a test case for a non-GUI executable
macro(NonGuiTest)

    set(_OPTIONS_ARGS)
    set(_ONE_VALUE_ARGS NAME)
    set(_MULTI_VALUE_ARGS LIBS DEFS)

    cmake_parse_arguments(_TEST "${_OPTIONS_ARGS}" "${_ONE_VALUE_ARGS}" "${_MULTI_VALUE_ARGS}" ${ARGN})

    _MakeTestCase(${_TEST_NAME} "${_TEST_LIBS}" "${_TEST_DEFS}")

endmacro()

# Create a test case for a GUI executable
macro(GuiTest)

    set(_OPTIONS_ARGS)
    set(_ONE_VALUE_ARGS NAME QPA_PLATFORM) # additional QPA_PLATFORM
    set(_MULTI_VALUE_ARGS LIBS DEFS)

    cmake_parse_arguments(_TEST "${_OPTIONS_ARGS}" "${_ONE_VALUE_ARGS}" "${_MULTI_VALUE_ARGS}" ${ARGN})

    _MakeTestCase(${_TEST_NAME} "${_TEST_LIBS}" "${_TEST_DEFS}")

    if(NOT _TEST_QPA_PLATFORM)
        set(_TEST_QPA_PLATFORM "${DEFAULT_QPA_PLATFORM}")
    endif()

    set_tests_properties(${_TEST_NAME} PROPERTIES ENVIRONMENT "DISPLAY=:0.0" ENVIRONMENT "QT_QPA_PLATFORM=${_TEST_QPA_PLATFORM}")

endmacro()

# Create a test case for a QML executable
macro(QMLTest)

    set(_OPTIONS_ARGS)
    set(_ONE_VALUE_ARGS NAME)
    set(_MULTI_VALUE_ARGS LIBS DEFS SRCS) # additional SRCS

    cmake_parse_arguments(_TEST "${_OPTIONS_ARGS}" "${_ONE_VALUE_ARGS}" "${_MULTI_VALUE_ARGS}" ${ARGN})

    _MakeTestCase(${_TEST_NAME} "${_TEST_LIBS}" "${_TEST_DEFS}")

    target_sources(${_TEST_NAME} PRIVATE ${_TEST_SRCS})

    set_target_properties(${_TEST_NAME} PROPERTIES AUTOMOC ON)

    set_tests_properties(${_TEST_NAME} PROPERTIES ENVIRONMENT "DISPLAY=:0.0" ENVIRONMENT "QT_QPA_PLATFORM=${DEFAULT_QPA_PLATFORM}")

endmacro()

NonGuiTest(NAME QCoreApplication LIBS Qt6::Core)
NonGuiTest(NAME QSQLite LIBS Qt6::Sql)
NonGuiTest(NAME QDesigner LIBS Qt6::Designer)
NonGuiTest(NAME QHelp LIBS Qt6::Help)
NonGuiTest(NAME QSSLSocket LIBS Qt6::Network)
NonGuiTest(NAME QImage LIBS Qt6::Gui DEFS JPEG_IMAGE_FILEPATH="${CMAKE_JPEG_IMAGE_FILEPATH}" PNG_IMAGE_FILEPATH="${CMAKE_PNG_IMAGE_FILEPATH}")
NonGuiTest(NAME QImageReader LIBS Qt6::Gui)
NonGuiTest(NAME QNetwork LIBS Qt6::Network)
NonGuiTest(NAME QWebChannel LIBS Qt6::WebChannel)

GuiTest(NAME QApplication LIBS Qt6::Widgets)
GuiTest(NAME QMainWindow LIBS Qt6::Widgets QPA_PLATFORM offscreen) # TODO: can't remember why this was offscreen
GuiTest(NAME QSVG LIBS Qt6::Widgets Qt6::SvgWidgets DEFS SVG_IMAGE_FILEPATH="${CMAKE_SVG_IMAGE_FILEPATH}")
GuiTest(NAME QQuick LIBS Qt6::Quick DEFS QQuick_main_FILEPATH="${CMAKE_QQuick_main_FILEPATH}")
GuiTest(NAME QQuickWidgets LIBS Qt6::QuickWidgets DEFS QQuick_main_FILEPATH="${CMAKE_QQuick_main_FILEPATH}")

QMLTest(NAME QML LIBS Qt6::Qml Qt6::Gui SRCS QML_BackEnd.cpp QML_Checker.cpp DEFS QML_main_FILEPATH="${CMAKE_QML_main_FILEPATH}")
QMLTest(NAME QGraphicalEffects LIBS Qt6::Qml Qt6::Gui SRCS QML.cpp QML_BackEnd.cpp QML_Checker.cpp DEFS QML_main_FILEPATH="${CMAKE_QGraphicalEffects_main_FILEPATH}") # note, reuses QML.cpp

if(INCLUDES_WEBENGINE)
    GuiTest(NAME QWebEngineView LIBS Qt5::Network Qt5::WebEngineWidgets)
endif()

if(UNIX AND NOT APPLE)
    add_subdirectory(linux)
elseif(APPLE)
    add_subdirectory(apple)
elseif(MSVC)
    add_subdirectory(win)
else()
    message(ERROR "Unknown platform.")
endif()
