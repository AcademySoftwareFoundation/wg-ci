cmake_minimum_required(VERSION 3.1)
project(ImGuiTest CXX)

find_package(IMGUI REQUIRED)

add_executable(ImGuiTest ImGuiTest.cpp)
target_link_libraries(ImGuiTest
    PRIVATE
    IMGUI::IMGUI
)

enable_testing()
add_test(NAME ImGuiTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND ImGuiTest)

if (MSVC)
    set_tests_properties(ImGuiTest PROPERTIES ENVIRONMENT "PATH=${CONAN_IMGUI_ROOT}/bin;$ENV{PATH}")
endif()
