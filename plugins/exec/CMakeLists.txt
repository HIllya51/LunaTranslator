
project(LUNA)

   
add_executable(LunaTranslator luna.cpp luna.rc) 
#target_link_options(LunaTranslator PRIVATE /MANIFESTUAC:level="asInvoker")

add_executable(LunaTranslator_admin luna.cpp luna.rc)
set_target_properties(LunaTranslator_admin PROPERTIES LINK_FLAGS " /MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\" ")

#target_link_options(LunaTranslator_admin PRIVATE /MANIFESTUAC:level="requireAdministrator")
#这个仅在visualstdio下管用，vscode cmake不管用了。
 