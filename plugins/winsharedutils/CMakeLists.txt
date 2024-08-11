
project(winsharedutils)


generate_product_version(
   versioninfo
   NAME "LunaTranslator winsharedutils"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)
add_library(tinymp3 ../libs/tinymp3/shine_mp3.c)
add_library(winsharedutils MODULE mp3enc.cpp webview2_extra.cpp AreoAcrylic.cpp screenshot.cpp ../implsapi.cpp hwnd.cpp globalmessagelistener.cpp theme.cpp version.cpp otsu.cpp clipboard.cpp lnk.cpp dllmain.cpp levenshtein.cpp muteprocess.cpp sapi_dll.cpp simplemecab.cpp SimpleBrowser.cpp MWebBrowser.cpp icon.cpp ${versioninfo})
target_precompile_headers(winsharedutils REUSE_FROM pch) 
target_link_libraries(winsharedutils tinymp3)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set_target_properties(winsharedutils PROPERTIES OUTPUT_NAME "winsharedutils64")
else()
	set_target_properties(winsharedutils PROPERTIES OUTPUT_NAME "winsharedutils32")
endif()
