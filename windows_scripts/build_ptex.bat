cd ptex-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\ptex-main --install-prefix %ASWF_DIR%\install -DPTEX_BUILD_SHARED_LIBS=TRUE -DPTEX_BUILD_STATIC_LIBS=FALSE 
cmake  --build %ASWF_DIR%\ptex-main\build --target install --config Release -v
cd ..\..
