pip install pyside6
pip install PyOpenGL PyOpenGL_accelerate

cd OpenUSD-release
mkdir build
cd build
del CMakeCache.txt
cmake %ASWF_DIR%\OpenUSD-release --install-prefix %ASWF_DIR%\install -DPXR_ENABLE_OPENVDB_SUPPORT=TRUE -DPXR_ENABLE_PYTHON_SUPPORT=TRUE DPXR_ENABLE_MATERIALX_SUPPORT=TRUE -DPXR_BUILD_ALEMBIC_PLUGIN=TRUE -DPXR_BUILD_OPENCOLORIO_PLUGIN=TRUE -DPXR_BUILD_TESTS=FALSE -DPXR_ENABLE_PTEX_SUPPORT=TRUE -DPXR_BUILD_OPENIMAGEIO_PLUGIN=TRUE
cmake  --build %ASWF_DIR%\OpenUSD-release\build --target install --config Release -v --parallel 4
cd ..\..


  -DPXR_ENABLE_OSL_SUPPORT=TRUE