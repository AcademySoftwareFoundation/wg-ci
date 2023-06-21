cmake_minimum_required(VERSION 3.0)
project(Minizip)

set(CMAKE_DEBUG_POSTFIX "_d")
find_package(zlib REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

set(MINIZIP_SRC
  "${MINIZIP_SRC_PREFIX}ioapi.c"
  "${MINIZIP_SRC_PREFIX}unzip.c"
  "${MINIZIP_SRC_PREFIX}zip.c")

set(MINIZIP_PUBLIC_HEADERS
  "${MINIZIP_SRC_PREFIX}crypt.h"
  "${MINIZIP_SRC_PREFIX}unzip.h"
  "${MINIZIP_SRC_PREFIX}ioapi.h"
  "${MINIZIP_SRC_PREFIX}zip.h")


if(WIN32)
  list(APPEND MINIZIP_SRC "${MINIZIP_SRC_PREFIX}iowin32.c")
  list(APPEND MINIZIP_PUBLIC_HEADERS "${MINIZIP_SRC_PREFIX}iowin32.h")
endif()

add_library(Minizip STATIC ${MINIZIP_SRC})
set_target_properties(Minizip PROPERTIES PREFIX "lib")
target_link_libraries(Minizip zlib::zlib)

install(TARGETS Minizip
  RUNTIME DESTINATION "bin"
  LIBRARY DESTINATION "lib"
  ARCHIVE DESTINATION "lib")

install(FILES
    ${MINIZIP_PUBLIC_HEADERS}
    DESTINATION "include/minizip")
