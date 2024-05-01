
project(shareddllproxy)
 

generate_product_version(
   versioninfo
   NAME "LunaTranslator shareddllproxy"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)


add_executable(shareddllproxy shareddllproxy.cpp dllinject.cpp ntleas.cpp aspatch.cpp ${versioninfo})
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	add_library(x64lib magpie.cpp lossless.cpp)
	target_link_libraries(shareddllproxy x64lib   ${Detours})
	set_target_properties(shareddllproxy PROPERTIES OUTPUT_NAME "shareddllproxy64")
else()
	add_subdirectory(voiceroid2)
	add_library(x86lib dreye.cpp jbj7.cpp kingsoft.cpp le.cpp neospeech.cpp  LR.cpp)
	target_link_libraries(shareddllproxy x86lib voiceroid2   ${Detours})
	set_target_properties(shareddllproxy PROPERTIES OUTPUT_NAME "shareddllproxy32")
endif()

	