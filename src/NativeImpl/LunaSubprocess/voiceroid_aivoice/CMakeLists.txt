
add_library(voiceroid_aivoice INTERFACE)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    target_sources(voiceroid_aivoice INTERFACE aitalk_engine.cc AITalk_SDK.cc main.cpp)
else()
    target_sources(voiceroid_aivoice INTERFACE aitalked.cc main.cpp)
endif()