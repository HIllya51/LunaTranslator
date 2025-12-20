set https_proxy=http://127.0.0.1:7897
cmake -DWIN10ABOVE=OFF -DWINXP=ON ../CMakeLists.txt -G "Visual Studio 18 2026" -A win32 -T v141_xp -B ../build/x86_winxp
