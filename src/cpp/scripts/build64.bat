python fetchwebview2.py
cmake ..\CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ..\build\x64
cmake --build ..\build\x64 --config Release --target ALL_BUILD -j 14

copy ..\builds\_x64\shareddllproxy64.exe ..\..\py\files\plugins
robocopy ..\builds\_x64 ..\..\py\files\plugins\DLL64 *.pyd *.dll