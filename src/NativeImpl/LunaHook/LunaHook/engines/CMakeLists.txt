
add_library(commonengine INTERFACE)
target_sources(commonengine INTERFACE unity/monoil2cpp.cpp unity/mono.impl.cpp unity/unity.cpp unity/il2cpp.impl.cpp mages/mages.cpp v8/v8.cpp v8/httpserver.cpp python/python2.cpp python/python3.cpp python/python.cpp pchooks/pchooks.cpp lua/lua51.cpp)


set(csc "C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe")
set(mscorlib "C:/Windows/Microsoft.NET/Framework64/v4.0.30319/mscorlib.dll")


set(_lunatmp_src "${CMAKE_CURRENT_SOURCE_DIR}/unity/LunaTmpFontLoader.cs")
set(_lunatmp_dll "${binary_out_putpath}/LunaTmpFontLoader.dll")
add_custom_command(
    OUTPUT "${_lunatmp_dll}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${binary_out_putpath}"
    COMMAND "${csc}" /nologo /nostdlib /target:library /out:${_lunatmp_dll} /reference:${mscorlib} LunaTmpFontLoader.cs
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/unity"
    DEPENDS "${_lunatmp_src}"
    VERBATIM
)
add_custom_target(LunaTmpFontLoader ALL DEPENDS "${_lunatmp_dll}")