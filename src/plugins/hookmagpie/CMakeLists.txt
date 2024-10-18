

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	add_library(hookmagpie MODULE hookmagpie.cpp veh_hook.cpp)
	target_precompile_headers(hookmagpie REUSE_FROM pch)
endif()

	