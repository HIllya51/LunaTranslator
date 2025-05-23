
project(LUNA)

option(PYSTAND_CONSOLE "Build PyStand as a console application." OFF)


set(sources PyStand.cpp luna.rc ${versioninfo})

#add_executable(LunaTranslator_debug ${sources})
#target_compile_definitions(LunaTranslator_debug PRIVATE PYSTAND_CONSOLE)
add_executable(LunaTranslator WIN32 ${sources})
if(NOT WINXP)
add_executable(LunaTranslator_admin WIN32 ${sources})
endif()
if(WIN10ABOVE)
target_compile_definitions(LunaTranslator INTERFACE -DWIN10ABOVE=1)
endif()
set_target_properties(LunaTranslator PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
if(NOT WINXP)
set_target_properties(LunaTranslator_admin PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
if(WIN10ABOVE)
target_compile_definitions(LunaTranslator_admin INTERFACE -DWIN10ABOVE=1)
endif()
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