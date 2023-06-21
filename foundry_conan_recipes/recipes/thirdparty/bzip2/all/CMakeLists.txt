cmake_minimum_required(VERSION 3.3.0)

project(bzip2 C)

file(TO_CMAKE_PATH "${SOURCE_DIR}" CMAKE_SOURCE_DIR)

# ----------------------------------------------------------------------

if (BUILD_SHARED_LIBS)
  add_library(bz2 SHARED)
else()
  add_library(bz2 STATIC)
endif()

target_sources(bz2
    PRIVATE
    ${CMAKE_SOURCE_DIR}/blocksort.c
    ${CMAKE_SOURCE_DIR}/huffman.c
    ${CMAKE_SOURCE_DIR}/crctable.c
    ${CMAKE_SOURCE_DIR}/randtable.c
    ${CMAKE_SOURCE_DIR}/compress.c
    ${CMAKE_SOURCE_DIR}/decompress.c
    ${CMAKE_SOURCE_DIR}/bzlib.c
)

if(MSVC)
  if (BUILD_SHARED_LIBS)
    set_target_properties(bz2 PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
  endif()
else()
  target_compile_options(bz2 PRIVATE -Wall -Winline)
endif()

target_compile_definitions(bz2 PRIVATE _FILE_OFFSET_BITS=64)

target_include_directories(bz2 INTERFACE $<INSTALL_INTERFACE:include>)

# ----------------------------------------------------------------------

add_executable(bzip2 ${CMAKE_SOURCE_DIR}/bzip2.c)
target_link_libraries(bzip2 PRIVATE bz2)

# ----------------------------------------------------------------------

add_executable(bzip2recover ${CMAKE_SOURCE_DIR}/bzip2recover.c)

# ----------------------------------------------------------------------

install(
  TARGETS bz2 bzip2 bzip2recover
  EXPORT bz2-export
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

install(
  EXPORT bz2-export
  FILE
    bzip2Config.cmake
  NAMESPACE
    bz2::
  DESTINATION
    cmake
)

install(
  FILES ${CMAKE_SOURCE_DIR}/bzlib.h
  DESTINATION include
)

# ----------------------------------------------------------------------

include(FindUnixCommands)
enable_testing()

function(BZipTest name switch input output reference)
  set(TEST_CMD "$<TARGET_FILE:bzip2> ${switch} < ${input} > ${output}")
  if (BASH)
    add_test(
      NAME ${name}
      WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
      COMMAND ${BASH} -c ${TEST_CMD}
    )
  elseif (WIN32)
    add_test(
      NAME ${name}
      WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
      COMMAND ${CMAKE_COMMAND} -E chdir $<TARGET_FILE_DIR:bzip2> $ENV{ComSpec} /c ${TEST_CMD}
    )
  else()
    message(FATAL_ERROR "Unknown shell")
  endif()
  add_test(
    NAME ${name}_compare
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E compare_files ${output} ${reference}
  )
  set_tests_properties(${name}_compare PROPERTIES DEPENDS ${name})
endfunction()

BZipTest(compresstest1 -1  ${CMAKE_SOURCE_DIR}/sample1.ref sample1.rb2 ${CMAKE_SOURCE_DIR}/sample1.bz2)
BZipTest(compresstest2 -2  ${CMAKE_SOURCE_DIR}/sample2.ref sample2.rb2 ${CMAKE_SOURCE_DIR}/sample2.bz2)
BZipTest(compresstest3 -3  ${CMAKE_SOURCE_DIR}/sample3.ref sample3.rb2 ${CMAKE_SOURCE_DIR}/sample3.bz2)
BZipTest(decompresstest1 -d  ${CMAKE_SOURCE_DIR}/sample1.bz2 sample1.tst ${CMAKE_SOURCE_DIR}/sample1.ref)
BZipTest(decompresstest2 -d  ${CMAKE_SOURCE_DIR}/sample2.bz2 sample2.tst ${CMAKE_SOURCE_DIR}/sample2.ref)
BZipTest(decompresstest3 -ds ${CMAKE_SOURCE_DIR}/sample3.bz2 sample3.tst ${CMAKE_SOURCE_DIR}/sample3.ref)
