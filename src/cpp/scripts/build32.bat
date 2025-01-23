python fetchwebview2.py
cmake ..\CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ..\build\x86
cmake --build ..\build\x86 --config Release --target ALL_BUILD -j 14
copy ..\builds\_x86\shareddllproxy32.exe ..\..\files\plugins
robocopy ..\builds\_x86 ..\..\files\plugins\DLL32 *.pyd *.dll