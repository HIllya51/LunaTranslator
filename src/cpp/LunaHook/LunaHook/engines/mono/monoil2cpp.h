#define RESOLVE_IMPORT(name) name = (decltype(name))(GetProcAddress(game_module, #name))
#pragma once
std::optional<std::wstring_view> commonsolvemonostring(uintptr_t arg);
void unity_ui_string_embed_fun(uintptr_t &arg, TextBuffer buff);
typedef std::vector<std::pair<int, uintptr_t>> il2cpploopinfo;
typedef std::vector<std::pair<uintptr_t, std::string>> monoloopinfo;
std::variant<monoloopinfo, il2cpploopinfo> loop_all_methods(std::optional<std::function<void(std::string &)>>);
uintptr_t tryfindmonoil2cpp(const char *_dll, const char *_namespace, const char *_class, const char *_method, int paramCoun, bool strict = false);