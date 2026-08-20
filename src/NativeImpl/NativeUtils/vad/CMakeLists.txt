
include(FetchContent)


set(_vad_ver "v1.13.6")
set(_vad_pkg "sherpa-onnx-${_vad_ver}-win-${platform}-shared-MD-Release")
set(_vad_url "https://github.com/k2-fsa/sherpa-onnx/releases/download/${_vad_ver}/${_vad_pkg}.tar.bz2")

FetchContent_Declare(sherpa_onnx URL "${_vad_url}")
FetchContent_Populate(sherpa_onnx)

set(_vad_root "${sherpa_onnx_SOURCE_DIR}")


add_library(vad INTERFACE)
aux_source_directory(${CMAKE_CURRENT_LIST_DIR} vad_src)

target_sources(vad INTERFACE "${vad_src}")

target_include_directories(vad INTERFACE "${_vad_root}/include")
target_link_libraries(vad INTERFACE "${_vad_root}/lib/sherpa-onnx-cxx-api.lib")

target_link_options(vad INTERFACE "/DELAYLOAD:sherpa-onnx-cxx-api.dll")