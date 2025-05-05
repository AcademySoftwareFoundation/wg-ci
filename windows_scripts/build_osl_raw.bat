rem SET PATH=%PATH%;%ASWF_DIR%\OpenShadingLanguage-main\build\bin\Release;%ASWF_DIR%\OpenShadingLanguage-main\build\lib\Release;%ASWF_DIR%\install\lib;%ASWF_DIR%\install\bin;%TBB_DIR%\bin\intel64\vc14
cd OpenShadingLanguage-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\OpenShadingLanguage-main --install-prefix %ASWF_DIR%\install -DBUILD_SHARED_LIBS=FALSE -DCLANG_FORMAT_EXE="%ASWF_DIR%\clang+llvm-18.1.4-x86_64-pc-windows-msvc\bin\clang-format.exe" -DCMAKE_SHARED_LINKER_FLAGS="/LIBPATH:%ASWF_DIR%\install\lib" -DCMAKE_STATIC_LINKER_FLAGS="/LIBPATH:%ASWF_DIR%\install\lib" -DCMAKE_CXX_STANDARD=17 -DBUILD_TESTING=FALSE
 CMAKE_SHARED_LINKER_FLAGS

cmake  --build %ASWF_DIR%\OpenShadingLanguage-main\build --target install --config Release -v --parallel 4
cd ..\..
