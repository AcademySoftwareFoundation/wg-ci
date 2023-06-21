# QtSingleApplication package details

## Building

### Build directories
The QtSingleApplication build system does not use the conan specified build directory. Instead it creates a 
`qtsingleapplication/Makefile*` files and `qtsingleapplication/debug` and `qtsingleapplication/release` directories in the `<source directory>/QtSingleApplication_src` directory. This is of particular importance if you are building multiple versions of QtSingleApplication (i.e. OpenGL, FoundryGL), as you many need to clean these directories manually to get a correct build.

### FoundryGL
Unlike other conan packages, this one obtains the `GLBackend` option from the Qt package used.
So to build a FoundryGL variation of `QtSingleApplication` you must overload the `Qt` package option `GLBackend`.
Do this by using the conan option `-o Qt:GLBackend=FoundryGL` when trying to `conan install`.

