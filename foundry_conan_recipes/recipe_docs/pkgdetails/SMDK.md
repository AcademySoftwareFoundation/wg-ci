# SMDK (Sony MXF Development Kit) package details

## Build prerequisites
### Why using Boost on linux
When building with libstdc++, SMDK requires Boost on Linux. Read further to understand why.
Internally, SMDK uses parts of Boost. A situation where SMDK uses Boost is when _LIBCPP_VERSION is undefined (if using libstdc++), in which case it uses the smart pointers from Boost. To fully understand this situtation, explore the file from the next link: https://a_gitlab_url/libraries/conan/thirdparty/sony/smdk/-/blob/foundry/v4.21.0/linux-x64-x86-release/Distribution/include/bst/shared_ptr.h

SMDK uses the C++ STL when compiling with libc++, not libstdc++, which is the case on Mac and Windows, but libc++ isn't complete for our versions of GCC neither compliant with our Conan profiles. See https://libcxx.llvm.org/#platform-and-compiler-support for what is currently recommended (GCC 12). 

Therefore, on linux platforms SMDK requires Boost. This would not be a problem for Nuke, the only application that depends on SMDK at the moment, as Nuke depends on Boost too.
