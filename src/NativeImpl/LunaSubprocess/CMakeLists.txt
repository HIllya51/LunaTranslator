
project(LunaSubprocess)

include(FetchContent)
FetchContent_Declare(cpp_base64
	GIT_REPOSITORY https://github.com/ReneNyffenegger/cpp-base64
	GIT_TAG master
	GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(cpp_base64)
add_library(base64 INTERFACE)
target_include_directories(base64 INTERFACE ${cpp_base64_SOURCE_DIR})
target_sources(base64 INTERFACE ${cpp_base64_SOURCE_DIR}/base64.cpp)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	# 使用<=1.41.1版本，否则和系统的可能不兼容。
	include(FetchContent)
	FetchContent_Declare(CognitiveServices
		URL https://www.nuget.org/api/v2/package/Microsoft.CognitiveServices.Speech/1.41.1
		DOWNLOAD_EXTRACT_TIMESTAMP true
	)
	FetchContent_MakeAvailable(CognitiveServices)

	add_library(CognitiveServices INTERFACE)
	target_include_directories(CognitiveServices INTERFACE ${cognitiveservices_SOURCE_DIR}/build/native/include/c_api)
	target_include_directories(CognitiveServices INTERFACE ${cognitiveservices_SOURCE_DIR}/build/native/include/cxx_api)

	target_link_libraries(CognitiveServices INTERFACE ${cognitiveservices_SOURCE_DIR}/build/native/x64/Release/Microsoft.CognitiveServices.Speech.core.lib)
	target_link_options(CognitiveServices INTERFACE "/DELAYLOAD:Microsoft.CognitiveServices.Speech.core.dll")
endif()


set(LunaSubprocess_common
	LunaSubprocess.cpp dllinject.cpp update.cpp ${versioninfo}
	../NativeUtils/loopbackaudio/LoopbackCapture.cpp ../NativeUtils/loopbackaudio/LoopbackTranditional.cpp)


if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	add_executable(LunaSubprocess ${LunaSubprocess_common}
	SnippingTool.cpp
    msnaturalvoice.cpp
    mssr.cpp)
else()
	add_executable(LunaSubprocess ${LunaSubprocess_common} lec.cpp Atlas.cpp eztrans.cpp dreye.cpp jbj7.cpp kingsoft.cpp neospeech.cpp)
endif()
add_subdirectory(voiceroid_aivoice)
add_subdirectory(vad)
add_subdirectory(FileLocksmithLibInterop)

target_precompile_headers(LunaSubprocess REUSE_FROM pch)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	target_link_libraries(LunaSubprocess PRIVATE mfuuid CognitiveServices voiceroid_aivoice vad version ${YY_Thunks})
	set_target_properties(LunaSubprocess PROPERTIES OUTPUT_NAME "LunaSubprocess64")
	if(NOT WINXP)
        target_link_libraries(LunaSubprocess PRIVATE Mmdevapi)
        target_link_options(LunaSubprocess PRIVATE "/DELAYLOAD:MMDevAPI.dll")
        target_link_options(LunaSubprocess PRIVATE "/DELAYLOAD:MFPlat.dll")
        target_link_options(LunaSubprocess PRIVATE "/DELAYLOAD:dxgi.dll")
        target_link_options(LunaSubprocess PRIVATE "/DELAYLOAD:d3d11.dll")
    endif()
else()
	# 32 位无 CognitiveServices（其传递依赖里带了 Mfplat.lib），故需显式链接 MF 运行时
	target_link_libraries(LunaSubprocess PRIVATE ${YY_Thunks} voiceroid_aivoice vad mfuuid Mfplat)
	set_target_properties(LunaSubprocess PROPERTIES OUTPUT_NAME "LunaSubprocess32")
	if(NOT WINXP)
		target_link_libraries(LunaSubprocess PRIVATE Mmdevapi)
		target_link_options(LunaSubprocess PRIVATE "/DELAYLOAD:MMDevAPI.dll")
		target_link_options(LunaSubprocess PRIVATE "/DELAYLOAD:MFPlat.dll")
	endif()
endif()

if(WIN10ABOVE)
	target_link_libraries(LunaSubprocess PRIVATE windowsapp)
endif()

target_link_libraries(LunaSubprocess PRIVATE FileLocksmith base64)
target_link_libraries(LunaSubprocess PRIVATE delayimp Dbghelp)
