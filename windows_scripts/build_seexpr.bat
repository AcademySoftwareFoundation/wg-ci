cd SeExpr-main
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\SeExpr-main --install-prefix %ASWF_DIR%\install -DUSE_PYTHON=TRUE -DDOXYGEN_EXECUTABLE=%DOXYGEN_BIN_DIR%\doxygen.exe -DBOOST_INCLUDE_DIR=%BOOST_ROOT% -DBOOST_LIB_DIR=%BOOST_ROOT%\libs -DBOOST_PYTHON3_LIB=%BOOST_ROOT%\lib64-msvc-14.3\boost_python310-vc143-mt-x64-1_80.lib
cmake  --build %ASWF_DIR%\SeExpr-main\build --target install --config Release -v
cd ..\..


