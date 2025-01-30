cd libjpeg-turbo-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\libjpeg-turbo-main --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\libjpeg-turbo-main\build --target install --config Release -v
cd ..\..


cd libpng-1.6.43
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\libpng-1.6.43 --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\libpng-1.6.43\build --target install --config Release -v
cd ..\..


cd libwebp-1.5.0
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\libwebp-1.5.0 --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\libwebp-1.5.0\build --target install --config Release -v
cd ..\..

cd libtiff-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\libtiff-master --install-prefix %ASWF_DIR%\install -Dwebp=FALSE
cmake  --build %ASWF_DIR%\libtiff-master\build --target install --config Release -v
cd ..\..


cd freetype-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\freetype-master --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\freetype-master\build --target install --config Release -v
cd ..\..


cd OpenImageIO-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\OpenImageIO-main --install-prefix %ASWF_DIR%\install -DBUILD_SHARED_LIBS=1 -DBUILD_TESTING=0 -DCMAKE_CXX_STANDARD=17
cmake  --build %ASWF_DIR%\OpenImageIO-main\build --target install --config Release -v
cd ..\..
