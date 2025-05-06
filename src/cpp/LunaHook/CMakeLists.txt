cmake_minimum_required(VERSION 3.16)

project(LunaHook)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

set(CMAKE_CXX_STANDARD 17)
add_definitions(-DUNICODE -D_UNICODE)
add_compile_options(/MP)

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
option(WINXP "WINXP" OFF)

if(WINXP)
  set(WINXPAPP "_winxp")
else()
  set(WINXPAPP "")
endif()

include(../winxphelper.cmake)

set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_x${bitappendix}${WINXPAPP}) 
set(binary_out_putpath ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}${WINXPAPP}) 
#set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${binary_out_putpath}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${binary_out_putpath}>)

include_directories(.)

FetchContent_Declare(minhook 
  GIT_REPOSITORY https://github.com/TsudaKageyu/minhook
  GIT_TAG 2b003bb063d66f016cc1aef7d63951350ce60f35
)
FetchContent_MakeAvailable(minhook)

include_directories(include)

include(${CMAKE_SOURCE_DIR}/../version.cmake)

add_subdirectory(include)
add_subdirectory(Lang)
add_subdirectory(LunaHook)
add_subdirectory(LunaHost)
