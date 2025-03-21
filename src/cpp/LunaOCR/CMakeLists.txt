project(LunaOCR)


if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    set(onnxruntimedir ${CMAKE_SOURCE_DIR}/libs/onnxruntime-win-x64-1.13.1)
else()
    set(onnxruntimedir ${CMAKE_SOURCE_DIR}/libs/onnxruntime-win-x86-1.13.1)
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