
project(winsharedutils)

if(NOT WINXP)
set(winrtsource winrt/winrtocr.cpp winrt/winrtsnapshot.cpp)
else()
set(winrtsource winrt/xp.cpp)
endif()
add_library(winsharedutils MODULE globalmessagelistener.cpp webview2.cpp AreoAcrylic.cpp screenshot.cpp ../implsapi.cpp hwnd.cpp theme.cpp version.cpp lnk.cpp levenshtein.cpp muteprocess.cpp sapi_dll.cpp simplemecab.cpp 
applicationloopbackaudio/runer.cpp applicationloopbackaudio/LoopbackCapture.cpp
SimpleBrowser.cpp MWebBrowser.cpp icon.cpp ${versioninfo}
${winrtsource})
target_precompile_headers(winsharedutils REUSE_FROM pch)
if(NOT WINXP)
target_link_libraries(winsharedutils libmecab rapidfuzz webview2 Mfplat mfuuid Mmdevapi dwmapi DXGI d3d11 ${YY_Thunks})
target_link_options(winsharedutils PRIVATE "/DELAYLOAD:Mmdevapi.dll")
target_link_options(winsharedutils PRIVATE "/DELAYLOAD:Mfplat.dll")
else()
target_link_libraries(winsharedutils libmecab webview2 ${YY_Thunks})
endif()