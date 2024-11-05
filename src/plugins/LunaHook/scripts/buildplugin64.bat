cmake -DBUILD_CORE=OFF -DPLUGIN=1 ../CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ../build/plugin64
cmake --build ../build/plugin64 --config Release --target ALL_BUILD -j 14