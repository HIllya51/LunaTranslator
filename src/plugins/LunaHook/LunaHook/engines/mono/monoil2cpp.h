#define RESOLVE_IMPORT(name) name = (decltype(name))(GetProcAddress(game_module, #name))

void commonsolvemonostring(uintptr_t offset, uintptr_t *data, size_t *len);

void unity_ui_string_hook_after(uintptr_t *offset, void *data, size_t len);

uintptr_t tryfindmonoil2cpp(const char *_dll, const char *_namespace, const char *_class, const char *_method, int paramCoun, bool strict = false);