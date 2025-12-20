set https_proxy=http://127.0.0.1:7897
cmake -DBUILD_HOST=OFF ..\LunaHook\CMakeLists.txt -G "Visual Studio 18 2026" -A win32 -T host=x86 -B ..\LunaHook\build\x86_win7_1
cmake -DUSE_VC_LTL=ON -DBUILD_HOOK=OFF ..\LunaHook\CMakeLists.txt -G "Visual Studio 18 2026" -A win32 -T host=x86 -B ..\LunaHook\build\x86_win7_2
cmake -DBUILD_HOST=OFF ..\LunaHook\CMakeLists.txt -G "Visual Studio 18 2026" -A x64 -T host=x64 -B ..\LunaHook\build\x64_win7_1
cmake -DUSE_VC_LTL=ON -DBUILD_HOOK=OFF ..\LunaHook\CMakeLists.txt -G "Visual Studio 18 2026" -A x64 -T host=x64 -B ..\LunaHook\build\x64_win7_2