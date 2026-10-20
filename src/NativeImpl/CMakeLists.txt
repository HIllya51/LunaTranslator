cmake_minimum_required(VERSION 3.16)

project(LunaPlugins)

set(FETCHCONTENT_UPDATES_DISCONNECTED ON)
Set(FETCHCONTENT_QUIET FALSE)

option(BUILD_EXEC_ONLY "BUILD_EXEC_ONLY" OFF)
option(BUILD_S_EXE_ONLY "BUILD_S_EXE_ONLY" OFF)
option(WINXP "WINXP" OFF)
option(WIN10ABOVE "WIN10ABOVE" ON)
option(STATIC_FORCE "STATIC_FORCE" OFF)

if(WIN32)
    if(BUILD_S_EXE_ONLY OR STATIC_FORCE OR (NOT WIN10ABOVE))
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
endif()
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

set(CMAKE_CXX_STANDARD 17)
if(WIN32)
    add_definitions(-DUNICODE -D_UNICODE)
endif()
if(MSVC)
  if (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    add_compile_options(/MP)
  endif()
  add_compile_options(/utf-8)
endif()

if(WIN32)
    if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
        set(platform "x64")
    else()
        set(platform "x86")
    endif()
else()
    # Linux/其他平台：按处理器取名，只用于输出目录
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "(x86_|X86_|AMD64|amd64)i?64")
        set(platform "x64")
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(i.86|x86)$")
        set(platform "x86")
    else()
        string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" platform)
    endif()
endif()

set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_${platform}${__APP})

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)

if(WIN32)
    if(NOT WIN10ABOVE)
        option(USE_VC_LTL "USE_VC_LTL" ON)
    endif()
    include(winxphelper.cmake)

    include(${CMAKE_SOURCE_DIR}/version.cmake)
endif()

# 显式STATIC：pch只用于承载预编译头，防止md4c泄漏的BUILD_SHARED_LIBS
# 使其在重新configure时漂移成共享库（libpch.so混进部署目录）
add_library(pch STATIC pch.cpp)
target_precompile_headers(pch PUBLIC pch.h)
if(NOT WIN32)
    # SHARED/MODULE目标复用PCH时gcc要求PIC一致
    set_target_properties(pch PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()

include(FetchContent)

if(WIN32)
    FetchContent_Declare(magic_enum
        GIT_REPOSITORY https://github.com/Neargye/magic_enum
        GIT_TAG master
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(magic_enum)
endif()


if(BUILD_EXEC_ONLY)
    add_subdirectory(exec)
elseif(BUILD_S_EXE_ONLY)
    add_subdirectory(LunaSubprocess)
elseif(WIN32)
    add_subdirectory(exec)
    add_subdirectory(LunaSubprocess)
    add_subdirectory(NativeUtils)
    add_subdirectory(CVUtils)
else()
    # Linux：只有NativeUtils/CVUtils中的跨平台部分可编译
    add_subdirectory(NativeUtils)
    add_subdirectory(CVUtils)
endif()
