 

set(utils_src_common
dyncodec/dynsjiscodec.cc 
dyncodec/dynsjis.cc
ithsys/ithsys.cc
  memdbg/memsearch.cc
  stringfilters.cpp
  util.cc
)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
  add_library(utils ${utils_src_common}   )
else()
  add_library(utils ${utils_src_common} disasm/disasm.cc)
endif()

target_precompile_headers(utils REUSE_FROM pchhook)

