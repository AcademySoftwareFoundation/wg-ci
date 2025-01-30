cd openexr-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\openexr-main --install-prefix %ASWF_DIR%\install -DBUILD_SHARED_LIBS=FALSE -DPYBIND11=TRUE
cmake  --build %ASWF_DIR%\openexr-main\build --target install --config Release -v
cd ..\..


cd openexr-3.3.2
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\openexr-3.3.2 --install-prefix %ASWF_DIR%\install -DBUILD_SHARED_LIBS=FALSE -DOPENEXR_BUILD_PYTHON=TRUE
cmake  --build %ASWF_DIR%\openexr-3.3.2\build --target install --config Release -v
cd ..\..

