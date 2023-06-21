cmake_minimum_required(VERSION 3.12)
project(PackageTest LANGUAGES CXX)

add_subdirectory(license_tests)

find_package(Qt5
    CONFIG
    REQUIRED
    COMPONENTS
        Concurrent  # For Katana, Mari, Modo, Nuke.
        Core    # For Colorway, Katana, Mari, Modo, Nuke.
        DBus    # For Modo. # TODO Needs testing...
        Designer # For Katana.
#       GraphicalEffects # For Colorway. Depends upon QML. Apparently no C++ interface: https://doc.qt.io/qt-5/qtgraphicaleffects-index.html
        Gui # For Katana, Mari, Modo, Nuke.
        Help # For Katana.
        Multimedia  # For Katana, Mari, Modo.
        MultimediaWidgets   # For Modo.
        Network # For Katana, Modo.
        OpenGL  # For Katana, Mari, Modo, Nuke.
        Positioning # For Katana, Modo.
        PrintSupport    # For Mari, Modo.
        Qml  # For Colorway, Mari & Modo.
        Quick    # For Colorway, Katana, Modo.
# TODO - not built yet?        Quick.2  # For Colorway.
        QuickWidgets # For Modo.
        Script  # For Katana, Mari.
        ScriptTools # For Katana, Mari.
        Sensors # For Modo.
        Sql # For Katana, Mari, Modo.
        Svg # For Katana, Mari, Modo.
        Test    # For Katana.
        WebChannel  # For Colorway, Katana, Modo.
        Widgets # For Colorway, Katana, Mari, Modo, Nuke.
# TODO - not built yet?        XcbQpa   # For Modo.
        Xml # For Katana, Mari, Modo, Nuke.
        XmlPatterns # For Katana, Mari.
    NO_SYSTEM_ENVIRONMENT_PATH
)

if(INCLUDES_WEBENGINE)
    find_package(Qt5
        CONFIG
        REQUIRED
        COMPONENTS
            WebEngine    # For Colorway, Modo.
            WebEngineCore    # For Modo.
            WebEngineWidgets # For Katana & Modo.
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
        set(_TEST_QPA_PLATFORM "minimal")
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

    set_tests_properties(${_TEST_NAME} PROPERTIES ENVIRONMENT "DISPLAY=:0.0" ENVIRONMENT "QT_QPA_PLATFORM=minimal")

endmacro()

NonGuiTest(NAME QCoreApplication LIBS Qt5::Core)
NonGuiTest(NAME QSQLite LIBS Qt5::Sql)
NonGuiTest(NAME QDesigner LIBS Qt5::Designer)
NonGuiTest(NAME QHelp LIBS Qt5::Help)
NonGuiTest(NAME QSSLSocket LIBS Qt5::Network)
NonGuiTest(NAME QImage LIBS Qt5::Gui DEFS JPEG_IMAGE_FILEPATH="${CMAKE_JPEG_IMAGE_FILEPATH}" PNG_IMAGE_FILEPATH="${CMAKE_PNG_IMAGE_FILEPATH}")
NonGuiTest(NAME QImageReader LIBS Qt5::Gui)
NonGuiTest(NAME QNetwork LIBS Qt5::Network)
NonGuiTest(NAME QWebChannel LIBS Qt5::WebChannel)

GuiTest(NAME QApplication LIBS Qt5::Widgets)
GuiTest(NAME QMainWindow LIBS Qt5::Widgets QPA_PLATFORM offscreen) # TODO: can't remember why this was offscreen
GuiTest(NAME QSVG LIBS Qt5::Widgets Qt5::Svg DEFS SVG_IMAGE_FILEPATH="${CMAKE_SVG_IMAGE_FILEPATH}")
GuiTest(NAME QQuick LIBS Qt5::Quick DEFS QQuick_main_FILEPATH="${CMAKE_QQuick_main_FILEPATH}")
GuiTest(NAME QQuickWidgets LIBS Qt5::QuickWidgets DEFS QQuick_main_FILEPATH="${CMAKE_QQuick_main_FILEPATH}")

QMLTest(NAME QML LIBS Qt5::Qml Qt5::Gui SRCS QML_BackEnd.cpp QML_Checker.cpp DEFS QML_main_FILEPATH="${CMAKE_QML_main_FILEPATH}")
QMLTest(NAME QGraphicalEffects LIBS Qt5::Qml Qt5::Gui SRCS QML.cpp QML_BackEnd.cpp QML_Checker.cpp DEFS QML_main_FILEPATH="${CMAKE_QGraphicalEffects_main_FILEPATH}") # note, reuses QML.cpp

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

#[[ This can timeout on Windows v5.12.10/Debug, which means there is a race condition on Windows at least. So it has been commented out. See https://a_gitlab_url/libraries/conan/recipes/-/issues/107
add_executable(QConcurrent QConcurrent.cpp)
target_link_libraries(QConcurrent Qt5::Concurrent Qt5::Core)
target_compile_features(QConcurrent PRIVATE cxx_std_11)
add_test(NAME QConcurrent
    WORKING_DIRECTORY ${TEST_WORKING_DIRECTORY}
    COMMAND QConcurrent
)
set_tests_properties(QConcurrent
    PROPERTIES
        TIMEOUT ${TIMEOUT_FOR_CTEST}
)
]]
