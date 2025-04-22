set https_proxy=http://127.0.0.1:7897
cmake --build ..\build\x86 --config Release --target ALL_BUILD -j 14
copy ..\builds\_x86\shareddllproxy32.exe ..\..\files\plugins
robocopy ..\builds\_x86 ..\..\files\plugins\DLL32 *.dll