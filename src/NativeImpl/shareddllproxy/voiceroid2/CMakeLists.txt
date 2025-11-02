
add_library(voiceroid2 INTERFACE)
target_sources(voiceroid2 INTERFACE api_adapter.cc api_settings.cc ebyroid.cc voice2.cpp)