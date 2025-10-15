
function(PROTOBUF_GENERATE_CPP SRCS target_dir protoc proto_path)
    cmake_parse_arguments(protobuf_generate_cpp "" "EXPORT_MACRO;DESCRIPTORS" "" ${ARGN})
    message("target_dir ${target_dir}")
    message("protoc ${protoc}")
    set(${SRCS})
    set(HDRS)
    
    foreach(FIL ${protobuf_generate_cpp_UNPARSED_ARGUMENTS}) 
        get_filename_component(FIL_WE ${FIL} NAME_WE)
        
        list(APPEND ${SRCS} "${target_dir}/${FIL_WE}.pb.cc")
        list(APPEND ${HDRS} "${target_dir}/${FIL_WE}.pb.h")
        
        add_custom_command(
            OUTPUT "${target_dir}/${FIL_WE}.pb.cc"
                   "${target_dir}/${FIL_WE}.pb.h"
            COMMAND ${protoc}
            ARGS --cpp_out ${target_dir} --proto_path ${proto_path} ${FIL} 
            COMMENT "Running C++ protocol buffer compiler on ${FIL}"
            VERBATIM
        )
    endforeach()
    
    set_source_files_properties(${${SRCS}} ${HDRS} PROPERTIES GENERATED TRUE)
    set(${SRCS} ${${SRCS}} PARENT_SCOPE)
    set(${HDRS} ${HDRS} PARENT_SCOPE)
endfunction()


include(FetchContent)

FetchContent_Declare(protobuf
    URL https://github.com/protocolbuffers/protobuf/archive/refs/tags/v3.21.12.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)

set(protobuf_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_PROTOC_BINARIES OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(protobuf_INSTALL OFF CACHE BOOL "" FORCE)
set(protobuf_WITH_ZLIB OFF CACHE BOOL "" FORCE)
set(ABSL_PROPAGATE_CXX_STD ON)

if(NOT IS_STATIC)
  option(protobuf_MSVC_STATIC_RUNTIME "protobuf_MSVC_STATIC_RUNTIME" OFF)
endif()
FetchContent_MakeAvailable(protobuf)
