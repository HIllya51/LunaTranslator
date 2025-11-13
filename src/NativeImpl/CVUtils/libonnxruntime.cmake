
include(FetchContent)

option(WIN10ABOVE "WIN10ABOVE" OFF)

#onnxruntime
#版本：
#1.13.1 最后一个原生支持win7的版本
#1.9.0 最早的可运行paddleocr的版本
#1.10.0 体积比1.9.0还要小一点
if(WIN10ABOVE)
    # https://github.com/microsoft/onnxruntime/issues/15255
    # DML和ort的版本必须对应，因此必须附带而非加载系统的，否则无法使用gpu
    
    if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
        set(ort_version 1.23.0) 
    else()
        set(ort_version 1.22.0) #之后不再有32位release
    endif()
    FetchContent_Declare(onnxruntime 
        URL https://www.nuget.org/api/v2/package/Microsoft.ML.OnnxRuntime.DirectML/${ort_version}
        DOWNLOAD_EXTRACT_TIMESTAMP true
    )
    FetchContent_MakeAvailable(onnxruntime)
    add_library(onnxruntime INTERFACE)
    target_include_directories(onnxruntime INTERFACE ${onnxruntime_SOURCE_DIR}/build/native/include)
    target_link_libraries(onnxruntime INTERFACE ${onnxruntime_SOURCE_DIR}/runtimes/win-${platform}/native/onnxruntime.lib)
    set(onnxruntime_DLL ${onnxruntime_SOURCE_DIR}/runtimes/win-${platform}/native/onnxruntime.dll)
    message(${onnxruntime_DLL})
    function(extract_last_version_simple file_path output_var)
        file(READ "${file_path}" file_content)
        # 使用贪婪匹配直接找到最后一个版本号
        string(REGEX MATCH ".*([0-9]+\\.[0-9]+\\.[0-9]+)" dummy "${file_content}")
        if(CMAKE_MATCH_1)
            set(${output_var} "${CMAKE_MATCH_1}" PARENT_SCOPE)
        else()
            set(${output_var} "" PARENT_SCOPE)
        endif()
    endfunction()
    extract_last_version_simple(${onnxruntime_SOURCE_DIR}/Microsoft.ML.OnnxRuntime.DirectML.nuspec directml_version)
    message(${directml_version})
    FetchContent_Declare(directml 
        URL https://www.nuget.org/api/v2/package/Microsoft.AI.DirectML/${directml_version}
        DOWNLOAD_EXTRACT_TIMESTAMP true
    )
    FetchContent_MakeAvailable(directml)
    set(directml_DLL ${directml_SOURCE_DIR}/bin/${platform}-win/DirectML.dll)
    message(${directml_DLL})
else()
    set(ort_version 1.10.0)

    FetchContent_Declare(onnxruntime 
        URL https://github.com/microsoft/onnxruntime/releases/download/v${ort_version}/onnxruntime-win-${platform}-${ort_version}.zip
        DOWNLOAD_EXTRACT_TIMESTAMP true
    )
    FetchContent_MakeAvailable(onnxruntime)
    add_library(onnxruntime INTERFACE)
    target_include_directories(onnxruntime INTERFACE ${onnxruntime_SOURCE_DIR}/include)
    target_link_libraries(onnxruntime INTERFACE ${onnxruntime_SOURCE_DIR}/lib/onnxruntime.lib)
    set(onnxruntime_DLL ${onnxruntime_SOURCE_DIR}/lib/onnxruntime.dll)
    message(${onnxruntime_DLL})
endif()