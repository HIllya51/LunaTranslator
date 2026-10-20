
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
    set(${HDRS} ${${HDRS}} PARENT_SCOPE)
endfunction()


if(WIN32)
    include(protobuf.cmake)
    include(FetchContent)

    FetchContent_Declare(wechat_ocr
        GIT_REPOSITORY https://github.com/swigger/wechat-ocr
        GIT_TAG master
        GIT_SHALLOW TRUE
    )
    FetchContent_Populate(wechat_ocr)


    function(FIX_CPP17 FILE_PATH)

        file(READ ${FILE_PATH} FILE_CONTENT)

        string(REPLACE "std::span" "std::basic_string_view" FILE_CONTENT "${FILE_CONTENT}")
        string(REPLACE "requires" "//requires" FILE_CONTENT "${FILE_CONTENT}")
        string(REPLACE "#include <span>" "//#include <span>" FILE_CONTENT "${FILE_CONTENT}")
        string(REPLACE "__declspec(dllexport)" "" FILE_CONTENT "${FILE_CONTENT}")

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
    target_include_directories(wcocr_1 PRIVATE ${wechat_ocr_SOURCE_DIR}/vs.proj PRIVATE ${wechat_ocr_SOURCE_DIR}/src)
    target_precompile_headers(wcocr_1 REUSE_FROM wcocrpch)


    target_link_libraries(wcocr_1 PRIVATE libprotobuf-lite)

    set(glens_protoc ${wechat_ocr_SOURCE_DIR}/spt/protoc.exe)
    set(glens_protobuf_lib libprotobuf-lite)
    set(glens_win_src wcocr.cpp)
    set(glens_win_lib wcocr_1)
else()
    # wcocr(微信OCR)是Windows only；glens是纯protobuf，跨平台。
    # 不能find_package(Protobuf)：其模块定义的protobuf_generate_cpp会与本文件
    # 上面的自定义同名函数冲突（命令名大小写不敏感），故只find_program拿protoc，
    # 库直接按名链接apt的libprotobuf-lite（3.21.12，与Windows的FetchContent同版本）
    find_program(glens_protoc protoc REQUIRED)
    set(glens_protobuf_lib protobuf-lite)
endif()

file(GLOB glensproto proto/*.proto)
PROTOBUF_GENERATE_CPP(glensprotocpp ${CMAKE_CURRENT_BINARY_DIR} ${glens_protoc} ${CMAKE_CURRENT_LIST_DIR}/proto "${glensproto}")

add_library(glensproto glens_1.cpp "${glensprotocpp}")
target_include_directories(glensproto PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(glensproto PRIVATE ${glens_protobuf_lib})
if(NOT WIN32)
    # 静态库链入.so需要PIC
    set_target_properties(glensproto PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()


add_library(needprotobuf INTERFACE)
target_sources(needprotobuf INTERFACE glens.cpp ${glens_win_src})
target_link_libraries(needprotobuf INTERFACE glensproto ${glens_win_lib})
