
include(FetchContent)

FetchContent_Declare(wechat_ocr
    GIT_REPOSITORY https://github.com/swigger/wechat-ocr
    GIT_TAG 81e6e75dda85e99754c90a8254f0fc16a52eb3b9
)
FetchContent_Populate(wechat_ocr)

set(wcocr_src ${wechat_ocr_SOURCE_DIR}/src/mojocall.cpp ${wechat_ocr_SOURCE_DIR}/src/ocr_common.pb.cc  ${wechat_ocr_SOURCE_DIR}/src/ocr_wx3.pb.cc ${wechat_ocr_SOURCE_DIR}/src/ocr_wx4.pb.cc ${wechat_ocr_SOURCE_DIR}/src/wechatocr.cpp)


add_library(wcocr_1 MODULE wcocr.cpp ${wcocr_src} ${versioninfo})
target_include_directories(wcocr_1 PUBLIC ${wechat_ocr_SOURCE_DIR}/vs.proj PUBLIC ${wechat_ocr_SOURCE_DIR}/src PRIVATE ${wechat_ocr_SOURCE_DIR}/spt)

target_compile_options(wcocr_1
  PUBLIC 
  /std:c++20
  /MD
)

target_link_libraries(wcocr_1 ${wechat_ocr_SOURCE_DIR}/spt/${platform}/libprotobuf-lite.lib)
set_target_properties(wcocr_1 PROPERTIES OUTPUT_NAME "wcocr")