add_library(host
	host.cpp
	textthread.cpp
	hookcode.cpp
)
target_precompile_headers(host REUSE_FROM pch)

add_subdirectory(CLI)
