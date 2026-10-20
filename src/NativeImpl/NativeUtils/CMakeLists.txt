if(NOT WIN32)
    # md4c的option()会往cache里塞BUILD_SHARED_LIBS=ON，导致目标类型（静态/共享）
    # 随配置顺序漂移；这里固定为ON，保证mecab/tiny-aes等是带PIC的共享库，可链入.so
    set(BUILD_SHARED_LIBS ON)
endif()
include(libmecab.cmake)
include(FetchContent)

FetchContent_Declare(md4c
    GIT_REPOSITORY https://github.com/mity/md4c
    GIT_TAG release-0.5.3
    GIT_SHALLOW TRUE
)
FetchContent_Declare(tiny-aes
    GIT_REPOSITORY https://github.com/kokke/tiny-AES-c
    GIT_TAG master
    GIT_SHALLOW TRUE
)
FetchContent_Declare(rapidfuzz
    GIT_REPOSITORY https://github.com/rapidfuzz/rapidfuzz-cpp
    GIT_TAG main
    GIT_SHALLOW TRUE
)
option(BUILD_MD2HTML_EXECUTABLE "Whether to compile the md2html executable" OFF)
FetchContent_MakeAvailable(tiny-aes rapidfuzz md4c)

add_library(md4c-all INTERFACE)
target_include_directories(md4c-all INTERFACE ${md4c_SOURCE_DIR}/src)
target_link_libraries(md4c-all INTERFACE md4c md4c-html)

# 平台差异只在这里取值
if(WIN32)
    aux_source_directory(loopbackaudio loopbackaudio)
    aux_source_directory(winrt winrt)
    add_subdirectory(webview)
    add_subdirectory(bass)
    add_subdirectory(needprotobuf)

    set(nu_src
        memory.cpp
        devices.cpp
        dllanalysis.cpp
        globalmessagelistener.cpp
        AreoAcrylic.cpp
        screenshot.cpp
        hwnd.cpp
        theme.cpp
        lnk.cpp
        muteprocess.cpp
        sapi_dll.cpp
        tools.cpp
        winmisc.cpp
        icon.cpp
        adapters.cpp
        winutils.cpp
        ${loopbackaudio}
        ${winrt}
        ${versioninfo}
    )
    set(nu_winlibs
        pdh
        Mpr
        Psapi
        Dbghelp
        bassimp
        libbass
        webview
        mfuuid
        dwmapi
        d3d11
        version
        iphlpapi
        Mfplat
        DXGI
        Msimg32
        setupapi
        delayimp
        needprotobuf
        ${YY_Thunks}
        magic_enum
    )
    if(NOT WINXP)
        list(APPEND nu_winlibs ShCore Mmdevapi)
    endif()
    if(WIN10ABOVE)
        list(APPEND nu_winlibs windowsapp)
    endif()
    set(nu_winlinkopts
        "/DELAYLOAD:Dbghelp.dll"
        "/DELAYLOAD:SETUPAPI.dll"
        "/DELAYLOAD:MSIMG32.dll"
        "/DELAYLOAD:pdh.dll"
        "/DELAYLOAD:GDI32.dll"
        "/DELAYLOAD:IPHLPAPI.dll"
        "/DELAYLOAD:MMDevAPI.dll"
        "/DELAYLOAD:MFPlat.dll"
        "/DELAYLOAD:dxgi.dll"
        "/DELAYLOAD:d3d11.dll"
    )
else()
    # Linux：仅跨平台部分（tools.cpp：levenshtein/mecab/AES/Markdown2Html）
    set(nu_src tools.cpp)
endif()

add_library(NativeUtils SHARED ${nu_src})
target_precompile_headers(NativeUtils REUSE_FROM pch)
target_link_libraries(NativeUtils PRIVATE
    tiny-aes
    libmecab
    rapidfuzz
    md4c-all
    ${nu_winlibs}
)
target_link_options(NativeUtils PRIVATE ${nu_winlinkopts})
