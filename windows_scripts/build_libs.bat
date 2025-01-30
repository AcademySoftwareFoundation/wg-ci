
cd zlib-1.3.1
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\zlib-1.3.1 --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\zlib-1.3.1\build --target install --config Release -v
cd ..\..

cd c-blosc-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\c-blosc-main --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\c-blosc-main\build --target install --config Release -v
cd ..\..

cd winflexbison-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\winflexbison-master --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\winflexbison-master\build --target install --config Release -v
cd ..\..

cd freeglut-3.6.0
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\freeglut-3.6.0 --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\freeglut-3.6.0\build --target install --config Release -v
cd ..\..




cd pybind11-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\pybind11-master --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\pybind11-master\build --target install --config Release -v
cd ..\..

