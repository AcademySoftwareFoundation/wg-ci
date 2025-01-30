cd alembic-master
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\alembic-master --install-prefix %ASWF_DIR%\install 
cmake  --build %ASWF_DIR%\alembic-master\build --target install --config Release -v
cd ..\..
