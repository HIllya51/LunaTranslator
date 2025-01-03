project(LunaOCR)

find_package(OnnxRuntime REQUIRED)
set(OpenCV_STATIC ON)
find_package(OpenCV REQUIRED)

add_library(LunaOCR SHARED OCR.cpp ${versioninfo})
target_link_libraries(LunaOCR ${OnnxRuntime_LIBS} ${OpenCV_LIBS} Clipper2Lib) 
target_precompile_headers(LunaOCR REUSE_FROM pch) 
