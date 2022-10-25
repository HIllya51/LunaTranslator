include_directories(. util minhook/include )

if(${CMAKE_SIZEOF_VOID_P} EQUAL 8)
	set(minhook_src
		minhook/src/buffer.c
		minhook/src/hook.c
		minhook/src/trampoline.c
		minhook/src/hde/hde64.c
	)
	set(texthook_src
		main.cc
		texthook.cc
		hookfinder.cc
		engine/match.cc
		engine/match64.cc
		engine/native/pchooks.cc
		util/ithsys/ithsys.cc
		util/util.cc
	)
else()
	set(minhook_src
		minhook/src/buffer.c
		minhook/src/hook.c
		minhook/src/trampoline.c
		minhook/src/hde/hde32.c
	)
	set(texthook_src
		main.cc
		texthook.cc
		hookfinder.cc
		engine/engine.cc
		engine/match.cc
		engine/match32.cc
		engine/native/pchooks.cc
		util/util.cc
		util/ithsys/ithsys.cc
		util/disasm/disasm.cc
		util/memdbg/memsearch.cc
	)
endif()

add_library(minhook ${minhook_src})
add_library(texthook MODULE ${texthook_src})
# isn't there a better way to do this?
target_precompile_headers(texthook PRIVATE ../include/common.h)
if(NOT CMAKE_BUILD_TYPE MATCHES Debug)
	target_compile_options(minhook PRIVATE /MT)
	target_compile_options(texthook PRIVATE /MT)
	target_link_options(texthook PRIVATE /NODEFAULTLIB:MSVCRT)
endif()
target_link_libraries(texthook minhook)
