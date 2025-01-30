cd MaterialX-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\MaterialX-main --install-prefix %ASWF_DIR%\install -DMATERIALX_BUILD_PYTHON=TRUE 
cmake  --build %ASWF_DIR%\MaterialX-main\build --target install --config Release -v
cd ..\..
