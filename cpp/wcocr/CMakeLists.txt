
project(wcocr)

set(wcocr_src wechat-ocr/src/mojocall.cpp wechat-ocr/src/ocr_common.pb.cc  wechat-ocr/src/ocr_wx3.pb.cc wechat-ocr/src/ocr_wx4.pb.cc wechat-ocr/src/wechatocr.cpp)


add_library(wcocr MODULE wcocr.cpp ${wcocr_src})
target_include_directories(wcocr PUBLIC wechat-ocr/vs.proj PUBLIC wechat-ocr/src PRIVATE wechat-ocr/spt)

target_compile_options(wcocr
  PUBLIC 
  /std:c++20
  /MD
  /wd4018
  /DUNICODE
  /D_UNICODE
)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
   target_link_libraries(wcocr ${CMAKE_CURRENT_SOURCE_DIR}/wechat-ocr/spt/x64/libprotobuf-lite.lib ${CMAKE_CURRENT_SOURCE_DIR}/wechat-ocr/spt/x64/mmmojo_64.lib)
   target_link_options(wcocr PRIVATE "/DELAYLOAD:mmmojo_64.dll")
else()
   target_link_libraries(wcocr ${CMAKE_CURRENT_SOURCE_DIR}/wechat-ocr/spt/x86/libprotobuf-lite.lib ${CMAKE_CURRENT_SOURCE_DIR}/wechat-ocr/spt/x86/mmmojo.lib)
   target_link_options(wcocr PRIVATE "/DELAYLOAD:mmmojo.dll")
endif()
