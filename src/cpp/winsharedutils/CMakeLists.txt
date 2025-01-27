
project(winsharedutils)


add_library(winsharedutils MODULE clipboard.cpp webview2.cpp AreoAcrylic.cpp screenshot.cpp ../implsapi.cpp hwnd.cpp theme.cpp version.cpp lnk.cpp levenshtein.cpp muteprocess.cpp sapi_dll.cpp simplemecab.cpp 
applicationloopbackaudio/runer.cpp applicationloopbackaudio/LoopbackCapture.cpp
SimpleBrowser.cpp MWebBrowser.cpp icon.cpp ${versioninfo})
target_precompile_headers(winsharedutils REUSE_FROM pch)
if(NOT WINXP)
target_link_libraries(winsharedutils rapidfuzz webview2 Mfplat mfuuid Mmdevapi dwmapi)
target_link_options(winsharedutils PRIVATE "/DELAYLOAD:Mmdevapi.dll")
target_link_options(winsharedutils PRIVATE "/DELAYLOAD:Mfplat.dll")
else()
target_link_libraries(winsharedutils webview2 ${YY_Thunks_for_WinXP})
endif()