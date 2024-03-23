
project(shareddllproxy)
 

add_executable(shareddllproxy shareddllproxy.cpp dllinject.cpp ntleas.cpp aspatch.cpp)
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

	