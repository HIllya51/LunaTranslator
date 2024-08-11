cmake_minimum_required(VERSION 3.16)

project(LunaPlugins)

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

include(libs/libs.cmake)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR}/version)
include(generate_product_version)

set(VERSION_MAJOR 5)
set(VERSION_MINOR 26)
set(VERSION_PATCH 0)

add_library(pch pch.cpp)
target_precompile_headers(pch PUBLIC pch.h)


add_subdirectory(exec)
add_subdirectory(winrtutils)
add_subdirectory(winsharedutils)
add_subdirectory(hookmagpie)
add_subdirectory(shareddllproxy)
add_subdirectory(applicationloopbackaudio)
add_subdirectory(wcocr)