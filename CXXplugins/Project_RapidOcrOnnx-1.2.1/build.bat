@ECHO OFF
chcp 65001
cls
@SETLOCAL
echo "========请先参考README.md准备好编译环境========"
echo.

set BUILD_TYPE=Release

set BUILD_OUTPUT="BIN"

set MT_ENABLED="True"

set ONNX_TYPE="CPU"

echo "VS版本: 1)vs2019-x64, 2)vs2019-x86"
set BUILD_CMAKE_T="v142"
set BUILD_CMAKE_A="x64"
set /p flag=
if %flag% == 1 (
    set BUILD_CMAKE_T="v142"
    set BUILD_CMAKE_A="x64"
)^
else if %flag% == 2 (
    set BUILD_CMAKE_T="v142"
    set BUILD_CMAKE_A="Win32"
)^
else (echo 输入错误！Input Error!)
echo.

mkdir win-%BUILD_OUTPUT%-%ONNX_TYPE%-%BUILD_CMAKE_A%
pushd win-%BUILD_OUTPUT%-%ONNX_TYPE%-%BUILD_CMAKE_A%

cmake -T "%BUILD_CMAKE_T%,host=x64" -A %BUILD_CMAKE_A% ^
  -DCMAKE_INSTALL_PREFIX=install ^
  -DCMAKE_BUILD_TYPE=%BUILD_TYPE% -DOCR_OUTPUT=%BUILD_OUTPUT% ^
  -DOCR_BUILD_CRT=%MT_ENABLED% -DOCR_ONNX=%ONNX_TYPE% ..
cmake --build . --config %BUILD_TYPE% -j %NUMBER_OF_PROCESSORS%
cmake --build . --config %BUILD_TYPE% --target install

popd
GOTO:EOF

@ENDLOCAL
