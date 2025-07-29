set https_proxy=http://127.0.0.1:7897
cmake --build ..\build\ --config Release --target ALL_BUILD -j 14
copy ..\builds\_x64_win10\shareddllproxy64.exe ..\..\files
robocopy ..\builds\_x64_win10 ..\..\files\DLL64 *.dll