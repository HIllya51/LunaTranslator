
project(LUNA)

option(PYSTAND_CONSOLE "Build PyStand as a console application." OFF)

# sources
set(sources PyStand.cpp luna.rc)

add_executable(LunaTranslator_debug ${sources})
target_compile_definitions(LunaTranslator_debug PRIVATE PYSTAND_CONSOLE)
add_executable(LunaTranslator WIN32 ${sources})
add_executable(LunaTranslator_admin WIN32 ${sources})
set_target_properties(LunaTranslator_admin PROPERTIES LINK_FLAGS " /MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\" ")