if (TARGET Libusb::libusb)
  return()
endif()

get_filename_component(FOLDER "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(FOLDER "${FOLDER}" PATH) #remove cmake

add_library(Libusb::libusb SHARED IMPORTED)

set_target_properties(
    Libusb::libusb
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${FOLDER}/include/libusb-1.0"
        IMPORTED_LOCATION "${FOLDER}/lib/libusb-1.0.so"
)

unset(FOLDER)
