set https_proxy=http://127.0.0.1:7897
cmake --build ..\build\x86 --config Release --target ALL_BUILD -j 14
cmake --build ..\build\x64 --config Release --target ALL_BUILD -j 14
robocopy ..\builds\Release ..\..\..\files\LunaHook