cmake_minimum_required(VERSION 3.16)

project(shareddllproxy)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

add_compile_options(
  /std:c++17
  /MP
  /wd4018 
  /DUNICODE 
  /D_UNICODE
)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_x64)
else()
	set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_x86)
endif()
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
 
include_directories(Detours-4.0.1/include)

add_executable(shareddllproxy shareddllproxy.cpp dllinject.cpp ntleas.cpp)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	add_library(x64lib magpie.cpp lossless.cpp)
	target_link_libraries(shareddllproxy x64lib   ${CMAKE_SOURCE_DIR}/Detours-4.0.1/lib.X64/detours.lib)
	set_target_properties(shareddllproxy PROPERTIES OUTPUT_NAME "shareddllproxy64")
else()
	add_subdirectory(voiceroid2)
	add_library(x86lib dreye.cpp jbj7.cpp kingsoft.cpp le.cpp neospeech.cpp  LR.cpp)
	target_link_libraries(shareddllproxy x86lib voiceroid2   ${CMAKE_SOURCE_DIR}/Detours-4.0.1/lib.X86/detours.lib)
	set_target_properties(shareddllproxy PROPERTIES OUTPUT_NAME "shareddllproxy32")
endif()

	