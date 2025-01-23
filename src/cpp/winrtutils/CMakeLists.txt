
project(winrtutils)


add_library(winrtutils MODULE winrtsnapshot.cpp winrtocr.cpp ${versioninfo})
target_precompile_headers(winrtutils REUSE_FROM pch) 
target_link_libraries(winrtutils wil dwmapi)