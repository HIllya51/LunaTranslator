project(LunaOCR)

generate_product_version(
   versioninfo
   NAME "LunaTranslator OCR"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)


set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

include(${CMAKE_CURRENT_SOURCE_DIR}/../libs/onnxruntime-static/OnnxRuntimeWrapper.cmake)

find_package(OnnxRuntime REQUIRED)
if (OnnxRuntime_FOUND)
    message(STATUS "OnnxRuntime_LIBS: ${OnnxRuntime_LIBS}")
    message(STATUS "OnnxRuntime_INCLUDE_DIRS: ${OnnxRuntime_INCLUDE_DIRS}")
else ()
    message(FATAL_ERROR "onnxruntime Not Found!")
endif (OnnxRuntime_FOUND)

# OpenCV
set(BUILD_SHARED_LIBS false)
if (CMAKE_CL_64)
    set(OpenCV_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../libs/opencv-static/windows-x64")
    link_directories(${OpenCV_DIR}/x64/vc16/staticlib)
    include(${OpenCV_DIR}/x64/vc16/staticlib/OpenCVConfig.cmake)

else ()
    set(OpenCV_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../libs/opencv-static/windows-x86")
    link_directories(${OpenCV_DIR}/x86/vc16/staticlib)
    include(${OpenCV_DIR}/x86/vc16/staticlib/OpenCVConfig.cmake)
endif ()

set(OpenCV_LIBS opencv_core;opencv_features2d;opencv_flann;opencv_highgui;opencv_imgcodecs;opencv_imgproc;opencv_photo;opencv_video)

add_library(LunaOCR SHARED OCR.cpp ${versioninfo})
target_link_libraries(LunaOCR ${OnnxRuntime_LIBS} ${OpenCV_LIBS} Clipper2Lib) 
target_include_directories(LunaOCR PRIVATE ${OpenCV_DIR}/include)
target_precompile_headers(LunaOCR REUSE_FROM pch) 

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set_target_properties(LunaOCR PROPERTIES OUTPUT_NAME "LunaOCR64")
else()
	set_target_properties(LunaOCR PROPERTIES OUTPUT_NAME "LunaOCR32")
endif()