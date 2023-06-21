cmake_minimum_required(VERSION 3.0.0)

project(tbb CXX)

file(TO_CMAKE_PATH "${SOURCE_DIR}" CMAKE_SOURCE_DIR)

# ----------------------------------------------------------------------

if(WIN32)
  LIST(APPEND CMAKE_PROGRAM_PATH "${CONAN_GNUMAKEFORWINDOWS_ROOT}/bin")
endif()

find_program(MAKE_TOOL "make")

include(ProcessorCount)
ProcessorCount(NUM_CORES)

include(ExternalProject)
ExternalProject_Add(
  tbb_extern
  PREFIX ${SOURCE_DIR}
  TMP_DIR ${CMAKE_BINARY_DIR}
  BINARY_DIR ${CMAKE_BINARY_DIR}
  DOWNLOAD_COMMAND ""
  BUILD_IN_SOURCE 0
  BUILD_COMMAND ${MAKE_TOOL} -C ${CMAKE_SOURCE_DIR} -j${NUM_CORES} tbb_build_dir=${CMAKE_BINARY_DIR} tbb_build_prefix=tbb $<IF:$<BOOL:${RUN_UNITTESTS}>,test,default>
  CONFIGURE_COMMAND ""
  INSTALL_COMMAND ""
)

# ----------------------------------------------------------------------

install(
  DIRECTORY ${CMAKE_SOURCE_DIR}/include
  DESTINATION .
  PATTERN *.h
)

install(
  FILES
  ${CMAKE_SOURCE_DIR}/LICENSE
  DESTINATION .
)

if(CMAKE_BUILD_TYPE MATCHES Debug)
  set(TBB_CONFIG _debug)
else()
  set(TBB_CONFIG)
endif()

if(WIN32)
  set(TBB_SHARED_LIBRARY_PREFIX bin/)
  set(TBB_SHARED_LIBRARY_SUFFIX .dll)
  set(TBB_IMPORT_LIBRARY_PREFIX lib/)
  set(TBB_IMPORT_LIBRARY_SUFFIX .lib)
  if(CMAKE_BUILD_TYPE MATCHES Debug)
    install(
      FILES
      ${CMAKE_BINARY_DIR}/tbb_debug/tbb_debug.dll
      ${CMAKE_BINARY_DIR}/tbb_debug/tbb_debug.pdb
      ${CMAKE_BINARY_DIR}/tbb_debug/tbbmalloc_debug.dll
      ${CMAKE_BINARY_DIR}/tbb_debug/tbbmalloc_debug.pdb
      ${CMAKE_BINARY_DIR}/tbb_debug/tbbmalloc_proxy_debug.dll
      ${CMAKE_BINARY_DIR}/tbb_debug/tbbmalloc_proxy_debug.pdb
      DESTINATION bin
    )
    install(
      FILES
      ${CMAKE_BINARY_DIR}/tbb_debug/tbb_debug.lib
      ${CMAKE_BINARY_DIR}/tbb_debug/tbbmalloc_debug.lib
      ${CMAKE_BINARY_DIR}/tbb_debug/tbbmalloc_proxy_debug.lib
      DESTINATION lib
    )
  else()
    install(
      FILES
      ${CMAKE_BINARY_DIR}/tbb_release/tbb.dll
      ${CMAKE_BINARY_DIR}/tbb_release/tbb.pdb
      ${CMAKE_BINARY_DIR}/tbb_release/tbbmalloc.dll
      ${CMAKE_BINARY_DIR}/tbb_release/tbbmalloc.pdb
      ${CMAKE_BINARY_DIR}/tbb_release/tbbmalloc_proxy.dll
      ${CMAKE_BINARY_DIR}/tbb_release/tbbmalloc_proxy.pdb
      DESTINATION bin
    )
    install(
      FILES
      ${CMAKE_BINARY_DIR}/tbb_release/tbb.lib
      ${CMAKE_BINARY_DIR}/tbb_release/tbbmalloc.lib
      ${CMAKE_BINARY_DIR}/tbb_release/tbbmalloc_proxy.lib
      DESTINATION lib
    )
  endif()
elseif(UNIX AND NOT APPLE)
  set(TBB_SHARED_LIBRARY_PREFIX lib/lib)
  set(TBB_SHARED_LIBRARY_SUFFIX .so)
  set(TBB_IMPORT_LIBRARY_PREFIX "")
  set(TBB_IMPORT_LIBRARY_SUFFIX "")
  # Note that the .so files here are NOT symbolic links but linker scripts
  if(CMAKE_BUILD_TYPE MATCHES Debug)
    install(
      DIRECTORY ${CMAKE_BINARY_DIR}/tbb_debug/
      DESTINATION lib
      FILES_MATCHING
      PATTERN "libtbb_debug.so*"
      PATTERN "libtbbmalloc_debug.so*"
      PATTERN "libtbbmalloc_proxy_debug.so*"
    )
  else()
    install(
      DIRECTORY ${CMAKE_BINARY_DIR}/tbb_release/
      DESTINATION lib
      FILES_MATCHING
      PATTERN "libtbb.so*"
      PATTERN "libtbbmalloc.so*"
      PATTERN "libtbbmalloc_proxy.so*"
    )
  endif()
elseif(APPLE)
  set(TBB_SHARED_LIBRARY_PREFIX lib/lib)
  set(TBB_SHARED_LIBRARY_SUFFIX .dylib)
  set(TBB_IMPORT_LIBRARY_PREFIX "")
  set(TBB_IMPORT_LIBRARY_SUFFIX "")
  if(CMAKE_BUILD_TYPE MATCHES Debug)
    install(
      FILES
      ${CMAKE_BINARY_DIR}/tbb_debug/libtbb_debug.dylib
      ${CMAKE_BINARY_DIR}/tbb_debug/libtbbmalloc_debug.dylib
      ${CMAKE_BINARY_DIR}/tbb_debug/libtbbmalloc_proxy_debug.dylib
      DESTINATION lib
    )
  else()
    install(
      FILES
      ${CMAKE_BINARY_DIR}/tbb_release/libtbb.dylib
      ${CMAKE_BINARY_DIR}/tbb_release/libtbbmalloc.dylib
      ${CMAKE_BINARY_DIR}/tbb_release/libtbbmalloc_proxy.dylib
      DESTINATION lib
    )
  endif()
else()
  message(FATAL_ERROR "Unsupported OS")
endif()

configure_file(
  config.cmake.in
  TBBConfig.cmake
  @ONLY
)

install(
  FILES
  ${CMAKE_BINARY_DIR}/TBBConfig.cmake
  DESTINATION cmake
)
