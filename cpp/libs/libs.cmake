
add_library(nlohmann INTERFACE)
target_include_directories(nlohmann INTERFACE ${CMAKE_CURRENT_LIST_DIR})

option(IS_LUNAHOOK "IS_LUNAHOOK" OFF)
if(IS_LUNAHOOK)
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/minhook ${CMAKE_BINARY_DIR}/minhook)
else()
    add_library(Detours ${CMAKE_CURRENT_LIST_DIR}/Detours/src/creatwth.cpp ${CMAKE_CURRENT_LIST_DIR}/Detours/src/detours.cpp ${CMAKE_CURRENT_LIST_DIR}/Detours/src/modules.cpp ${CMAKE_CURRENT_LIST_DIR}/Detours/src/disasm.cpp)
    target_include_directories(Detours PUBLIC ${CMAKE_CURRENT_LIST_DIR}/Detours/src)

    add_library(wil INTERFACE)
    target_include_directories(wil INTERFACE ${CMAKE_CURRENT_LIST_DIR}/wil/include)

    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/tinymp3 ${CMAKE_BINARY_DIR}/tinymp3)
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/rapidfuzz-cpp ${CMAKE_BINARY_DIR}/rapidfuzz-cpp)


    add_library(webview2 INTERFACE)
    target_include_directories(webview2 INTERFACE ${CMAKE_CURRENT_LIST_DIR}/webview2/Microsoft.Web.WebView2.1.0.2535.41/build/native/include)


    option(USE_VCLTL "USE_VCLTL" ON)
    if(USE_VCLTL)
        if(${CMAKE_SIZEOF_VOID_P} EQUAL 4)
            set(LTLPlatform "Win32")
        endif()
        if(WINXP)
            set(WindowsTargetPlatformMinVersion "5.1.2600.0")
        endif()
        include("${CMAKE_CURRENT_LIST_DIR}/VC-LTL helper for cmake.cmake")
    endif()


    file(GLOB Clipper2LibSrc ${CMAKE_CURRENT_LIST_DIR}/Clipper2/CPP/Clipper2Lib/src/*.cpp)
    add_library(Clipper2Lib ${Clipper2LibSrc})
    target_include_directories(Clipper2Lib PUBLIC ${CMAKE_CURRENT_LIST_DIR}/Clipper2/CPP/Clipper2Lib/include)


    if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
        set(OnnxRuntime_DIR ${CMAKE_CURRENT_LIST_DIR}/onnxruntime-static/windows-x64)
        set(OpenCV_DIR ${CMAKE_CURRENT_LIST_DIR}/opencv-static/windows-x64)
        set(OpenCV_ARCH x64)
    else()
        set(OnnxRuntime_DIR ${CMAKE_CURRENT_LIST_DIR}/onnxruntime-static/windows-x86)
        set(OpenCV_DIR ${CMAKE_CURRENT_LIST_DIR}/opencv-static/windows-x86)
        set(OpenCV_ARCH x86)
    endif()
    set(OpenCV_RUNTIME vc16)
endif()

option(WINXP "WINXP" OFF)
if(WINXP)
    set(YY_Thunks_for_WinXP ${CMAKE_CURRENT_LIST_DIR}/YY-Thunks/objs/X86/YY_Thunks_for_WinXP.obj)
else()
    set(YY_Thunks_for_WinXP)
endif()