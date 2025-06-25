
cd pugixml-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\pugixml-master --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\pugixml-master\build --target install --config Release -v
cd ..\..


cd libxml2-2.10.4\win32
cscript configure.js compiler=msvc prefix=%ASWF_DIR%\install iconv=no static=yes
nmake -f Makefile.msvc
nmake -f Makefile.msvc install
cd ..\..
copy %ASWF_DIR%\install\lib\libxml2_a.lib %ASWF_DIR%\install\lib\libxml2s.lib 
copy %ASWF_DIR%\install\lib\libxml2_a.lib %LLVM_ROOT%\lib\libxml2s.lib 




call build_osl_raw.bat
 