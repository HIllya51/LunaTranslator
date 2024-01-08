cmake_minimum_required(VERSION 3.16)

project(LUNA)

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
   
add_executable(LunaTranslator luna.cpp luna.rc) 
#target_link_options(LunaTranslator PRIVATE /MANIFESTUAC:level="asInvoker")

add_executable(LunaTranslator_admin luna.cpp luna.rc)
set_target_properties(LunaTranslator_admin PROPERTIES LINK_FLAGS " /MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\" ")

#target_link_options(LunaTranslator_admin PRIVATE /MANIFESTUAC:level="requireAdministrator")
#这个仅在visualstdio下管用，vscode cmake不管用了。
 