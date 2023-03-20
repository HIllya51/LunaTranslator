cmake_minimum_required(VERSION 3.16)

project(Textractor)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

if (NOT MSVC)
	message(FATAL_ERROR "Textractor can only be built with Visual Studio")
endif()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

add_compile_options(
  /std:c++17
  /MP
  /wd4018 # signed/unsigned mismatch
  /DVERSION="${VERSION}"
  /DUNICODE # config.pri
  /D_UNICODE
)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_x64)
	link_directories(x64libs)
else()
	set(CMAKE_FINAL_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/builds/${CMAKE_BUILD_TYPE}_x86)
	link_directories(x86libs)
endif()
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_FINAL_OUTPUT_DIRECTORY}>)

include_directories(include)
add_library(pch text.cpp)
target_precompile_headers(pch PUBLIC include/common.h)

file(GLOB ASSETS assets/*)
file(COPY ${ASSETS} DESTINATION ${CMAKE_FINAL_OUTPUT_DIRECTORY})

add_library(text text.cpp)
target_compile_definitions(text PRIVATE ${TEXT_LANGUAGE})
link_libraries(text)

add_subdirectory(host)
#add_subdirectory(texthook)
#add_subdirectory(GUI)
#add_subdirectory(extensions)
#add_subdirectory(test)
