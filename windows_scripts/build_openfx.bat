
cd libexpat-master\expat
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\libexpat-master\expat --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\libexpat-master\expat\build --target install --config Release -v
cd ..\..\..

python -mpip install conan
cd openfx-main
call conan install -s build_type=Release -pr:b=default --build=missing .
cmake --preset conan-default -DBUILD_EXAMPLE_PLUGINS=TRUE --install-prefix %ASWF_DIR%\install 
cmake --build build --config Release --parallel
cmake --build build --target install --config Release
cd ..
