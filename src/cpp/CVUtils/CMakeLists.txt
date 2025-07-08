
#onnxruntime
#版本：
#1.13.1 最后一个原生支持win7的版本
#1.9.0 最早的可运行paddleocr的版本
#1.10.0 体积比1.9.0还要小一点
#
include(ExternalProject)
include(FetchContent)

FetchContent_Declare(clipper2 
    GIT_REPOSITORY https://github.com/AngusJohnson/Clipper2
    GIT_TAG Clipper2_1.5.4
)

if(WIN10ABOVE)
    set(mtmd "md")
else()
    set(mtmd "mt")
endif()

FetchContent_Declare(opencv 
    URL https://github.com/RapidAI/OpenCVBuilder/releases/download/4.7.0/opencv-4.7.0-windows-vs2019-${mtmd}.7z
    DOWNLOAD_EXTRACT_TIMESTAMP true
)

FetchContent_MakeAvailable(opencv clipper2)

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

include(libonnxruntime.cmake)


add_library(CVUtils MODULE)
if(WINXP)
    target_compile_definitions(CVUtils PRIVATE _Frees_ptr_opt_=)
endif()
target_precompile_headers(CVUtils REUSE_FROM pch)
target_sources(CVUtils PRIVATE similarity.cpp ortwrapper.cpp dbcrnn.cpp localocr.cpp ${versioninfo})
target_link_libraries(CVUtils PRIVATE Clipper2Lib libOpenCV onnxruntime dxgi version)
if(NOT WINXP)
    target_link_libraries(CVUtils PRIVATE d3d12)
endif()
target_link_libraries(CVUtils PRIVATE ${YY_Thunks} VC_LTL)
if(MSVC)
target_link_options(CVUtils PRIVATE "/DELAYLOAD:d3d12.dll")
target_link_options(CVUtils PRIVATE "/DELAYLOAD:dxgi.dll")
target_link_options(CVUtils PRIVATE "/DELAYLOAD:onnxruntime.dll")
endif()
if (NOT WINXP)
    add_custom_command(TARGET CVUtils
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${onnxruntime_DLL}
        ${CMAKE_FINAL_OUTPUT_DIRECTORY}/onnxruntime.dll
    )
    if(WIN10ABOVE)
        add_custom_command(TARGET CVUtils
            POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${directml_DLL}
            ${CMAKE_FINAL_OUTPUT_DIRECTORY}/DirectML.dll
        )
    endif()
endif()