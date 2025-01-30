# Compiling ASWF (and related) libraries on windows (with Visual Studio 2022)
This document describes the steps to compile 
OpenSubdiv, ptex, seexpr, partio, alembic, OpenExr, OpenVdb, MaterialX, OpenColorIO, OpenImageIO, OpenTimelineIO, OpenFx, OpenShadingLanguage and OpenUSD. 
Without VC22 and windows sdk, compiling all the libraries requires 30 GB of disc space and take a day or two to complete. All the libraries are compiled on the same directory (D:\ASWF for me, but fill free to choose whatever suits your environment, if possible without a space in the path).

## Prerequisite
- download and install vc22 (community edition) if not already done.
- download and install windows sdk.
- download and unzip cmake: https://github.com/Kitware/CMake/releases/download/v3.29.2/cmake-3.29.2-windows-x86_64.zip
- create the installation directory (D:\ASWF for example) and copy the .bat files provided in the 'windows_scripts' folder.
- download prebuild boost: https://sourceforge.net/projects/boost/files/boost-binaries/1.80.0/boost_1_80_0-msvc-14.3-64.exe/download
installation take some time.
 
- download and unzip doxygen: https://www.doxygen.nl/download.html
- download and unzip prebuild LLVM : https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.4/clang+llvm-18.1.4-x86_64-pc-windows-msvc.tar.xz
- download and unzip pthread: http://mirrors.kernel.org/sourceware/pthreads-win32/pthreads-w32-2-9-1-release.zip

- download and unzip TBB: https://github.com/uxlfoundation/oneTBB/releases/download/v2020.3/tbb-2020.3-win.zip

- edit the build_setup.bat file, and set paths between the 2 `REM #####################`

## libraries
These are the needed libraries to compile everything. Some are used by one of the target, some by many. They are compiled by the 'bat' scripts the first time there are needed. So, for example, go to https://github.com/pybind/pybind11/tree/master, click on the code button, download as zip, and unzip the file in the main folder (that will create a pybind11-master folder).
- zlib: https://www.zlib.net/zlib-1.3.1.tar.gz
- pybind11: https://github.com/pybind/pybind11/tree/master
- blosc: https://github.com/Blosc/c-blosc
- flex&bison: https://github.com/lexxmark/winflexbison
- glew: https://github.com/nigels-com/glew/releases/download/glew-2.2.0/glew-2.2.0-win32.zip
- glut: https://github.com/freeglut/freeglut/releases/download/v3.6.0/freeglut-3.6.0.tar.gz

- libtiff: https://gitlab.com/libtiff/libtiff
- libjpeg-turbo: https://github.com/libjpeg-turbo/libjpeg-turbo
- libpng: https://sourceforge.net/projects/libpng/
- webp: https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.5.0.tar.gz  
- freetype: https://gitlab.freedesktop.org/freetype/freetype

- rapidjson: https://github.com/Tencent/rapidjson/

- expat: https://github.com/libexpat/libexpat
- pugixml: https://github.com/zeux/pugixml
- lib2xml: https://download.gnome.org/sources/libxml2/2.10/libxml2-2.10.4.tar.xz

## ASWF, Disney and Pixar libraries
Open a command prompt. Go to the directory where the libraries are being compiled. First, launch `build_setup`. All the steps should be executed in this command prompt. If not, build_setup should be relaunched to setup the compilation environment.
Everything is installed in the "install" directory.

### Some Libraries
- run `build_libs` to compiled some of the needed libraries, already downloaded.

### OpenEXR: 
- download https://github.com/AcademySoftwareFoundation/openexr
(code->download as zip, unzip in the main folder)
- launch `build_openex`
- test: download from https://polyhaven.com/a/qwantani_afternoon in the 'samples' folder
        run `exrinfo samples\qwantani_afternoon_4k.exr`

### OpenSubdiv: 
- download https://github.com/PixarAnimationStudios/OpenSubdiv
- run `build_opensubdiv'
- test: run `install\bin\tutorials\osd_tutorial_0.exe`

### ptex:
- download https://github.com/wdas/ptex
- run `build_ptex`
- test: download from https://ptex.us/samples/teapot.zip and unzip it in the 'samples' folder
  - run `ptxinfo samples\teapot\teapot.ptx`
- note: ptex build has a problem: Ptex.lib is used for dynamic lib and the static lib... so, only one can be built! The dynamic one is built here.
 
### seexpr: 
- download https://github.com/wdas/SeExpr
- edit file: SeExpr-main\src\SeExpr2\Platform.hpp, line 81, 
  - comment line:
    > inline double log2(double x) { return log(x) * 1.4426950408889634; }
- run `build_seexpr`
- test: run `asciiCalc2`

### OpenVDB:
 - download https://github.com/AcademySoftwareFoundation/openvdb
 - run `build_openvdb`
 - test: download from https://www.openvdb.org/download/ the fire  sample at the bottom of the page and unzip it in the 'samples' folder
   - run `vdb_print samples\fire.vdb with 

### MaterialX: 
  There are 2 build scripts for MaterialX: 'build_materialx.bat' and 'build_materialx_git.bat'.

  The first one works on an unzipped file, but is missing viewer libraries, so it builds the libraries and the python bindings, but not the viewer.

  The second one use git to download MaterialX sources and dependencies and build MaterialX libraries, python binding and the viewer.
#### Without viewer:
- download https://github.com/AcademySoftwareFoundation/MaterialX
- run `build_materialx`
 
#### With viewer:
- run `build_materialx_git`
- test: run `MaterialXView.exe`

### OpenColorIO: 
- download https://github.com/AcademySoftwareFoundation/OpenColorIO
- run `build_opencolorio`

### OpenImageIO: 
- download https://github.com/AcademySoftwareFoundation/OpenImageIO
- run `build_openimageio`
- note:  building test result in a never ending compilation of src/util/smid_text.cpp, so the library is built without the tests.

### OpenTimelineIO: 
- download https://github.com/AcademySoftwareFoundation/OpenTimelineIO
- run `build_opentimelineio`

### OpenFX: 
- download https://github.com/AcademySoftwareFoundation/openfx
- run `build_openfx`

### partio: 
- download https://github.com/wdas/partio
- run `build_partio`

### OpenShadingLanguage: 
- download https://github.com/AcademySoftwareFoundation/OpenShadingLanguage
- run `build_osl`

### alembic: 
- download https://github.com/alembic/alembic
- run `build_alembic`

### OpenUSD: 
- download https://github.com/PixarAnimationStudios/OpenUSD
- run `build_openusd`

## Conclusion
If everything worked properly, you have in the 'install' directory all the libraries, dlls and include files necessary to link one of the ASWF library to your own programs.



