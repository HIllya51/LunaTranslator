
add_library(commonengine INTERFACE)
target_sources(commonengine INTERFACE mono/impl_mono.cpp mono/monoil2cpp.cpp mono/mono.cpp mono/impl_il2cpp.cpp mages/mages.cpp v8/v8.cpp v8/httpserver.cpp python/python2.cpp python/python3.cpp python/python.cpp pchooks/pchooks.cpp lua/lua51.cpp)

