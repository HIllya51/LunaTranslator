include(libmecab.cmake)
include(libwebview2.cmake)
include(FetchContent)

FetchContent_Declare(md4c
    GIT_REPOSITORY https://github.com/mity/md4c
    GIT_TAG master
    GIT_SHALLOW TRUE
)
FetchContent_Declare(tiny-aes 
    GIT_REPOSITORY https://github.com/kokke/tiny-AES-c
    GIT_TAG master
    GIT_SHALLOW TRUE
)
FetchContent_Declare(rapidfuzz 
    GIT_REPOSITORY https://github.com/rapidfuzz/rapidfuzz-cpp 
    GIT_TAG main
    GIT_SHALLOW TRUE
)
option(BUILD_MD2HTML_EXECUTABLE "Whether to compile the md2html executable" OFF)
FetchContent_MakeAvailable(tiny-aes rapidfuzz md4c)

add_library(md4c-all INTERFACE)
target_include_directories(md4c-all INTERFACE ${md4c_SOURCE_DIR}/src)
target_link_libraries(md4c-all INTERFACE md4c md4c-html)


set(winrt_src winrt/winrtocr.cpp winrt/winrtsnapshot.cpp)
set(loopback_src applicationloopbackaudio/runer.cpp applicationloopbackaudio/LoopbackCapture.cpp applicationloopbackaudio/eRenderRecord.cpp)

aux_source_directory(webview webviewimpls)

add_library(NativeUtils SHARED
    audiodevice.cpp
    globalmessagelistener.cpp AreoAcrylic.cpp screenshot.cpp hwnd.cpp theme.cpp lnk.cpp muteprocess.cpp sapi_dll.cpp tools.cpp icon.cpp adapters.cpp appx.cpp
    ${loopback_src} ${winrt_src} ${webviewimpls} ${versioninfo}
)
target_precompile_headers(NativeUtils REUSE_FROM pch)
target_link_libraries(NativeUtils PRIVATE tiny-aes Dbghelp libmecab rapidfuzz webview2 mfuuid md4c-all dwmapi d3d11 version Mfplat DXGI Msimg32)

target_link_libraries(NativeUtils PRIVATE ${YY_Thunks})
target_link_options(NativeUtils PRIVATE "/DELAYLOAD:Dbghelp.dll")
if(NOT WINXP)
    target_link_libraries(NativeUtils PRIVATE ShCore)
    target_link_libraries(NativeUtils PRIVATE Mmdevapi)
    target_link_options(NativeUtils PRIVATE "/DELAYLOAD:MMDevAPI.dll")
    target_link_options(NativeUtils PRIVATE "/DELAYLOAD:MFPlat.dll")
    target_link_options(NativeUtils PRIVATE "/DELAYLOAD:dxgi.dll")
    target_link_options(NativeUtils PRIVATE "/DELAYLOAD:d3d11.dll")
endif()
target_link_libraries(NativeUtils PRIVATE delayimp)


if(WIN10ABOVE)
	target_link_libraries(NativeUtils PRIVATE windowsapp)
endif()

add_subdirectory(needprotobuf)
target_link_libraries(NativeUtils PRIVATE needprotobuf)