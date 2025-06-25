cd partio-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\partio-main --install-prefix %ASWF_DIR%\install -DGLUT_ROOT=%ASWF_DIR%\freeglut-3.6.0
cmake  --build %ASWF_DIR%\partio-main\build --target install --config Release -v
cd ..\..