set https_proxy=http://127.0.0.1:7897
cmake --build ..\LunaHook\build\x86_win10_1 --config Release --target ALL_BUILD -j 14
cmake --build ..\LunaHook\build\x64_win10_1 --config Release --target ALL_BUILD -j 14
cmake --build ..\LunaHook\build\x86_win10_2 --config Release --target ALL_BUILD -j 14
cmake --build ..\LunaHook\build\x64_win10_2 --config Release --target ALL_BUILD -j 14
robocopy ..\LunaHook\builds\Release_win10 ..\..\files\LunaHook