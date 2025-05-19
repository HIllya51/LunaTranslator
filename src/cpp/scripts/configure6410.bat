set https_proxy=http://127.0.0.1:7897
cmake -DWIN10ABOVE=ON ..\CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ..\build\x64_10