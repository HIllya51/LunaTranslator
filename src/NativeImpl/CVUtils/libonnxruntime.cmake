
include(FetchContent)

option(WIN10ABOVE "WIN10ABOVE" OFF)

# onnxruntime统一从nuget获取（github仓库已不可用）
# 版本：
# 1.13.1 最后一个原生支持win7的版本
# 1.9.0 最早的可运行paddleocr的版本
# 1.10.0 体积比1.9.0还要小一点
if(NOT WIN32)
    # Linux：CPU包，直接链接（DT_NEEDED），运行时靠 $ORIGIN rpath找到
    set(ort_version 1.24.4)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "(x86_|X86_|AMD64|amd64)i?64")
        set(ort_rid linux-x64)
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64)$")
        set(ort_rid linux-arm64)
    else()
        message(FATAL_ERROR "unsupported onnxruntime architecture: ${CMAKE_SYSTEM_PROCESSOR}")
    endif()
    set(ort_pkg Microsoft.ML.OnnxRuntime)
elseif(WIN10ABOVE)
    # https://github.com/microsoft/onnxruntime/issues/15255
    # DML和ort的版本必须对应，因此必须附带而非加载系统的，否则无法使用gpu
    if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
        set(ort_version 1.24.4)
    else()
        set(ort_version 1.22.1) #之后不再有32位release
    endif()
    set(ort_pkg Microsoft.ML.OnnxRuntime.DirectML)
else()
    # win7/xp：CPU包（win-x64/win-x86）
    set(ort_version 1.10.0)
    set(ort_pkg Microsoft.ML.OnnxRuntime)
endif()

FetchContent_Declare(onnxruntime
    URL https://www.nuget.org/api/v2/package/${ort_pkg}/${ort_version}
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_MakeAvailable(onnxruntime)

add_library(onnxruntime INTERFACE)
target_include_directories(onnxruntime INTERFACE ${onnxruntime_SOURCE_DIR}/build/native/include)

if(NOT WIN32)
    set(ort_lib ${onnxruntime_SOURCE_DIR}/runtimes/${ort_rid}/native/libonnxruntime.so)
    target_link_libraries(onnxruntime INTERFACE ${ort_lib})

    # 链接记录的DT_NEEDED是SONAME(libonnxruntime.so.1)；nuget包里只有
    # libonnxruntime.so单文件（无版本后缀无软链），拷出后自建SONAME软链
    add_custom_target(copy_onnxruntime_dll
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${ort_lib}
            ${CMAKE_FINAL_OUTPUT_DIRECTORY}
        COMMAND ln -sf libonnxruntime.so ${CMAKE_FINAL_OUTPUT_DIRECTORY}/libonnxruntime.so.1
    )
    add_dependencies(onnxruntime copy_onnxruntime_dll)
    return()
endif()

set(ort_lib ${onnxruntime_SOURCE_DIR}/runtimes/win-${platform}/native/onnxruntime.lib)
target_link_libraries(onnxruntime INTERFACE ${ort_lib})
set(onnxruntime_DLL ${onnxruntime_SOURCE_DIR}/runtimes/win-${platform}/native/onnxruntime.dll)

if(WIN10ABOVE)
    # DML版本从ort的nuspec读，保证与ort配套
    file(READ ${onnxruntime_SOURCE_DIR}/Microsoft.ML.OnnxRuntime.DirectML.nuspec nuspec)
    # 贪婪匹配取nuspec里最后一个版本号
    string(REGEX MATCH ".*([0-9]+\\.[0-9]+\\.[0-9]+)" dummy "${nuspec}")
    set(directml_version ${CMAKE_MATCH_1})
    FetchContent_Declare(directml
        URL https://www.nuget.org/api/v2/package/Microsoft.AI.DirectML/${directml_version}
        DOWNLOAD_EXTRACT_TIMESTAMP true
    )
    FetchContent_MakeAvailable(directml)

    add_custom_target(copy_directml_dll
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${directml_SOURCE_DIR}/bin/${platform}-win/DirectML.dll
            ${CMAKE_FINAL_OUTPUT_DIRECTORY}/DirectML.dll
    )
    add_dependencies(onnxruntime copy_directml_dll)
endif()

add_custom_target(copy_onnxruntime_dll
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${onnxruntime_DLL}
        ${CMAKE_FINAL_OUTPUT_DIRECTORY}/onnxruntime.dll
)
add_dependencies(onnxruntime copy_onnxruntime_dll)

target_link_options(onnxruntime INTERFACE "/DELAYLOAD:onnxruntime.dll")