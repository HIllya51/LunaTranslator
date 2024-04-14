
project(winsharedutils)


add_library(winsharedutils MODULE hwnd.cpp darklistener.cpp theme.cpp version.cpp otsu.cpp cinterface.cpp clipboard.cpp lnk.cpp dllmain.cpp levenshtein.cpp muteprocess.cpp sapi_dll.cpp simplemecab.cpp SimpleBrowser.cpp MWebBrowser.cpp icon.cpp)
target_link_libraries(winsharedutils dwmapi)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set_target_properties(winsharedutils PROPERTIES OUTPUT_NAME "winsharedutils64")
else()
	set_target_properties(winsharedutils PROPERTIES OUTPUT_NAME "winsharedutils32")
endif()

	