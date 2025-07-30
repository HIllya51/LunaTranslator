
add_library(lang_hook   INTERFACE)
add_library(lang_host   INTERFACE)
add_library(lang_ui     INTERFACE)
target_sources(lang_hook    INTERFACE Lang.cpp Lang_hook.cpp)
target_sources(lang_host    INTERFACE Lang.cpp Lang_host.cpp)
target_sources(lang_ui      INTERFACE Lang.cpp Lang_host.cpp Lang_ui.cpp)