
include(libuchardet.cmake)


add_library(host host.cpp textthread.cpp ../include/InfoStrings.cpp)
target_compile_definitions(host PRIVATE -DBUILD_HOST=1)
target_precompile_headers(host REUSE_FROM pch)
target_include_directories(host PUBLIC .)
target_link_libraries(host PRIVATE VERSION_DEF libuchardet)

add_library(LunaHostDll MODULE LunaHostDll.cpp ${versioninfo})
target_precompile_headers(LunaHostDll REUSE_FROM pch)
set_target_properties(LunaHostDll PROPERTIES OUTPUT_NAME "LunaHost${bitappendix}")
target_link_libraries(LunaHostDll pch host ${YY_Thunks})

add_subdirectory(GUI)