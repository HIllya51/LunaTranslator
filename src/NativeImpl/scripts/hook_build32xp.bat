set https_proxy=http://127.0.0.1:7897
cmake -DBUILD_GUI=ON -DWINXP=1 ..\LunaHook\CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T v141_xp -B ..\LunaHook\build\x86_xp
cmake --build ..\LunaHook\build\x86_xp --config Release --target ALL_BUILD -j %NUMBER_OF_PROCESSORS%
