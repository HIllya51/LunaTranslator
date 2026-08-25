
add_library(voiceroid_aivoice INTERFACE)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    target_sources(voiceroid_aivoice INTERFACE aitalk_engine.cc main.cpp)
else()
    target_sources(voiceroid_aivoice INTERFACE aitalked.cc aitalked_func.cc main.cpp)
endif()