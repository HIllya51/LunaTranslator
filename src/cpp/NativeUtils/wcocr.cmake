
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

if(WIN10ABOVE)
  target_link_libraries(wcocr_1 PRIVATE ${wechat_ocr_SOURCE_DIR}/spt/${platform}/libprotobuf-lite.lib)
else()
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
  FetchContent_MakeAvailable(protobuf)
  target_link_libraries(wcocr_1 PRIVATE libprotobuf-lite)
endif()

