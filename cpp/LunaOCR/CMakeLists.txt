project(LunaOCR)

generate_product_version(
   versioninfo
   NAME "LunaTranslator OCR"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
)

find_package(OnnxRuntime REQUIRED)
set(OpenCV_STATIC ON)
find_package(OpenCV REQUIRED)

add_library(LunaOCR SHARED OCR.cpp ${versioninfo})
target_link_libraries(LunaOCR ${OnnxRuntime_LIBS} ${OpenCV_LIBS} Clipper2Lib ${YY_Thunks_for_WinXP}) 
target_precompile_headers(LunaOCR REUSE_FROM pch) 

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set_target_properties(LunaOCR PROPERTIES OUTPUT_NAME "LunaOCR64")
else()
	set_target_properties(LunaOCR PROPERTIES OUTPUT_NAME "LunaOCR32")
endif()