
include(libwebview2.cmake)

aux_source_directory(${CMAKE_CURRENT_LIST_DIR} webview_src)

add_library(webview INTERFACE)
target_sources(webview INTERFACE "${webview_src}")
target_link_libraries(webview INTERFACE webview2)