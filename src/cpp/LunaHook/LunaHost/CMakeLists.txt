

add_library(host host.cpp textthread.cpp injector.cpp)
target_precompile_headers(host REUSE_FROM pch)
target_include_directories(host PUBLIC .)
target_link_libraries(host VERSION_DEF)

add_library(LunaHostDll MODULE LunaHostDll.cpp ${versioninfo})
target_precompile_headers(LunaHostDll REUSE_FROM pch)
set_target_properties(LunaHostDll PROPERTIES OUTPUT_NAME "LunaHost${bitappendix}")
target_link_libraries(LunaHostDll pch host ${YY_Thunks} lang_host)

add_subdirectory(GUI)