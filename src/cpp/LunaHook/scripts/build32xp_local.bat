cmake -DBUILD_GUI=ON -DBUILD_CLI=ON -DWINXP=1 ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86_xp
call dobuildxp.bat