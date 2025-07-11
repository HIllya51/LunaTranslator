
add_library(emulators)

target_include_directories(emulators PRIVATE .)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8) 
    target_sources(emulators PRIVATE 
                            PCSX2.cpp PCSX2_1.cpp
                            rpcs3_1.cpp
                            rpcs3.cpp Ryujinx.cpp
                            vita3k.cpp vita3k_1.cpp
                            yuzu.cpp yuzu_1.cpp
                            ppsspp.cpp ppsspp_1.cpp)
else()
    target_sources(emulators PRIVATE ppsspp.cpp ppsspp_1.cpp)
endif()
target_precompile_headers(emulators REUSE_FROM pchhook)
