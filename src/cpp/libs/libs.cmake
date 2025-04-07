
add_library(nlohmann INTERFACE)
target_include_directories(nlohmann INTERFACE ${CMAKE_CURRENT_LIST_DIR})

option(IS_LUNAHOOK "IS_LUNAHOOK" OFF)
if(IS_LUNAHOOK)
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/minhook ${CMAKE_BINARY_DIR}/minhook)
else()
    # add_library(Detours ${CMAKE_CURRENT_LIST_DIR}/Detours/src/creatwth.cpp ${CMAKE_CURRENT_LIST_DIR}/Detours/src/detours.cpp ${CMAKE_CURRENT_LIST_DIR}/Detours/src/modules.cpp ${CMAKE_CURRENT_LIST_DIR}/Detours/src/disasm.cpp)
    # target_include_directories(Detours PUBLIC ${CMAKE_CURRENT_LIST_DIR}/Detours/src)


    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/rapidfuzz-cpp)

    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/mecab/mecab/src)


    add_library(webview2 INTERFACE)
    target_include_directories(webview2 INTERFACE ${CMAKE_CURRENT_LIST_DIR}/webview2/Microsoft.Web.WebView2.1.0.2535.41/build/native/include)
    if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
        target_link_libraries(webview2 INTERFACE ${CMAKE_CURRENT_LIST_DIR}/webview2/Microsoft.Web.WebView2.1.0.2535.41/build/native/x64/WebView2LoaderStatic.lib)
    else()
        target_link_libraries(webview2 INTERFACE ${CMAKE_CURRENT_LIST_DIR}/webview2/Microsoft.Web.WebView2.1.0.2535.41/build/native/x86/WebView2LoaderStatic.lib)
    endif()

    option(USE_VCLTL "USE_VCLTL" ON)
    if(USE_VCLTL)
        if(${CMAKE_SIZEOF_VOID_P} EQUAL 4)
            set(LTLPlatform "Win32")
        endif()
        if(WINXP)
            set(WindowsTargetPlatformMinVersion "5.1.2600.0")
        endif()
        include("${CMAKE_CURRENT_LIST_DIR}/VC-LTL helper for cmake.cmake")
    endif()

endif()

option(WINXP "WINXP" OFF)
if(WINXP)
    add_definitions(-DWINXP=${WINXP})
    set(YY_Thunks ${CMAKE_CURRENT_LIST_DIR}/YY-Thunks/objs/X86/YY_Thunks_for_WinXP.obj)
else()
    if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
        set(YY_Thunks ${CMAKE_CURRENT_LIST_DIR}/YY-Thunks/objs/X64/YY_Thunks_for_Win7.obj)
    else()
        set(YY_Thunks ${CMAKE_CURRENT_LIST_DIR}/YY-Thunks/objs/X86/YY_Thunks_for_Win7.obj)
    endif()
endif()
if(NOT EXISTS ${YY_Thunks})
    set(YY_Thunks )
endif()