
project(winrtutils)

generate_product_version(
   versioninfo
   NAME "LunaTranslator winrtutils"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)

add_library(winrtutils MODULE winrtsnapshot.cpp cinterface.cpp dllmain.cpp pch.cpp winrtocr.cpp ${versioninfo})

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set_target_properties(winrtutils PROPERTIES OUTPUT_NAME "winrtutils64")
else()
	set_target_properties(winrtutils PROPERTIES OUTPUT_NAME "winrtutils32")
endif()

	