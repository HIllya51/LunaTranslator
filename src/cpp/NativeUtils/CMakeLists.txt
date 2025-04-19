include(libmecab.cmake)
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
FetchContent_Declare(webview2 
    URL https://www.nuget.org/api/v2/package/Microsoft.Web.WebView2/1.0.2535.41
    URL_HASH SHA1=5991fa16cdbd1e7da9ac8226fd04470da4918337
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_MakeAvailable(tiny-aes rapidfuzz webview2 md4c)

add_library(md4c-all INTERFACE)
target_include_directories(md4c-all INTERFACE ${md4c_SOURCE_DIR}/src)
target_link_libraries(md4c-all INTERFACE md4c md4c-html)


add_library(webview2 INTERFACE)
target_include_directories(webview2 INTERFACE ${webview2_SOURCE_DIR}/build/native/include)
target_link_libraries(webview2 INTERFACE ${webview2_SOURCE_DIR}/build/native/${platform}/WebView2LoaderStatic.lib)

set(winrt_src winrt/winrtocr.cpp winrt/winrtsnapshot.cpp)
set(mshtml_src mshtml/SimpleBrowser.cpp mshtml/MWebBrowser.cpp)
set(webview2_src webview2/webview2.cpp webview2/webview2_impl.cpp)
set(loopback_src applicationloopbackaudio/runer.cpp applicationloopbackaudio/LoopbackCapture.cpp)


add_library(NativeUtils SHARED 
    globalmessagelistener.cpp AreoAcrylic.cpp screenshot.cpp ../implsapi.cpp hwnd.cpp theme.cpp version.cpp lnk.cpp muteprocess.cpp sapi_dll.cpp tools.cpp icon.cpp adapters.cpp appx.cpp
    ${loopback_src} ${winrt_src} ${mshtml_src} ${webview2_src} ${versioninfo}
)
target_precompile_headers(NativeUtils REUSE_FROM pch)

target_link_libraries(NativeUtils tiny-aes Dbghelp libmecab rapidfuzz webview2 mfuuid md4c-all dwmapi d3d11 ${YY_Thunks})

target_link_options(NativeUtils PRIVATE "/DELAYLOAD:Dbghelp.dll")
if(NOT WINXP)
    target_link_options(NativeUtils PRIVATE "/DELAYLOAD:MFPlat.dll")
    target_link_options(NativeUtils PRIVATE "/DELAYLOAD:dxgi.dll")
endif()