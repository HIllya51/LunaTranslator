
project(winsharedutils)


generate_product_version(
   versioninfo
   NAME "LunaTranslator winsharedutils"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)
add_library(winsharedutils MODULE mp3enc.cpp webview2_extra.cpp AreoAcrylic.cpp screenshot.cpp ../implsapi.cpp hwnd.cpp globalmessagelistener.cpp theme.cpp version.cpp otsu.cpp clipboard.cpp lnk.cpp levenshtein.cpp muteprocess.cpp sapi_dll.cpp simplemecab.cpp 
applicationloopbackaudio/runer.cpp applicationloopbackaudio/LoopbackCapture.cpp
SimpleBrowser.cpp MWebBrowser.cpp icon.cpp ${versioninfo})
target_precompile_headers(winsharedutils REUSE_FROM pch) 
target_link_libraries(winsharedutils tinymp3 rapidfuzz wil webview2 Mfplat mfuuid Mmdevapi ${YY_Thunks_for_WinXP})
target_link_options(winsharedutils PRIVATE "/DELAYLOAD:Mmdevapi.dll")
target_link_options(winsharedutils PRIVATE "/DELAYLOAD:Mfplat.dll")
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set_target_properties(winsharedutils PROPERTIES OUTPUT_NAME "winsharedutils64")
else()
	set_target_properties(winsharedutils PROPERTIES OUTPUT_NAME "winsharedutils32")
endif()
