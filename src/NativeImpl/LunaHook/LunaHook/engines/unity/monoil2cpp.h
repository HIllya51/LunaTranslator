#define RESOLVE_IMPORT(name) name = (decltype(name))(GetProcAddress(game_module, #name))
#pragma once
typedef std::vector<std::pair<int, uintptr_t>> il2cpploopinfo;
typedef std::vector<std::pair<uintptr_t, std::string>> monoloopinfo;

struct monoil2cpp
{
    virtual void *get_method_pointer(const char *assemblyName, const char *namespaze,
                                     const char *klassName, const char *name, int argsCount, bool strict) = 0;
    virtual void *get_type_pointer(const char *assemblyName, const char *namespaze,
                                   const char *klassName, bool strict) = 0;
    virtual void *get_class_pointer(const char *assemblyName, const char *namespaze,
                                    const char *klassName, bool strict) = 0;

    virtual std::optional<std::wstring_view> get_string(void *ptr) = 0;
    virtual void *create_string(std::wstring_view ws) = 0;
    virtual std::variant<monoloopinfo, il2cpploopinfo> loop_all_methods(std::function<void(const std::string &)> show) = 0;

    virtual void apply_font(void *self) = 0;

    virtual ~monoil2cpp() = default;
    void *create_string_csharp(std::wstring_view, void *origin = nullptr);

    void ensure_tmp_font_loaded();
private:
    virtual bool load_managed_plugin_impl() = 0;
    std::atomic<int> g_font_state{0};
    void load_on_main_seh();
};

extern monoil2cpp *g_monoil2cpp;
monoil2cpp *create_mono_runtime(HMODULE module);
monoil2cpp *create_il2cpp_runtime(HMODULE module);

std::optional<std::wstring_view> commonsolvemonostring(uintptr_t arg);
void unity_ui_string_embed_fun(uintptr_t &arg, TextBuffer buff);
