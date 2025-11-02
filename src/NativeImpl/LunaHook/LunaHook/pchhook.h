#include "../include/pch.h"

// #define wcslen(XX) wcsnlen((XX), TEXT_BUFFER_SIZE*2)
// #define strlen(XX) strnlen((XX), TEXT_BUFFER_SIZE*2)

#include "texthook.h"
#include "main.h"
#include "util/stringfilters.h"
#include "memdbg/memsearch.h"
#include "util/util.h"
#include "ithsys/ithsys.h"
#include "pchooks/pchooks.h"
#include "cpputil/cppcstring.h"
#include "dyncodec/dynsjiscodec.h"
#include "dyncodec/dynsjis.h"
#include "disasm/disasm.h"
#include "engine.h"
#include "embed_util.h"
#include "hijackfuns.h"

#include "emulators/emujitarg.hpp"
#include "engines/mono/monoil2cpp.h"
#include "hookfinder.h"
#include "util/textunion.h"
#include "util/ntxpundef.h"

#define EXPAND_BRACKETS(...) EXPAND_BRACKETS_IMPL(__VA_ARGS__)
#define EXPAND_BRACKETS_IMPL(...) __VA_ARGS__

#define DECLARE_PLAIN_FUNCTION(FUNC) \
    __pragma(optimize("", off)) FUNC \
    __pragma(optimize("", on))

#define DECLARE_FUNCTION(NAME, ARGS) DECLARE_PLAIN_FUNCTION(void NAME(ARGS){})

#define ___WIDEN___(x) L##x
#define WIDEN(x) ___WIDEN___(x)