cmake_minimum_required(VERSION 3.16)

project(LunaPlugins)

set(FETCHCONTENT_UPDATES_DISCONNECTED ON)
Set(FETCHCONTENT_QUIET FALSE)

option(BUILD_EXEC_ONLY "BUILD_EXEC_ONLY" OFF)
option(WINXP "WINXP" OFF)
option(WIN10ABOVE "WIN10ABOVE" ON)
option(STATIC_FORCE "STATIC_FORCE" OFF)
if(STATIC_FORCE OR (NOT WIN10ABOVE))
    set(IS_STATIC ON)
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()
if(NOT WIN10ABOVE)
    if(WINXP)
        set(__APP "_winxp")
    else()
        set(__APP "_win7")
    endif()
else()
    add_definitions(-DWIN10ABOVE=${WIN10ABOVE})
    set(__APP "_win10")
endif()
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

set(CMAKE_CXX_STANDARD 17)
add_definitions(-DUNICODE -D_UNICODE)
if(MSVC)
add_compile_options(/MP)
endif()
add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    set(platform "x64")
else()
    set(platform "x86")
endif()

set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_${platform}${__APP})

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

if(NOT BUILD_EXEC_ONLY)
    add_subdirectory(NativeUtils)
    add_subdirectory(shareddllproxy)
    add_subdirectory(CVUtils)
endif()