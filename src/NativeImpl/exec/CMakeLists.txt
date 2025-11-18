
project(LUNA)

option(PYSTAND_CONSOLE "Build PyStand as a console application." OFF)


include(FetchContent)

file(DOWNLOAD
    https://image.lunatranslator.org/luna.ico
    ${CMAKE_BINARY_DIR}/luna.ico
)

file(WRITE ${CMAKE_BINARY_DIR}/luna.rc "IDI_ICON1 ICON DISCARDABLE \"luna.ico\"")

set(sources PyStand.cpp ${CMAKE_BINARY_DIR}/luna.rc ${versioninfo} WjCryptLib_Sha512.c)

#add_executable(LunaTranslator_debug ${sources})
#target_compile_definitions(LunaTranslator_debug PRIVATE PYSTAND_CONSOLE)
add_executable(LunaTranslator WIN32 ${sources})
if(NOT WINXP)
add_executable(LunaTranslator_admin WIN32 ${sources})
endif()
set_target_properties(LunaTranslator PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
if(NOT WINXP)
set_target_properties(LunaTranslator_admin PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
endif()
if(MSVC)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 4)
    set_target_properties(LunaTranslator PROPERTIES LINK_FLAGS "/LARGEADDRESSAWARE")
    #set_target_properties(LunaTranslator_debug PROPERTIES LINK_FLAGS "/LARGEADDRESSAWARE")
    if(NOT WINXP)
        set_target_properties(LunaTranslator_admin PROPERTIES LINK_FLAGS "/LARGEADDRESSAWARE /MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\"")
    endif()
else()
    set_target_properties(LunaTranslator_admin PROPERTIES LINK_FLAGS "/MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\"")
endif()
endif()