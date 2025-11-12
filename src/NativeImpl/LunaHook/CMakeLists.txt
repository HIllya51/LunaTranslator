cmake_minimum_required(VERSION 3.16)

project(LunaHook)

set(FETCHCONTENT_UPDATES_DISCONNECTED ON)
Set(FETCHCONTENT_QUIET FALSE)

option(BUILD_HOST "BUILD_HOST" ON)
option(BUILD_HOOK "BUILD_HOOK" ON)
option(WIN10ABOVE "WIN10ABOVE" ON)
option(WINXP "WINXP" OFF)

if(NOT (WIN10ABOVE AND (NOT BUILD_HOOK)))
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

set(CMAKE_CXX_STANDARD 17)
add_definitions(-DUNICODE -D_UNICODE)
if(MSVC)
add_compile_options(/MP)
endif()
include(FetchContent)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set(bitappendix "64")
else()
	set(bitappendix "32")
endif()

option(BUILD_GUI "BUILD_GUI" OFF)
if(NOT WIN10ABOVE)
    if(WINXP)
        set(__APP "_winxp")
    else()
        set(__APP "_win7")
    endif()
else()
    set(__APP "_win10")
endif()

include(../winxphelper.cmake)

set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_x${bitappendix}${__APP}) 
set(binary_out_putpath ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}${__APP}) 
#set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${binary_out_putpath}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${binary_out_putpath}>)

include_directories(.)

FetchContent_Declare(minhook 
  GIT_REPOSITORY https://github.com/TsudaKageyu/minhook
    GIT_TAG master
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(minhook)

include_directories(include)

include(${CMAKE_SOURCE_DIR}/../version.cmake)

add_subdirectory(include)
if(BUILD_HOST)
  add_subdirectory(LunaHost)
endif()
if(BUILD_HOOK)
  add_subdirectory(LunaHook)
endif()