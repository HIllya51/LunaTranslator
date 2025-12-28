include(FetchContent)
FetchContent_Declare(bass24
    URL https://www.un4seen.com/files/bass24.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(bass_spx24
    URL https://www.un4seen.com/files/z/2/bass_spx24.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(bass_aac24
    URL https://www.un4seen.com/files/z/2/bass_aac24.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(bassopus24
    URL https://www.un4seen.com/files/bassopus24.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(bassenc24
    URL https://www.un4seen.com/files/bassenc24.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(bassenc_mp324
    URL https://www.un4seen.com/files/bassenc_mp324.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_Declare(bassenc_opus24
    URL https://www.un4seen.com/files/bassenc_opus24.zip
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_MakeAvailable(bass24 bass_spx24 bass_aac24 bassopus24 bassenc24 bassenc_mp324 bassenc_opus24)

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
    set(inter "/x64/")
else()
    set(inter "/")
endif()

set(BASS_MODULES
    bass
    bass_spx
    bass_aac
    bassopus
    bassenc
    bassenc_mp3
    bassenc_opus
)

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
