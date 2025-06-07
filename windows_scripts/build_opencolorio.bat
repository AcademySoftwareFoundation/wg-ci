cd OpenColorIO-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\OpenColorIO-main --install-prefix %ASWF_DIR%\install -DGLEW_ROOT=%ASWF_DIR%\glew-2.2.0 -DGLUT_ROOT=%ASWF_DIR%\freeglut-3.6.0
cmake  --build %ASWF_DIR%\OpenColorIO-main\build --target install --config Release -v
cd ..\..