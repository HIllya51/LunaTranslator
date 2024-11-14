
generate_product_version(
   versioninfohost
   NAME "LunaHost"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   ICON ${PATH_TO_APPLICATION_ICON}
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
   VERSION_REVISION ${VERSION_REVISION}
)

add_library(host
	host.cpp
	textthread.cpp
)
target_precompile_headers(host REUSE_FROM pch)
target_include_directories(host PUBLIC .)


add_library(LunaHostDll MODULE LunaHostDll.cpp  ${versioninfohost})
target_precompile_headers(LunaHostDll REUSE_FROM pch)
set_target_properties(LunaHostDll PROPERTIES OUTPUT_NAME "LunaHost${bitappendix}")
target_link_libraries(LunaHostDll pch host)

if(BUILD_CLI)
add_executable(LunaHostCLI LunaHostCLI.cpp  ${versioninfohost})
target_precompile_headers(LunaHostCLI REUSE_FROM pch)
set_target_properties(LunaHostCLI PROPERTIES OUTPUT_NAME "LunaHostCLI${bitappendix}")
target_link_libraries(LunaHostCLI pch host)
endif()

add_subdirectory(GUI)