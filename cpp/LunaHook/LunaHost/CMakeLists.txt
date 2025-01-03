

add_library(host
	host.cpp
	textthread.cpp
)
target_precompile_headers(host REUSE_FROM pch)
target_include_directories(host PUBLIC .)
target_link_libraries(host VERSION_DEF)

add_library(LunaHostDll MODULE LunaHostDll.cpp ${versioninfo})
target_precompile_headers(LunaHostDll REUSE_FROM pch)
set_target_properties(LunaHostDll PROPERTIES OUTPUT_NAME "LunaHost${bitappendix}")
target_link_libraries(LunaHostDll pch host ${YY_Thunks_for_WinXP} lang_host)

if(BUILD_CLI)
add_executable(LunaHostCLI LunaHostCLI.cpp injector.cpp ${versioninfo})
target_precompile_headers(LunaHostCLI REUSE_FROM pch)
set_target_properties(LunaHostCLI PROPERTIES OUTPUT_NAME "LunaHostCLI${bitappendix}")
target_link_libraries(LunaHostCLI pch host ${YY_Thunks_for_WinXP} lang_host)
endif()

add_subdirectory(GUI)