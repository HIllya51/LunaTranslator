   
const wchar_t* ALREADY_INJECTED = L"already injected";
const wchar_t* NEED_32_BIT = L"architecture mismatch: only x86 can inject this process";
const wchar_t* NEED_64_BIT = L"architecture mismatch: only x64 can inject this process";
const wchar_t* INJECT_FAILED = L"couldn't inject";
const wchar_t* LAUNCH_FAILED = L"couldn't launch";
const wchar_t* INVALID_CODE = L"invalid code";
const wchar_t* INVALID_CODEPAGE = L"couldn't convert text (invalid codepage?)";
const char* PIPE_CONNECTED = u8"pipe connected";
const char* INSERTING_HOOK = u8"inserting hook: %s";
const char* REMOVING_HOOK = u8"removing hook: %s";
const char* HOOK_FAILED = u8"failed to insert hook";
const char* TOO_MANY_HOOKS = u8"too many hooks: can't insert";
const char* HOOK_SEARCH_STARTING = u8"starting hook search";
const char* HOOK_SEARCH_INITIALIZING = u8"initializing hook search (%f%%)";
const char* NOT_ENOUGH_TEXT = u8"not enough text to search accurately";
const char* HOOK_SEARCH_INITIALIZED = u8"initialized hook search with %zd hooks";
const char* MAKE_GAME_PROCESS_TEXT = u8"please click around in the game to force it to process text during the next %d seconds";
const char* HOOK_SEARCH_FINISHED = u8"hook search finished, %d results found";
const char* OUT_OF_RECORDS_RETRY = u8"out of search records, please retry if results are poor (default record count increased)";
const char* FUNC_MISSING = u8"function not present";
const char* MODULE_MISSING = u8"module not present";
const char* GARBAGE_MEMORY = u8"memory constantly changing, useless to read";
const char* SEND_ERROR = u8"Send ERROR (likely an unstable/incorrect H-code)";
const char* READ_ERROR = u8"Reader ERROR (likely an incorrect R-code)";
const char* HIJACK_ERROR = u8"Hijack ERROR";
const char* COULD_NOT_FIND = u8"could not find text";

 

const wchar_t* CONSOLE = L"Console";

const wchar_t* CLIPBOARD = L"Clipboard";