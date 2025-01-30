REM ##################### TO BE EDITED FOR A GIVEN ENV  #############################################
SET VS_DIR=C:\Program Files\Microsoft Visual Studio\2022\Community\VC
rem SET CMAKE_DIR=C:\bin\CMake-3.29.2\bin
SET CMAKE_DIR=d:\aswf\cmake-3.29.2-windows-x86_64\bin
SET ASWF_DIR=d:\aswf
set LUA_DIR=d:\aswf\lua-5.4.2_Win64_bin

SET BOOST_ROOT=%ASWF_DIR%\boost_1_80_0
SET PYTHON_HOME=C:\bin\Python310
SET GIT_BIN_DIR=C:\bin\Git\bin
SET TBB_DIR=%ASWF_DIR%\tbb-2020.3-win\tbb
SET PTHREAD_DIR=%ASWF_DIR%\pthreads-w32-2-9-1-release\Pre-built.2
SET DOXYGEN_BIN_DIR=%ASWF_DIR%\doxygen-1.13.2.windows.x64.bin
SET LLVM_ROOT=%ASWF_DIR%\clang+llvm-18.1.4-x86_64-pc-windows-msvc
SET QT_ROOT=%ASWF_DIR%\Qt\5.15.2\msvc2019_64

REM ##################### END                           #############################################



SET VS_VCVARS64_DIR=%VS_DIR%\Auxiliary\Build

call "%VS_VCVARS64_DIR%\vcvars64.bat"
set PATH=%CMAKE_DIR%\;%PYTHON_HOME%\;%PYTHON_HOME%\Scripts\;%GIT_BIN_DIR%\;%LUA_DIR%;%PATH%;%DOXYGEN_BIN_DIR%;%ASWF_DIR%\install\bin;%TBB_DIR%\bin\intel64\vc14;

REM add boost, tbb and pthread to default include and library path
SET INCLUDE_ORG=%INCLUDE%
SET INCLUDE=%TBB_DIR%\include;%BOOST_ROOT%;%PTHREAD_DIR%\include;%INCLUDE_ORG%;%ASWF_DIR%\install\include
SET LIB_ORG=%LIB%
SET LIB=%TBB_DIR%\lib\intel64\vc14;%BOOST_ROOT%\lib64-msvc-14.3;%PTHREAD_DIR%\lib\x64;%LIB_ORG%;%ASWF_DIR%\install\lib



mkdir install
cd install
mkdir include
mkdir lib
mkdir bin
cd ..
