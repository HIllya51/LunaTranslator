

include(ExternalProject)
include(FetchContent)

if(NOT WIN32)
    # 同NativeUtils：固定库类型，避免md4c泄漏的BUILD_SHARED_LIBS导致顺序漂移
    set(BUILD_SHARED_LIBS ON)
endif()

FetchContent_Declare(clipper2
    GIT_REPOSITORY https://github.com/AngusJohnson/Clipper2
    GIT_TAG main
    GIT_SHALLOW TRUE
)

# OpenCV按平台获取，最后统一链到${cv_opencv_lib}
if(WIN32)
    if(IS_STATIC)
        set(mtmd "mt")
    else()
        set(mtmd "md")
    endif()

    FetchContent_Declare(opencv
        URL https://github.com/RapidAI/OpenCVBuilder/releases/download/4.7.0/opencv-4.7.0-windows-vs2019-${mtmd}.7z
        DOWNLOAD_EXTRACT_TIMESTAMP true
    )
    FetchContent_MakeAvailable(opencv)

    #OpenCV
    add_library(libOpenCV INTERFACE)
    target_include_directories(libOpenCV INTERFACE "${opencv_SOURCE_DIR}/windows-${platform}/include")
    file(GLOB OpenCV_LIBS_STATIC_LIBS "${opencv_SOURCE_DIR}/windows-${platform}/${platform}/vc16/staticlib/*.lib")
    target_link_libraries(libOpenCV INTERFACE "${OpenCV_LIBS_STATIC_LIBS}")
    ###

    set(cv_opencv_lib libOpenCV)
else()
    find_package(OpenCV REQUIRED COMPONENTS core imgproc)
    set(cv_opencv_lib ${OpenCV_LIBS})
endif()

FetchContent_MakeAvailable(clipper2)

#Clipper2
file(GLOB Clipper2LibSrc ${clipper2_SOURCE_DIR}/CPP/Clipper2Lib/src/*.cpp)
add_library(Clipper2Lib ${Clipper2LibSrc})
target_include_directories(Clipper2Lib PUBLIC ${clipper2_SOURCE_DIR}/CPP/Clipper2Lib/include)
###

include(libonnxruntime.cmake)

if(WIN32)
    set(cv_versioninfo ${versioninfo})
endif()

add_library(CVUtils MODULE
    similarity.cpp
    ortwrapper.cpp
    dbcrnn.cpp
    localocr.cpp
    ${cv_versioninfo}
)
target_precompile_headers(CVUtils REUSE_FROM pch)
target_link_libraries(CVUtils PRIVATE Clipper2Lib ${cv_opencv_lib} onnxruntime)

if(WIN32)
    if(WINXP)
        target_compile_definitions(CVUtils PRIVATE _Frees_ptr_opt_=)
    endif()
    target_link_libraries(CVUtils PRIVATE dxgi version)
    if(NOT WINXP)
        target_link_libraries(CVUtils PRIVATE d3d12)
    endif()
    target_link_libraries(CVUtils PRIVATE ${YY_Thunks} NativeUtils delayimp)
    target_link_options(CVUtils PRIVATE "/DELAYLOAD:d3d12.dll")
    target_link_options(CVUtils PRIVATE "/DELAYLOAD:dxgi.dll")
else()
    # 运行时在模块自身目录找libonnxruntime.so
    set_target_properties(CVUtils PROPERTIES BUILD_RPATH "\$ORIGIN" INSTALL_RPATH "\$ORIGIN")
endif()
