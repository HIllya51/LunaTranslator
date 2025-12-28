
include(bass.cmake)

add_library(bassimp INTERFACE)
aux_source_directory(${CMAKE_CURRENT_LIST_DIR} bass_src)

target_sources(bassimp INTERFACE "${bass_src}")
