
#onnxruntime
#版本：
#1.13.1 最后一个原生支持win7的版本
#1.9.0 最早的可运行paddleocr的版本
#1.10.0 体积比1.9.0还要小一点
set(ort_version 1.10.0)
#

include(FetchContent)

FetchContent_Declare(clipper2 
    GIT_REPOSITORY https://github.com/AngusJohnson/Clipper2
    GIT_TAG 3dd975ad6d6d770ed5be02e5b898a0937c21b806
)
FetchContent_Declare(opencv 
    URL https://github.com/RapidAI/OpenCVBuilder/releases/download/4.7.0/opencv-4.7.0-windows-vs2019-mt.7z
    URL_HASH SHA1=fff392a1dab68b447c8ad06a60566e2967e7c04d
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(onnxruntime 
    URL https://github.com/microsoft/onnxruntime/releases/download/v${ort_version}/onnxruntime-win-${platform}-${ort_version}.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_MakeAvailable(onnxruntime opencv clipper2)

#Clipper2
file(GLOB Clipper2LibSrc ${clipper2_SOURCE_DIR}/CPP/Clipper2Lib/src/*.cpp)
add_library(Clipper2Lib ${Clipper2LibSrc})
target_include_directories(Clipper2Lib PUBLIC ${clipper2_SOURCE_DIR}/CPP/Clipper2Lib/include)
###

#OpenCV
add_library(libOpenCV INTERFACE)
target_include_directories(libOpenCV INTERFACE "${opencv_SOURCE_DIR}/windows-${platform}/include")
file(GLOB OpenCV_LIBS_STATIC_LIBS "${opencv_SOURCE_DIR}/windows-${platform}/${platform}/vc16/staticlib/*.lib")
target_link_libraries(libOpenCV INTERFACE "${OpenCV_LIBS_STATIC_LIBS}")
###

#onnxruntime
add_library(onnxruntime INTERFACE)
target_include_directories(onnxruntime INTERFACE ${onnxruntime_SOURCE_DIR}/include)
target_link_libraries(onnxruntime INTERFACE ${onnxruntime_SOURCE_DIR}/lib/onnxruntime.lib)
###


#由于onnxruntime无法被delayload，因此单独分离出来。
add_library(OrtWrapper SHARED ortwrapper.cpp ${versioninfo})
target_link_libraries(OrtWrapper onnxruntime) 
if(WINXP)
    target_compile_definitions(OrtWrapper PRIVATE _Frees_ptr_opt_=)
endif()
target_precompile_headers(OrtWrapper REUSE_FROM pch)

add_library(CVUtils SHARED)
target_precompile_headers(CVUtils REUSE_FROM pch)
target_sources(CVUtils PRIVATE similarity.cpp dbcrnn.cpp localocr.cpp ${versioninfo})
target_link_libraries(CVUtils Clipper2Lib OrtWrapper libOpenCV NativeUtils)
target_link_options(CVUtils PRIVATE "/DELAYLOAD:OrtWrapper.dll")
if ((NOT WINXP) AND (NOT EXISTS ${CMAKE_FINAL_OUTPUT_DIRECTORY}/onnxruntime.dll))
    add_custom_command(TARGET CVUtils
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        ${onnxruntime_SOURCE_DIR}/lib/onnxruntime.dll
        ${CMAKE_FINAL_OUTPUT_DIRECTORY}/onnxruntime.dll
    )
endif()