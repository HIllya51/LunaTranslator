@ECHO OFF
chcp 65001
cls
@SETLOCAL
echo "========请先参考README.md准备好编译环境========"
echo.

echo "========编译选项========"
echo "请注意：项目默认使用Release库，除非您自行编译Debug版的Onnxruntime和Opencv，否则请不要选择Debug编译"
echo "请输入编译选项并回车: 1)Release, 2)Debug"
set BUILD_TYPE=Release
set /p flag=
if %flag% == 1 (set BUILD_TYPE=Release)^
else if %flag% == 2 (set BUILD_TYPE=Debug)^
else (echo 输入错误！Input Error!)
echo.

echo "请注意：如果选择2)JNI动态库时，必须安装配置Oracle JDK"
echo "请选择编译输出类型并回车: 1)BIN可执行文件，2)JNI动态库，3)C动态库"
set /p flag=
if %flag% == 1 (set BUILD_OUTPUT="BIN")^
else if %flag% == 2 (set BUILD_OUTPUT="JNI")^
else if %flag% == 3 (set BUILD_OUTPUT="CLIB")^
else (echo 输入错误！Input Error!)
echo.

echo "引用的库类型: 1)静态CRT(mt), 2)动态CRT(md)"
echo "注意：范例工程默认集成mt版库"
set /p flag=
if %flag% == 1 (
    set MT_ENABLED="True"
)^
else (set MT_ENABLED="False")
echo.

echo "onnxruntime: 1)CPU(默认), 2)GPU(cuda)"
echo "注意：范例工程默认集成CPU版，CUDA版仅支持x64且需下载"
set /p flag=
if %flag% == 1 (set ONNX_TYPE="CPU")^
else if %flag% == 2 (set ONNX_TYPE="CUDA")^
else (echo 输入错误！Input Error!)
echo.

echo "请输入选项并回车: 0)ALL, 1)vs2019-x86, 2)vs2019-x64:"
set /p flag=
if %flag% == 0 (call :buildALL)^
else if %flag% == 1 (call :gen2019-x86)^
else if %flag% == 2 (call :gen2019-x64)^
else (echo "输入错误！Input Error!")
GOTO:EOF

:buildALL
call :gen2019-x86
call :gen2019-x64
GOTO:EOF

:gen2019-x86
mkdir build-win-vs2019-x86
pushd build-win-vs2019-x86
call :cmakeParams "Visual Studio 16 2019" "Win32"
popd
GOTO:EOF

:gen2019-x64
mkdir build-win-vs2019-x64
pushd build-win-vs2019-x64
call :cmakeParams "Visual Studio 16 2019" "x64"
popd
GOTO:EOF

:cmakeParams
echo cmake -G "%~1" -A "%~2" -DOCR_OUTPUT=%BUILD_OUTPUT% -DOCR_BUILD_CRT=%MT_ENABLED% -DOCR_ONNX=%ONNX_TYPE% ..
cmake -G "%~1" -A "%~2" -DOCR_OUTPUT=%BUILD_OUTPUT% -DOCR_BUILD_CRT=%MT_ENABLED% -DOCR_ONNX=%ONNX_TYPE% ..
GOTO:EOF

@ENDLOCAL
