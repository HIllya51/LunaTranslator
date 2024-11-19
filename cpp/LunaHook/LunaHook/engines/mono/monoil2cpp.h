#define RESOLVE_IMPORT(name) name = (decltype(name))(GetProcAddress(game_module, #name))
#pragma once
void commonsolvemonostring(uintptr_t offset, TextBuffer *buffer);
void unity_ui_string_embed_fun(uintptr_t *offset, TextBuffer buff);

uintptr_t tryfindmonoil2cpp(const char *_dll, const char *_namespace, const char *_class, const char *_method, int paramCoun, bool strict = false);