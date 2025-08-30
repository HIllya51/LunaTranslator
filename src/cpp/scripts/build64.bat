set https_proxy=http://127.0.0.1:7897
cmake --build ..\build\x64_win7 --config Release --target ALL_BUILD -j %NUMBER_OF_PROCESSORS%
copy ..\builds\_x64_win7\shareddllproxy64.exe ..\..\files
robocopy ..\builds\_x64_win7 ..\..\files\DLL64 *.dll