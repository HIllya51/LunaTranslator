
include(FetchContent)

FetchContent_Declare(wechat_ocr
    GIT_REPOSITORY https://github.com/swigger/wechat-ocr
    GIT_TAG master
    GIT_SHALLOW TRUE
)
FetchContent_Declare(protobuf
    URL https://github.com/protocolbuffers/protobuf/archive/refs/tags/v3.21.12.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Populate(wechat_ocr)

set(protobuf_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_PROTOC_BINARIES OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(protobuf_INSTALL OFF CACHE BOOL "" FORCE)
set(protobuf_WITH_ZLIB OFF CACHE BOOL "" FORCE)
set(ABSL_PROPAGATE_CXX_STD ON)

if(WIN10ABOVE)
  option(protobuf_MSVC_STATIC_RUNTIME "protobuf_MSVC_STATIC_RUNTIME" OFF)
endif()
FetchContent_MakeAvailable(protobuf)


function(FIX_CPP17 FILE_PATH)

    file(READ ${FILE_PATH} FILE_CONTENT)

    string(REPLACE "std::span" "std::basic_string_view" FILE_CONTENT "${FILE_CONTENT}")
    string(REPLACE "requires" "//requires" FILE_CONTENT "${FILE_CONTENT}")
    string(REPLACE "#include <span>" "//#include <span>" FILE_CONTENT "${FILE_CONTENT}")

    file(WRITE ${FILE_PATH} "${FILE_CONTENT}")
endfunction()

FIX_CPP17("${wechat_ocr_SOURCE_DIR}/src/mojocall.cpp")
FIX_CPP17("${wechat_ocr_SOURCE_DIR}/src/mojocall.h")
FIX_CPP17("${wechat_ocr_SOURCE_DIR}/src/wechatocr.cpp")
FIX_CPP17("${wechat_ocr_SOURCE_DIR}/src/wechatocr.h")
FIX_CPP17("${wechat_ocr_SOURCE_DIR}/vs.proj/stdafx.h")

set(wcocr_src ${wechat_ocr_SOURCE_DIR}/src/mojocall.cpp ${wechat_ocr_SOURCE_DIR}/src/ocr_common.pb.cc  ${wechat_ocr_SOURCE_DIR}/src/ocr_wx3.pb.cc ${wechat_ocr_SOURCE_DIR}/src/ocr_wx4.pb.cc ${wechat_ocr_SOURCE_DIR}/src/wechatocr.cpp)


add_library(wcocrpch ${wechat_ocr_SOURCE_DIR}/vs.proj/stdafx.cpp)
target_precompile_headers(wcocrpch PUBLIC ${wechat_ocr_SOURCE_DIR}/vs.proj/stdafx.h)
add_library(wcocr_1 wcocr_1.cpp ${wcocr_src})
target_include_directories(wcocr_1 PRIVATE ${wechat_ocr_SOURCE_DIR}/vs.proj PRIVATE ${wechat_ocr_SOURCE_DIR}/src PRIVATE ${wechat_ocr_SOURCE_DIR}/spt)
target_precompile_headers(wcocr_1 REUSE_FROM wcocrpch)


target_link_libraries(wcocr_1 PRIVATE libprotobuf-lite)

file(GLOB glensproto proto/*.proto)


function(PROTOBUF_GENERATE_CPP SRCS HDRS)
    cmake_parse_arguments(protobuf_generate_cpp "" "EXPORT_MACRO;DESCRIPTORS" "" ${ARGN})
    
    set(${SRCS})
    set(${HDRS})
    
    foreach(FIL ${protobuf_generate_cpp_UNPARSED_ARGUMENTS}) 
        get_filename_component(FIL_WE ${FIL} NAME_WE)
        
        list(APPEND ${SRCS} "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.pb.cc")
        list(APPEND ${HDRS} "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.pb.h")
        
        add_custom_command(
            OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.pb.cc"
                   "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.pb.h"
            COMMAND ${wechat_ocr_SOURCE_DIR}/spt/protoc.exe
            ARGS --cpp_out ${CMAKE_CURRENT_BINARY_DIR} --proto_path ${CMAKE_CURRENT_LIST_DIR}/proto ${FIL} 
            COMMENT "Running C++ protocol buffer compiler on ${FIL}"
            VERBATIM
        )
    endforeach()
    
    set_source_files_properties(${${SRCS}} ${${HDRS}} PROPERTIES GENERATED TRUE)
    set(${SRCS} ${${SRCS}} PARENT_SCOPE)
    set(${HDRS} ${${HDRS}} PARENT_SCOPE)
endfunction()

PROTOBUF_GENERATE_CPP(glensprotocpp glensprotoh "${glensproto}")

add_library(glensproto glens_1.cpp "${glensprotocpp}")
target_include_directories(glensproto PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_include_directories(glensproto PRIVATE ${wechat_ocr_SOURCE_DIR}/spt)
target_link_libraries(glensproto PRIVATE libprotobuf-lite)


add_library(needprotobuf INTERFACE)
target_sources(needprotobuf INTERFACE wcocr.cpp)
target_sources(needprotobuf INTERFACE glens.cpp)
target_link_libraries(needprotobuf INTERFACE wcocr_1)
target_link_libraries(needprotobuf INTERFACE glensproto)