﻿if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
  set(Detours ${CMAKE_CURRENT_LIST_DIR}/Detours-4.0.1/lib.X64/detours.lib)
else()
  set(Detours ${CMAKE_CURRENT_LIST_DIR}/Detours-4.0.1/lib.X86/detours.lib)
endif()

include_directories(${CMAKE_CURRENT_LIST_DIR})
include_directories(${CMAKE_CURRENT_LIST_DIR}/Detours-4.0.1/include)

include_directories(${CMAKE_CURRENT_LIST_DIR}/wil/include)
include_directories(${CMAKE_CURRENT_LIST_DIR}/miniaudio)
include_directories(${CMAKE_CURRENT_LIST_DIR}/tinymp3)
include_directories(${CMAKE_CURRENT_LIST_DIR}/rapidfuzz-cpp)

include_directories(${CMAKE_CURRENT_LIST_DIR}/webview2/Microsoft.Web.WebView2.1.0.2535.41/build/native/include)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 4)
    set(LTLPlatform "Win32")
endif()
include("${CMAKE_CURRENT_LIST_DIR}/VC-LTL helper for cmake.cmake")