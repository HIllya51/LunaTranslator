
include(FetchContent)
set(BASS_MODULE_URLS
    "bass,https://www.un4seen.com/files/bass24.zip"
    "bass_spx,https://www.un4seen.com/files/z/2/bass_spx24.zip"
    "bass_aac,https://www.un4seen.com/files/z/2/bass_aac24.zip"
    "bassopus,https://www.un4seen.com/files/bassopus24.zip"
    "bassenc,https://www.un4seen.com/files/bassenc24.zip"
    "bassenc_mp3,https://www.un4seen.com/files/bassenc_mp324.zip"
    "bassenc_opus,https://www.un4seen.com/files/bassenc_opus24.zip"
)

foreach(item ${BASS_MODULE_URLS})
    string(REPLACE "," " " item_list "${item}")
    separate_arguments(item_list)
    list(GET item_list 0 module)
    list(GET item_list 1 url)
    FetchContent_Declare(${module}24
        URL ${url}
        DOWNLOAD_EXTRACT_TIMESTAMP true
    )
    list(APPEND BASS_DECLARE_LIST ${module}24)
    list(APPEND BASS_MODULES ${module})
endforeach()

FetchContent_MakeAvailable(${BASS_DECLARE_LIST})

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    set(inter "/x64/")
else()
    set(inter "/")
endif()

add_library(libbass INTERFACE)

foreach(module ${BASS_MODULES}) 
    target_include_directories(libbass 
        INTERFACE ${${module}24_SOURCE_DIR}/c
    )
    target_link_libraries(libbass 
        INTERFACE ${${module}24_SOURCE_DIR}/c${inter}${module}.lib
    )
    target_link_options(libbass INTERFACE "/DELAYLOAD:${module}.dll")
    add_custom_target(copy_${module}_dll
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${${module}24_SOURCE_DIR}${inter}${module}.dll"
            "${CMAKE_FINAL_OUTPUT_DIRECTORY}/${module}.dll"
    )
    add_dependencies(libbass copy_${module}_dll)
endforeach()
