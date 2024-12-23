
project(shareddllproxy)
 

generate_product_version(
   versioninfo
   NAME "LunaTranslator shareddllproxy"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)

set(shareddllproxy_common shareddllproxy.cpp dllinject.cpp aspatch.cpp update.cpp ${versioninfo})

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	add_executable(shareddllproxy ${shareddllproxy_common})

else()
	add_executable(shareddllproxy ${shareddllproxy_common} lec.cpp Atlas.cpp eztrans.cpp dreye.cpp jbj7.cpp kingsoft.cpp neospeech.cpp ../implsapi.cpp)
	add_subdirectory(voiceroid2)
endif()

target_precompile_headers(shareddllproxy REUSE_FROM pch) 

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	target_link_libraries(shareddllproxy nlohmann Mfplat mfuuid)
	set_target_properties(shareddllproxy PROPERTIES OUTPUT_NAME "shareddllproxy64")
else()
	target_precompile_headers(voiceroid2 REUSE_FROM pch) 
	target_link_libraries(shareddllproxy nlohmann Mfplat mfuuid voiceroid2)
	set_target_properties(shareddllproxy PROPERTIES OUTPUT_NAME "shareddllproxy32")
endif()