set https_proxy=http://127.0.0.1:7897
cmake --build ..\build\x86_win7 --config Release --target ALL_BUILD -j %NUMBER_OF_PROCESSORS%
copy ..\builds\_x86_win7\shareddllproxy32.exe ..\..\files
robocopy ..\builds\_x86_win7 ..\..\files\DLL32 *.dll