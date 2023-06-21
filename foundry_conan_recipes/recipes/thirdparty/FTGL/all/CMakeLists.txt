cmake_minimum_required(VERSION 3.13)
project(FTGL VERSION 2.1.3 LANGUAGES CXX)

find_package(Freetype REQUIRED)
find_package(FoundryGL QUIET)
if (NOT FOUNDRYGL_FOUND)
   find_package(OpenGL REQUIRED)
endif()


include (CheckSymbolExists)
check_symbol_exists(wcsdup "wchar.h" HAVE_WCSDUP)
check_symbol_exists(strndup "string.h" HAVE_STRNDUP)
configure_file(config.h.cmake.in ${CMAKE_CURRENT_BINARY_DIR}/config.h @ONLY)

add_library(FTGL STATIC)

target_sources(FTGL
   PRIVATE
      ${FTGL_SRC_PREFIX}/src/FTBuffer.cpp
      ${FTGL_SRC_PREFIX}/src/FTCharmap.cpp
      ${FTGL_SRC_PREFIX}/src/FTContour.cpp
      ${FTGL_SRC_PREFIX}/src/FTFace.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyphContainer.cpp
      ${FTGL_SRC_PREFIX}/src/FTLibrary.cpp
      ${FTGL_SRC_PREFIX}/src/FTPoint.cpp
      ${FTGL_SRC_PREFIX}/src/FTSize.cpp
      ${FTGL_SRC_PREFIX}/src/FTVectoriser.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTGlyphGlue.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTBitmapGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTBufferGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTExtrudeGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTOutlineGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTPixmapGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTPolygonGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTGlyph/FTTextureGlyph.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTFontGlue.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTBitmapFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTBufferFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTExtrudeFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTOutlineFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTPixmapFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTPolygonFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTFont/FTTextureFont.cpp
      ${FTGL_SRC_PREFIX}/src/FTLayout/FTLayout.cpp
      ${FTGL_SRC_PREFIX}/src/FTLayout/FTLayoutGlue.cpp
      ${FTGL_SRC_PREFIX}/src/FTLayout/FTSimpleLayout.cpp
)

target_include_directories(FTGL
   PRIVATE
      ${FTGL_SRC_PREFIX}/src
      ${FTGL_SRC_PREFIX}/src/FTGL
      ${FTGL_SRC_PREFIX}/src/FTGlyph
      ${FTGL_SRC_PREFIX}/src/FTFont
      ${FTGL_SRC_PREFIX}/src/FTLayout
      ${CMAKE_CURRENT_BINARY_DIR}
   PUBLIC
      $<INSTALL_INTERFACE:include>
)

if (APPLE)
   target_compile_definitions(FTGL
      PUBLIC
         GL_SILENCE_DEPRECATION
   )
elseif (MSVC)
   target_compile_definitions(FTGL
      PUBLIC
         FTGL_LIBRARY_STATIC # Static linking.
         _USE_MATH_DEFINES # Ensure that the POSIX-Standard constant "M_PI" is defined in <math.h>.
   )
endif()

target_link_libraries(FTGL PUBLIC Freetype::Freetype $<IF:$<BOOL:${FOUNDRYGL_FOUND}>,FoundryGL::GL,OpenGL::GL>)

set_target_properties(FTGL
   PROPERTIES
      OUTPUT_NAME FnFtgl
)

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
   FTGLConfigVersion.cmake
   COMPATIBILITY AnyNewerVersion
)

install(
   TARGETS FTGL
   EXPORT FTGLTargets
   RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
   ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
   LIBRARY DESTINATION ${CMAKE_INSTALL_LIBEXECDIR}
   PUBLIC_HEADER DESTINATION include/FTGL
   PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE
)
install(
   DIRECTORY ${FTGL_SRC_PREFIX}/src/ ${FTGL_SRC_PREFIX}/src/FTGL/ ${FTGL_SRC_PREFIX}/src/FTGlyph/ ${FTGL_SRC_PREFIX}/src/FTFont/ ${FTGL_SRC_PREFIX}/src/FTLayout/
   DESTINATION include/FTGL
   FILES_MATCHING PATTERN "*.h"
   PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ
)
install(
   EXPORT FTGLTargets
   NAMESPACE FTGL::
   DESTINATION cmake
   PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ
)
install(
   FILES
      FTGLConfig.cmake
      ${CMAKE_CURRENT_BINARY_DIR}/FTGLConfigVersion.cmake
   DESTINATION cmake
   PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ
)
