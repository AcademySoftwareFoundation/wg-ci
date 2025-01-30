git clone https://github.com/AcademySoftwareFoundation/MaterialX MaterialX-main

cd MaterialX-main
git submodule update --init --recursive
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\MaterialX-main --install-prefix %ASWF_DIR%\install -DMATERIALX_BUILD_PYTHON=TRUE -DMATERIALX_BUILD_VIEWER=TRUE
cmake  --build %ASWF_DIR%\MaterialX-main\build --target install --config Release -v
cd ..\..
