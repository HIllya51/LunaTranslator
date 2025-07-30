 

set(utils_src_common
dyncodec/dynsjiscodec.cc 
dyncodec/dynsjis.cc
ithsys/ithsys.cc
  memdbg/memsearch.cc
  stringfilters.cpp
  util.cc
)
add_library(utils INTERFACE)
target_sources(utils INTERFACE ${utils_src_common})
if(NOT (${CMAKE_SIZEOF_VOID_P} EQUAL 8))
  target_sources(utils INTERFACE disasm/disasm.cc)
endif()
