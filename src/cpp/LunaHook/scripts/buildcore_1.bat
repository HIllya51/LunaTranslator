set https_proxy=http://127.0.0.1:7897
cmake ..\CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ..\build\x86
cmake ..\CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ..\build\x64