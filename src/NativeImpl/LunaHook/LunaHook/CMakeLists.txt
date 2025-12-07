include_directories(. util engines)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8) 
	aux_source_directory("engine64" enginessrc)
	set(collector "enginecollection64.cpp")
else()
	aux_source_directory("engine32" enginessrc)
	set(collector "enginecollection32.cpp")
endif()

set_source_files_properties(${enginessrc} PROPERTIES SOURCE_ENCODING "UTF-8")


add_library(pchhook pchhook.cpp)
target_precompile_headers(pchhook PUBLIC pchhook.h)


set(texthook_src
		main.cc
		texthook.cc
		hookfinder.cc
		${enginessrc}
		${collector}
		enginecontrol.cpp
		embed_util.cc
		hijackfuns.cc
		veh_hook.cpp
) 
add_subdirectory(util)
add_subdirectory(engines)
add_subdirectory(emulators)



add_library(LunaHook MODULE ${texthook_src} resource.rc ${versioninfo})
add_library(trhelper ../include/InfoStrings.cpp)
target_compile_definitions(trhelper PRIVATE -DBUILD_HOOK=1)

target_precompile_headers(trhelper REUSE_FROM pchhook) 
target_precompile_headers(LunaHook REUSE_FROM pchhook) 

set_target_properties(LunaHook PROPERTIES OUTPUT_NAME "LunaHook${bitappendix}")

target_link_libraries(LunaHook PRIVATE trhelper VERSION_DEF Version httpapi ws2_32 Shlwapi pch minhook commonengine emulators utils ${YY_Thunks})

target_link_options(LunaHook PRIVATE "/DELAYLOAD:httpapi.dll")
target_link_options(LunaHook PRIVATE "/DELAYLOAD:WS2_32.dll")
target_link_options(LunaHook PRIVATE "/DELAYLOAD:VERSION.dll")
target_link_libraries(LunaHook PRIVATE delayimp)