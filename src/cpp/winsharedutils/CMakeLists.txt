
project(winsharedutils)

set(winrt_src winrt/winrtocr.cpp winrt/winrtsnapshot.cpp)
set(mshtml_src mshtml/SimpleBrowser.cpp mshtml/MWebBrowser.cpp)
set(webview2_src webview2/webview2.cpp webview2/webview2_impl.cpp)
set(loopback_src applicationloopbackaudio/runer.cpp applicationloopbackaudio/LoopbackCapture.cpp)

add_library(winsharedutils MODULE 
    globalmessagelistener.cpp AreoAcrylic.cpp screenshot.cpp ../implsapi.cpp hwnd.cpp theme.cpp version.cpp lnk.cpp levenshtein.cpp muteprocess.cpp sapi_dll.cpp simplemecab.cpp icon.cpp 
    ${loopback_src} ${winrt_src} ${mshtml_src} ${webview2_src} ${versioninfo}
)
target_precompile_headers(winsharedutils REUSE_FROM pch)
if(NOT WINXP)
target_link_libraries(winsharedutils libmecab rapidfuzz webview2 mfuuid dwmapi d3d11 ${YY_Thunks})
else()
target_link_libraries(winsharedutils libmecab webview2 mfuuid ${YY_Thunks})
endif()