
project(wcocr)

set(wcocr_src wechat-ocr/src/mojocall.cpp wechat-ocr/src/ocr_protobuf.pb.cc  wechat-ocr/src/wechatocr.cpp)
message(${wcocr_src})
string(REPLACE ";" ";../libs/" wcocr_src "${wcocr_src}")
message(${wcocr_src})
set(wcocr_src "../libs/${wcocr_src}")
message(${wcocr_src})


add_library(wcocr MODULE wcocr.cpp ${wcocr_src})
target_include_directories(wcocr PUBLIC ../libs/wechat-ocr/vs.proj PUBLIC ../libs/wechat-ocr/src PRIVATE ../libs/wechat-ocr/spt)

target_compile_options(wcocr
  PUBLIC 
  /std:c++17
  /MD
  /wd4018
  /DUNICODE
  /D_UNICODE
)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
   target_link_libraries(wcocr ${CMAKE_SOURCE_DIR}/libs/wechat-ocr/spt/x64/libprotobuf-lite.lib ${CMAKE_SOURCE_DIR}/libs/wechat-ocr/spt/x64/mmmojo_64.lib)
   target_link_options(wcocr PRIVATE "/DELAYLOAD:mmmojo_64.dll")
else()
   target_link_libraries(wcocr ${CMAKE_SOURCE_DIR}/libs/wechat-ocr/spt/x86/libprotobuf-lite.lib ${CMAKE_SOURCE_DIR}/libs/wechat-ocr/spt/x86/mmmojo.lib)
   target_link_options(wcocr PRIVATE "/DELAYLOAD:mmmojo.dll")
endif()
