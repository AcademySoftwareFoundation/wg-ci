# ICU package details

## Supported platforms
The [documentation](https://unicode-org.github.io/icu/userguide/icu4c/build.html) does suggest that the library is supported on multiple platforms, but the current need for it was Linux only, to satisfy the [QCollator](https://doc.qt.io/qt-5/qcollator.html) backend to Qt5, since the non-ICU Posix backend spammed the console due to missing features.

## Static library
When configured as a static library, it is important to note that an additional preprocessor definition is required, `U_STATIC_IMPLEMENTATION`. The [documentation](https://unicode-org.github.io/icu/userguide/icu4c/build.html#configuring-icu-on-windows) refers to this on Windows only (presumably to distinguish between dllexport and dllimport). However, it was also necessary on Linux static builds to avoid visibility attributes being defined during the library build. Otherwise, linking the ICU static library into a shared library revealed the ICU symbols.

## Consuming
Use the CMake provided [FindICU](https://cmake.org/cmake/help/latest/module/FindICU.html) module.

On Linux static libraries, `pthread` and `dl` are also required for linking, and the order matters for the libraries on the link line: icudata must be last.
