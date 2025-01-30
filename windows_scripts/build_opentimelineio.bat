cd rapidjson-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\rapidjson-master --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\rapidjson-master\build --target install --config Release -v
cd ..\..


cd OpenTimelineIO-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\OpenTimelineIO-main --install-prefix %ASWF_DIR%\install -DOTIO_IMATH_LIBS=%ASWF_DIR%\install -DCMAKE_CXX_FLAGS="/I%ASWF_DIR%\install\include\Imath /I%ASWF_DIR%\install\include"
cmake  --build %ASWF_DIR%\OpenTimelineIO-main\build --target install --config Release -v
cd ..\..