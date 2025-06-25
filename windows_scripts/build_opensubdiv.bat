cd OpenSubdiv-release
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\OpenSubdiv-release --install-prefix %ASWF_DIR%\install -DNO_DX=TRUE
cmake  --build %ASWF_DIR%\OpenSubdiv-release\build --target install --config Release -v
cd ..\..