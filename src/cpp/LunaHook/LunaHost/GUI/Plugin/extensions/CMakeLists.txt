cmake_policy(SET CMP0037 OLD)

include_directories(../)
add_library(extpch text.cpp)
target_precompile_headers(extpch PUBLIC extpch.h)

set(disttarget "${CMAKE_SOURCE_DIR}/builds/plugin${bitappendix}")
message(${disttarget})
function(add_library_and_link_target TARGET_NAME)
    add_library(${TARGET_NAME} MODULE ${ARGN} ../extensionimpl.cpp)
    target_precompile_headers(${TARGET_NAME} REUSE_FROM extpch)
    target_link_libraries(${TARGET_NAME} PRIVATE extpch shell32 winhttp Qt5::Widgets Qt5::WebSockets)
    set_target_properties(${TARGET_NAME} PROPERTIES 
        LIBRARY_OUTPUT_DIRECTORY ${disttarget}
        LIBRARY_OUTPUT_DIRECTORY_DEBUG ${disttarget}
        LIBRARY_OUTPUT_DIRECTORY_RELEASE ${disttarget}
    )
        
    
endfunction()

add_library_and_link_target(Bing\ Translate bingtranslate.cpp translatewrapper.cpp network.cpp)
#add_library_and_link_target(Copy\ to\ Clipboard copyclipboard.cpp)
add_library_and_link_target(DeepL\ Translate deepltranslate.cpp translatewrapper.cpp network.cpp)


add_library_and_link_target(DevTools\ DeepL\ Translate devtoolsdeepltranslate.cpp devtools.cpp translatewrapper.cpp network.cpp)
add_library_and_link_target(DevTools\ Papago\ Translate devtoolspapagotranslate.cpp devtools.cpp translatewrapper.cpp network.cpp)
add_library_and_link_target(DevTools\ Systran\ Translate devtoolssystrantranslate.cpp devtools.cpp translatewrapper.cpp network.cpp)
add_library_and_link_target(Extra\ Newlines extranewlines.cpp)
add_library_and_link_target(Extra\ Window extrawindow.cpp)
add_library_and_link_target(Google\ Translate googletranslate.cpp translatewrapper.cpp network.cpp)
add_library_and_link_target(Regex\ Filter regexfilter.cpp)
add_library_and_link_target(Regex\ Replacer regexreplacer.cpp)
add_library_and_link_target(Remove\ Repeated\ Characters removerepeatchar.cpp)
add_library_and_link_target(Remove\ Repeated\ Phrases removerepeatphrase.cpp)
add_library_and_link_target(Remove\ Repeated\ Phrases\ 2 removerepeatphrase2.cpp)
add_library_and_link_target(Remove\ 30\ Repeated\ Sentences removerepeatsentence.cpp)
add_library_and_link_target(Replacer replacer.cpp)
add_library_and_link_target(Styler styler.cpp)
add_library_and_link_target(Thread\ Linker threadlinker.cpp)



if (NOT EXISTS ${disttarget}/Qt5WebSockets.dll AND NOT EXISTS ${disttarget}/Qt5WebSocketsd.dll)
add_custom_command(TARGET DevTools\ DeepL\ Translate
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_CURRENT_BINARY_DIR}/windeployqt"
    COMMAND set PATH=%PATH%$<SEMICOLON>${qt5_install_prefix}/bin
    COMMAND Qt5::windeployqt --dir ${disttarget} "${disttarget}/DevTools\ DeepL\ Translate.dll"  --release
)
endif()
