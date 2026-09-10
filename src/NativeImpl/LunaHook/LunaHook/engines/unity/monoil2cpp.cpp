#include "mono.def.hpp"
#include "monoil2cpp.h"
extern CommonSharedMem *commonsharedmem;

extern "C" __declspec(dllexport) void luna_internal_unity_font_log(const wchar_t *text)
{
    if (text)
        Msg::Log(text);
}

monoil2cpp *g_monoil2cpp = nullptr;

namespace
{
    std::optional<std::wstring_view> readmonostring(void *ptr)
    {
        if (!ptr)
            return {};
        MonoString *string = (MonoString *)ptr;
        auto data = (wchar_t *)string->chars;
        auto len = string->length;
        if (!(len && data))
            return {};
        if (wcslen(data) != len)
            return {};
        return std::wstring_view(data, len);
    }
    void *createmonostring(std::wstring_view ws, MonoString *origin)
    {
        auto newstring = (MonoString *)malloc(sizeof(MonoString) + ws.size() + 2);
        MonoString __;
        origin = origin ? origin : &__;
        memcpy(newstring, origin, sizeof(MonoString));
        memcpy((wchar_t *)newstring->chars, ws.data(), ws.size() * 2);
        newstring->length = ws.size();
        return newstring;
    }
}

std::optional<std::wstring_view> commonsolvemonostring(uintptr_t arg)
{
    std::optional<std::wstring_view> sw;
    if (g_monoil2cpp)
        sw = g_monoil2cpp->get_string((void *)arg);
    if (!sw)
        sw = readmonostring((void *)arg);
    if (!sw)
        return {};
    if (sw.value().size() > TEXT_BUFFER_SIZE)
        return {};
    return sw;
}
void *monoil2cpp::create_string_csharp(std::wstring_view view, void *origin)
{
    void *newstring = create_string(view);
    if (!newstring)
        newstring = createmonostring(view, (MonoString *)origin);
    return newstring;
}
void unity_ui_string_embed_fun(uintptr_t &arg, TextBuffer buff)
{
    auto view = buff.viewW();
    arg = (uintptr_t)g_monoil2cpp->create_string_csharp(view, (void *)arg);
}

void monoil2cpp::load_on_main_seh()
{
    bool ok = false;
    __try
    {
        ok = load_managed_plugin_impl();
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        ok = false;
    }
    g_font_state = ok ? 4 : -1;
}

void monoil2cpp::ensure_tmp_font_loaded()
{
    if (!commonsharedmem || !commonsharedmem->unityfontdir[0])
        return;
    int s = g_font_state.load(std::memory_order_relaxed);
    if (s == 4 || s == -1)
        return;
    int expected = 0;
    if (!g_font_state.compare_exchange_strong(expected, 1, std::memory_order_acq_rel))
        return;
    load_on_main_seh();
}