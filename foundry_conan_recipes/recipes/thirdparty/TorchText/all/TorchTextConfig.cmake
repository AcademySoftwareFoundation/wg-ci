if(TARGET TorchText::TorchText)
  return()
endif()

if (CMAKE_VERSION VERSION_LESS 3.18)
  message(FATAL_ERROR "TorchText requires at least CMake version 3.18")
endif()
get_filename_component(_torchtext_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

message(STATUS "Found TorchText: ${_torchtext_install_prefix}")

include(CMakeFindDependencyMacro)
find_dependency(Torch REQUIRED)

add_library(TorchText::TorchText IMPORTED SHARED)

set(TORCHTEXT_LINK_LIBS "torch;torch_cpu")
if(CMAKE_SYSTEM_PROCESSOR MATCHES "(AMD64|x86_64)")
  list(APPEND TORCHTEXT_LINK_LIBS MKL::Intel)
  if(UNIX AND NOT APPLE)
    list(APPEND TORCHTEXT_LINK_LIBS MKL::RT)
  endif()
endif()

set(TORCHTEXT_LIBNAME libtorchtext)
set_target_properties(
    TorchText::TorchText
    PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${_torchtext_install_prefix}/include
    INTERFACE_LINK_LIBRARIES "${TORCHTEXT_LINK_LIBS}"
    IMPORTED_LOCATION ${_torchtext_install_prefix}/lib/${TORCHTEXT_LIBNAME}${CMAKE_SHARED_LIBRARY_SUFFIX}
)

target_compile_features(TorchText::TorchText INTERFACE cxx_std_14 c_std_11)

if(MSVC)
  set_target_properties(
    TorchText::TorchText
    PROPERTIES
    IMPORTED_IMPLIB ${_torchtext_install_prefix}/lib/${TORCHTEXT_LIBNAME}.lib
  )
endif()

unset(TORCHTEXT_LIBNAME)
unset(TORCHTEXT_LINK_LIBS)
