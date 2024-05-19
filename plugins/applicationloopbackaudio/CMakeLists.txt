
project(loopbackaudio)
 

generate_product_version(
   versioninfo
   NAME "LunaTranslator loopbackaudio"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)


if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	
else()
	
	add_executable(loopbackaudio runer.cpp  LoopbackCapture.cpp  ${versioninfo})
	target_precompile_headers(loopbackaudio REUSE_FROM pch) 
	target_link_libraries(loopbackaudio Mfplat mfuuid )
endif()
