cmake_minimum_required(VERSION 3.10)
project(QtJSON)

find_package(Qt5 REQUIRED COMPONENTS Core)

add_library(QtJSON STATIC
  ${QtJSON_SRC_PREFIX}/json.cpp
)
target_include_directories(QtJSON
  PUBLIC
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(QtJSON PUBLIC Qt5::Core)

install(
  TARGETS QtJSON
  EXPORT QtJSONTargets
  ARCHIVE DESTINATION lib
)
install(
  FILES ${QtJSON_SRC_PREFIX}/json.h
  DESTINATION include
)

configure_file(QtJSONConfig.cmake.in QtJSONConfig.cmake @ONLY)
install(
  FILES ${CMAKE_CURRENT_BINARY_DIR}/QtJSONConfig.cmake
  DESTINATION cmake
)
install(
  EXPORT QtJSONTargets
  NAMESPACE QtJSON::
  DESTINATION cmake
)
