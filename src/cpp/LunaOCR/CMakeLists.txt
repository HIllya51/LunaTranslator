project(LunaOCR)

file(GLOB Clipper2LibSrc ${CMAKE_SOURCE_DIR}/libs/Clipper2/CPP/Clipper2Lib/src/*.cpp)
add_library(Clipper2Lib ${Clipper2LibSrc})
target_include_directories(Clipper2Lib PUBLIC ${CMAKE_SOURCE_DIR}/libs/Clipper2/CPP/Clipper2Lib/include)


if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    set(OpenCV_DIR ${CMAKE_SOURCE_DIR}/libs/opencv-static/windows-x64)
    set(OpenCV_ARCH x64)
else()
    set(OpenCV_DIR ${CMAKE_SOURCE_DIR}/libs/opencv-static/windows-x86)
    set(OpenCV_ARCH x86)
endif()
set(OpenCV_RUNTIME vc16)

#onnxruntime版本：
#1.13.1 最后一个原生支持win7的版本
#1.9.0 最早的可运行paddleocr的版本
#1.10.0 体积比1.9.0还要小一点

set(onnxruntime_version 1.10.0)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    set(onnxruntimedir ${CMAKE_SOURCE_DIR}/libs/onnxruntime-win-x64-${onnxruntime_version})
else()
    set(onnxruntimedir ${CMAKE_SOURCE_DIR}/libs/onnxruntime-win-x86-${onnxruntime_version})
endif()

add_library(onnxruntime INTERFACE)
target_include_directories(onnxruntime INTERFACE ${onnxruntimedir}/include)
target_link_libraries(onnxruntime INTERFACE ${onnxruntimedir}/lib/onnxruntime.lib)


set(OpenCV_STATIC ON)
find_package(OpenCV REQUIRED)

add_library(LunaOCR SHARED OCR.cpp ${versioninfo})
target_link_libraries(LunaOCR  ${OpenCV_LIBS} Clipper2Lib onnxruntime) 
target_precompile_headers(LunaOCR REUSE_FROM pch) 

if (NOT EXISTS ${CMAKE_FINAL_OUTPUT_DIRECTORY}/onnxruntime.dll)
	add_custom_command(TARGET LunaOCR
		POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        ${onnxruntimedir}/lib/onnxruntime.dll
        ${CMAKE_FINAL_OUTPUT_DIRECTORY}/onnxruntime.dll
	)
endif()