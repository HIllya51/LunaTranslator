set https_proxy=http://127.0.0.1:7897
cmake --build ..\build\x86_win7_1 --config Release --target ALL_BUILD -j 14
cmake --build ..\build\x64_win7_1 --config Release --target ALL_BUILD -j 14
cmake --build ..\build\x86_win7_2 --config Release --target ALL_BUILD -j 14
cmake --build ..\build\x64_win7_2 --config Release --target ALL_BUILD -j 14
robocopy ..\builds\Release_win7 ..\..\..\files\LunaHook