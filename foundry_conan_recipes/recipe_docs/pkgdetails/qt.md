# Qt 5.x package details

## Local conan usage
The Qt recipe uses the Qt qmake build system underneath, instead of the more typical CMake system. Due to this some of the conan build steps have to be specifically done.

If using `conan create ...` then everything should work.

If using `conan [install|source|build|package|export-pkg]` then some specifics have to be done.
If using a custom `<package directory>` then it must be supplied as a command line parameter to `conan [build|package|export-pkg]` stages. The `export-pkg` stage should **not** be supply the `<build directory>` or the `<source directory>`. Due to these requirements you **will** have to run `package` and then the `export-pkg` stages, in order, to get a complete package uploaded to conan home. 

When building on Windows, make sure to keep short location paths to avoid issues with [Windows MAX_PATH of 260 characters](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation).


## Known RPMs required to build
### Linux for X11Extras
* xcb-util-wm-devel
* xcb-util-devel
* xcb-util-image-devel
* xcb-util-keysyms-devel
* xcb-util-renderutil-devel

### WebEngine
* nss-devel
* libXcomposite-devel
* libXtst-devel
* ibXdamage-devel
