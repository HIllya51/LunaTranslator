

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	add_library(hookmagpie MODULE hookmagpie.cpp)
	add_subdirectory(minhook)
	target_link_libraries(hookmagpie minhook ${Detours})
endif()

	