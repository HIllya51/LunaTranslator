cmake ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86
cmake --build ../build/x86 --config Release --target ALL_BUILD -j 14

cmake ../CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ../build/x64
cmake --build ../build/x64 --config Release --target ALL_BUILD -j 14
python copytarget.py