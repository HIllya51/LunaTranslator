cmake -DBUILD_PLUGIN=OFF -DWINXP=1 ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86_xp
cmake -DBUILD_PLUGIN=OFF -DWINXP=1 -DLANGUAGE=Chinese ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86_zh_xp
call dobuildxp.bat