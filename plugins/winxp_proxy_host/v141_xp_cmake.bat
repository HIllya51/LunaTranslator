cmake ./CMakeLists.txt -G "Visual Studio 15 2017" -A win32 -T v141_xp -B ./build
cmake --build ./build --config Release --target ALL_BUILD -j 14
