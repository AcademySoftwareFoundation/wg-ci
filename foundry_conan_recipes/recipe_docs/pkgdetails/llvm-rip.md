# LLVM-RIP package details

### Package overview
The LLVM-RIP package is a patched build of LLVM, clang and lld specifically set for statically linking against RIP. 
The patches applied to LLVM-RIP add or change behaviour in LLVM to suite the needs of RIP and enable compilation across our different build environments. 
The CMake directives enable/disable LLVM targets/tools based on whether we need them to minimise package size.

### CMake configuration
The CMake configuration documentation of LLVM can be found here: https://www.llvm.org/docs/CMake.html


### Building/usage difficulties
LLVM is quite the beast. During creation of this recipe numerous hurdles were overcome to get it building:
- LLVM is huge, especially the debug builds. Various timeouts were increased in order to give LLVM enough time to finish building/uploading (15-50GB ballpark depending on architecture targets).
- Some executables use an enormous amount of memory while linking. Machines with insufficient memory will fall over. This has been mitigated by setting LLVM_PARALLEL_LINK_JOBS=1 and by increasing the size of the build machine's swap drive.
- Set LLVM_ENABLE_RTTI=ON otherwise dynamically linking against RIP on macOSX and linux can randomly fail and complain about missing type_info. This issue is incredibly difficult to debug so, future developers please keep this enabled.
