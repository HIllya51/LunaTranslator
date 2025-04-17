cmake_minimum_required(VERSION 3.16)

project(LunaHook)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

set(CMAKE_CXX_STANDARD 17)
add_definitions(-DUNICODE -D_UNICODE)
add_compile_options(
  /MP
  /wd4018 
  /wd4819 
  /wd4244
  /wd4267
  /wd4340
  /wd4369
  /wd4573
)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set(bitappendix "64")
else()
	set(bitappendix "32")
endif()

option(BUILD_GUI "BUILD_GUI" OFF)
option(BUILD_CLI "BUILD_CLI" OFF)
option(WINXP "WINXP" OFF)

if(WINXP)
  set(WINXPAPP "_winxp")
  add_definitions(-DWINXP=${WINXP})
  set(YY_Thunks ${CMAKE_CURRENT_LIST_DIR}/YY-Thunks/objs/X86/YY_Thunks_for_WinXP.obj)
else()
  set(WINXPAPP "")
  if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
      set(YY_Thunks ${CMAKE_CURRENT_LIST_DIR}/YY-Thunks/objs/X64/YY_Thunks_for_Win7.obj)
  else()
      set(YY_Thunks ${CMAKE_CURRENT_LIST_DIR}/YY-Thunks/objs/X86/YY_Thunks_for_Win7.obj)
  endif()
endif()

if(NOT EXISTS ${YY_Thunks})
    set(YY_Thunks )
endif()

set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_x${bitappendix}${WINXPAPP}) 
set(binary_out_putpath ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}${WINXPAPP}) 
#set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${binary_out_putpath}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${binary_out_putpath}>)

include_directories(.)
option(USE_VCLTL "USE_VCLTL" OFF)

add_subdirectory(${CMAKE_SOURCE_DIR}/../libs/minhook ${CMAKE_BINARY_DIR}/minhook)

include_directories(include)

include(${CMAKE_SOURCE_DIR}/../version.cmake)

add_subdirectory(include)
add_subdirectory(Lang)
add_subdirectory(LunaHook)
add_subdirectory(LunaHost)
