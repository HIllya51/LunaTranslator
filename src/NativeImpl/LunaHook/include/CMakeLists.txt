

add_library(pch pch.cpp stringutils.cpp types.cpp)
target_precompile_headers(pch PUBLIC pch.h)
