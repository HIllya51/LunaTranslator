
include(FetchContent)
FetchContent_Declare(libfvad 
    GIT_REPOSITORY https://github.com/dpirch/libfvad
    GIT_TAG master
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(libfvad)

add_library(vad INTERFACE)
aux_source_directory(${CMAKE_CURRENT_LIST_DIR} vad_src)

target_sources(vad INTERFACE "${vad_src}")
target_link_libraries(vad INTERFACE fvad)
