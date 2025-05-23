cmake_minimum_required(VERSION 3.16)

project(LunaPlugins)

option(WINXP "WINXP" OFF)
option(WIN10ABOVE "WIN10ABOVE" OFF)
if(NOT WIN10ABOVE)
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
else()
    set(WIN10ABOVEAPP "_win10")
endif()
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

if(WINXP)
    set(WINXPAPP "_xp")
endif()
set(CMAKE_CXX_STANDARD 17)
add_definitions(-DUNICODE -D_UNICODE)
if(MSVC)
add_compile_options(/MP)
endif()

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    set(platform "x64")
else()
    set(platform "x86")
endif()

set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_${platform}${WIN10ABOVEAPP}${WINXPAPP})

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)

if(NOT WIN10ABOVE)
    option(USE_VC_LTL "USE_VC_LTL" ON)
endif()
include(winxphelper.cmake)

include(${CMAKE_SOURCE_DIR}/version.cmake)

add_library(pch pch.cpp)
target_precompile_headers(pch PUBLIC pch.h)

add_subdirectory(exec)
add_subdirectory(NativeUtils)
add_subdirectory(shareddllproxy)
add_subdirectory(CVUtils)
if(NOT WINXP)
if(MSVC)
add_subdirectory(wcocr)
endif()
endif()