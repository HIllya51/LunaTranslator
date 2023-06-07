cmake_minimum_required(VERSION 3.16)

project(winxp_proxy_host)

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
  
include_directories(include)
add_executable(winxp_proxy_host WIN32 processlistwindow.cpp ipport.cpp hosttext.cpp host.cpp hookcode.cpp textthread.cpp text.cpp)
target_link_libraries(winxp_proxy_host ws2_32.lib ${CMAKE_SOURCE_DIR}/YY-Thunks-1.0.7-Binary/objs/x86/YY_Thunks_for_WinXP.obj)