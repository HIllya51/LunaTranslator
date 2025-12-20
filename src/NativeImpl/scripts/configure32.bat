set https_proxy=http://127.0.0.1:7897
cmake -DWIN10ABOVE=OFF ..\CMakeLists.txt -G "Visual Studio 18 2026" -A win32 -T host=x86 -B ..\build\x86_win7