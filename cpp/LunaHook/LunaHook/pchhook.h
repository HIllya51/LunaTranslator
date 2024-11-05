#include "../include/pch.h"

// #define wcslen(XX) wcsnlen((XX), TEXT_BUFFER_SIZE*2)
// #define strlen(XX) strnlen((XX), TEXT_BUFFER_SIZE*2)

#include "main.h"
#include "stackoffset.hpp"
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

#include "Lang/Lang.h"
#include "veh_hook.h"
#include "engines/emujitarg.hpp"
#include "engines/mono/monoil2cpp.h"
#include "hookfinder.h"
#include "util/textunion.h"
#include "util/ntxpundef.h"
