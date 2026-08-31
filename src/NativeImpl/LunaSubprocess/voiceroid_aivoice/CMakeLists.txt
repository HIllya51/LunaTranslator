
add_library(voiceroid_aivoice INTERFACE)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    target_sources(voiceroid_aivoice INTERFACE main.cpp aitalked.cc aitalk_engine.cc AITalk_SDK.cc)
else()
    target_sources(voiceroid_aivoice INTERFACE main.cpp aitalked.cc)
endif()
target_link_libraries(voiceroid_aivoice INTERFACE magic_enum)