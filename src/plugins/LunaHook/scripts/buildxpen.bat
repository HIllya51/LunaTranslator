cmake -DBUILD_PLUGIN=OFF -DWINXP=1 ../CMakeLists.txt -G "Visual Studio 16 2019" -A win32 -T v141_xp -B ../build/x86_xp
cmake --build ../build/x86_xp --config Release --target ALL_BUILD -j 14
call dobuildxp.bat