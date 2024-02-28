

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	add_library(hookmagpie MODULE hookmagpie.cpp)
	target_link_libraries(hookmagpie minhook ${Detours})
endif()

	