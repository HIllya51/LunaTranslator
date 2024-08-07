
project(LUNA)

option(PYSTAND_CONSOLE "Build PyStand as a console application." OFF)


generate_product_version(
   versioninfo
   NAME "LunaTranslator"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)

set(sources PyStand.cpp luna.rc ${versioninfo})

#add_executable(LunaTranslator_debug ${sources})
#target_compile_definitions(LunaTranslator_debug PRIVATE PYSTAND_CONSOLE)
add_executable(LunaTranslator WIN32 ${sources})
add_executable(LunaTranslator_admin WIN32 ${sources})
set_target_properties(LunaTranslator_admin PROPERTIES LINK_FLAGS " /MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\" ")
#target_precompile_headers(LunaTranslator_debug REUSE_FROM pch) 
target_precompile_headers(LunaTranslator_admin REUSE_FROM pch) 
target_precompile_headers(LunaTranslator REUSE_FROM pch)