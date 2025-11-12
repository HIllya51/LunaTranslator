set(YY_Thunks_VERSION "v1.1.7")
option(WINXP "WINXP" OFF)
option(WIN10ABOVE "WIN10ABOVE" ON)
option(USE_VC_LTL "USE_VC_LTL" OFF)

include(FetchContent)
FetchContent_Declare(yy_thunks 
    URL https://github.com/Chuyu-Team/YY-Thunks/releases/download/${YY_Thunks_VERSION}/YY-Thunks-Objs.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(vc_ltl 
    URL https://github.com/Chuyu-Team/VC-LTL5/releases/download/v5.2.1/VC-LTL-Binary.7z
    DOWNLOAD_EXTRACT_TIMESTAMP true
)

if(USE_VC_LTL)
    if(WINXP)
        set(WindowsTargetPlatformMinVersion "5.1.2600.0")
    endif()
    FetchContent_MakeAvailable(vc_ltl)
    include("${vc_ltl_SOURCE_DIR}/VC-LTL helper for cmake.cmake")
endif()

if(WIN10ABOVE)
    set(YY_Thunks )
else()
    FetchContent_MakeAvailable(yy_thunks)
    if(WINXP)
        add_definitions(-DWINXP=${WINXP})
        set(YY_Thunks ${yy_thunks_SOURCE_DIR}/objs/X86/YY_Thunks_for_WinXP.obj)
    else()
        if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
            set(YY_Thunks ${yy_thunks_SOURCE_DIR}/objs/X64/YY_Thunks_for_Win7.obj)
        else()
            set(YY_Thunks ${yy_thunks_SOURCE_DIR}/objs/X86/YY_Thunks_for_Win7.obj)
        endif()
    endif()
endif()