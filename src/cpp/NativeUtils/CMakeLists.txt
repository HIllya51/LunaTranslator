include(libmecab.cmake)
include(libwebview2.cmake)
include(FetchContent)

FetchContent_Declare(md4c
    GIT_REPOSITORY https://github.com/mity/md4c
    GIT_TAG release-0.5.2
)
FetchContent_Declare(maddy
    URL https://github.com/progsource/maddy/releases/download/1.5.0/maddy-src.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(tiny-aes 
    GIT_REPOSITORY https://github.com/kokke/tiny-AES-c
    GIT_TAG 23856752fbd139da0b8ca6e471a13d5bcc99a08d
)
FetchContent_Declare(rapidfuzz 
    GIT_REPOSITORY https://github.com/rapidfuzz/rapidfuzz-cpp 
    GIT_TAG 5d078a96d7b5e0c4c39b0295efd9d9280fa11a66
)
FetchContent_MakeAvailable(tiny-aes rapidfuzz md4c)

add_library(md4c-all INTERFACE)
target_include_directories(md4c-all INTERFACE ${md4c_SOURCE_DIR}/src)
target_link_libraries(md4c-all INTERFACE md4c md4c-html)


set(winrt_src winrt/winrtocr.cpp winrt/winrtsnapshot.cpp)
set(mshtml_src mshtml/SimpleBrowser.cpp mshtml/MWebBrowser.cpp)
set(webview2_src webview2/webview2.cpp webview2/webview2_impl.cpp)
set(loopback_src applicationloopbackaudio/runer.cpp applicationloopbackaudio/LoopbackCapture.cpp)


add_library(NativeUtils SHARED
    audiodevice.cpp
    globalmessagelistener.cpp AreoAcrylic.cpp screenshot.cpp hwnd.cpp theme.cpp version.cpp lnk.cpp muteprocess.cpp sapi_dll.cpp tools.cpp icon.cpp adapters.cpp appx.cpp
    ${loopback_src} ${winrt_src} ${mshtml_src} ${webview2_src} ${versioninfo}
)
target_precompile_headers(NativeUtils REUSE_FROM pch)
target_link_libraries(NativeUtils PRIVATE tiny-aes Dbghelp libmecab rapidfuzz webview2 mfuuid md4c-all dwmapi d3d11 version Mfplat DXGI)

if(MSVC)
    target_link_libraries(NativeUtils PRIVATE ${YY_Thunks})
    target_link_options(NativeUtils PRIVATE "/DELAYLOAD:Dbghelp.dll")
    if(NOT WINXP)
        target_link_libraries(NativeUtils PRIVATE ShCore Mmdevapi windowsapp)
        target_link_options(NativeUtils PRIVATE "/DELAYLOAD:MMDevAPI.dll")
        target_link_options(NativeUtils PRIVATE "/DELAYLOAD:MFPlat.dll")
        target_link_options(NativeUtils PRIVATE "/DELAYLOAD:dxgi.dll")
    endif()
else()
    target_link_libraries(NativeUtils PRIVATE ShCore Mmdevapi windowsapp)
endif()