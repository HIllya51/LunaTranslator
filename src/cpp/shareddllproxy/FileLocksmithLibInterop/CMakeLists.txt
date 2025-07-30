

add_library(FileLocksmith INTERFACE)
target_sources(FileLocksmith INTERFACE 
							FileLocksmith.cpp
							NtdllBase.cpp
							NtdllExtensions.cpp)
target_include_directories(FileLocksmith INTERFACE .)