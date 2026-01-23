

add_library(pch hookcode.cpp pch.cpp stringutils.cpp types.cpp)
target_precompile_headers(pch PUBLIC pch.h)
