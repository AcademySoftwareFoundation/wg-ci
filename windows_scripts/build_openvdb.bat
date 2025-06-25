cd openvdb-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\openvdb-master --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\openvdb-master\build --target install --config Release -v
cd ..\..
