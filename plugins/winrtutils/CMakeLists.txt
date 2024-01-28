
project(winrtutils)


add_library(winrtutils MODULE winrtsnapshot.cpp cinterface.cpp dllmain.cpp pch.cpp winrtocr.cpp )

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set_target_properties(winrtutils PROPERTIES OUTPUT_NAME "winrtutils64")
else()
	set_target_properties(winrtutils PROPERTIES OUTPUT_NAME "winrtutils32")
endif()

	