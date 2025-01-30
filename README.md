# Compiling ASWF (and related) libraries on windows (with Visual Studio 2022)
this document describes the steps to compile 
OpenSubdiv, ptex, seexpr, partio, alembic, OpenExr, OpenVdb, MaterialX, OpenColorIO, OpenImageIO, OpenTimelineIO, OpenFx, OpenShadingLanguage and OpenUSD. Without VC22 and windows sdk, compiling all the libraries requires 30 GB of disc space and take a day or two to complete. All the libraries are compiled on the same directory (D:\ASWF for me, but fill free to choose whatever suits your environment).

## Prerequisite
- download and install vc22 (community edition) if not already done.
- download and install windows sdk
- downlaod and unzip cmake: https://github.com/Kitware/CMake/releases/download/v3.29.2/cmake-3.29.2-windows-x86_64.zip
- create the installation directory (D:\ASWF) and copy the .bat files provided there.
- download pre built boost: https://sourceforge.net/projects/boost/files/boost-binaries/1.80.0/boost_1_80_0-msvc-14.3-64.exe/download
installtion take some time.
 
- download and unzip doxygen: https://www.doxygen.nl/download.html
- download and unzip prebuild llvm : https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.4/clang+llvm-18.1.4-x86_64-pc-windows-msvc.tar.xz
- dowload and unzip pthread: http://mirrors.kernel.org/sourceware/pthreads-win32/pthreads-w32-2-9-1-release.zip

- download and unzip tbb: https://github.com/uxlfoundation/oneTBB/releases/download/v2020.3/tbb-2020.3-win.zip

- edit the build_setup.bat file, and set pathes between the 2 
`REM #####################`
## libraries
This the libraries that are needed. Some are used by one of the target, some by many. There are compiled by the bat scripts the first time there are needed. So, for example, go to https://github.com/pybind/pybind11/tree/master, click on the code button, downlad as zip, and unzip the file in the main folder (that will create a pybind11-master folder).
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
Everythink is installed in the "install" directory.

### openexr: 
- download https://github.com/AcademySoftwareFoundation/openexr
(code->download as zip, unzip in the main folder)
- launch `build_openex`
- 
- test: download from https://polyhaven.com/a/qwantani_afternoon in the 'samples' folder
        run `exrinfo samples\qwantani_afternoon_4k.exr`
### openSubdiv: 
- download https://github.com/PixarAnimationStudios/OpenSubdiv
- run `build_opensubdiv'
- test: run `install\bin\tutorials\osd_tutorial_0.exe`
### ptex:
- downlaod https://github.com/wdas/ptex
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

### openvdb:
 - download https://github.com/AcademySoftwareFoundation/openvdb
 - run `build_openvdb`
 - test: download from https://www.openvdb.org/download/ the fire  sample at the bottom of the page and unzip it in the 'samples' folder
   - run `vdb_print samples\fire.vdb with 
### materialx: 
  there are 2 build scripts for materialx: 'build_materialx.bat' and 'build_materialx_git.bat'.

  the first one works on an unziped file, but is missing viewer libraries, so it buids the libraries and the python bindings, but not the viewer.

  the second one use git to download materialx sources and dependencies and build materilax libraries, python binding and the viewer.
  #### Without viewer
- download https://github.com/AcademySoftwareFoundation/MaterialX
- run `build_materialx`
 
  #### With viewer
- run `build_materialx_git`
- test: run `MaterialXView.exe`
### opencolorio: 
- download https://github.com/AcademySoftwareFoundation/OpenColorIO
- run `build_opencolorio`
### openimageio: 
- download https://github.com/AcademySoftwareFoundation/OpenImageIO
- run `build_openimageio`
- note:  building test result in a never ending compilation of src/util/smid_text.cpp, so the library is built without the tests.
### opentimelineio: 
- download https://github.com/AcademySoftwareFoundation/OpenTimelineIO
- run `build_opentimelineio`
### openfx: 
- download https://github.com/AcademySoftwareFoundation/openfx
- run `build_openfx`
### partio: 
- download https://github.com/wdas/partio
- run `build_partio`
### openshadinglanguage: 
- download https://github.com/AcademySoftwareFoundation/OpenShadingLanguage
- run`build_osl`
### alembic: 
- download https://github.com/alembic/alembic
- run `build_alembic`
### openusd: 
- download https://github.com/PixarAnimationStudios/OpenUSD
- run `build_openusd`

## Conclusion
If everything worked properly, you have in the 'install' directory all the libraries, dlls and include files necessary to link one of the ASWF library to your own programs.



