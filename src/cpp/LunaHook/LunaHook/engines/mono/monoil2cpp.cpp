#include "def_mono.hpp"
#include "def_il2cpp.hpp"
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
        memcpy(newstring, origin, sizeof(MonoString));
        memcpy((wchar_t *)newstring->chars, ws.data(), ws.size() * 2);
        newstring->length = ws.size();
        return newstring;
    }
}
std::optional<std::wstring_view> commonsolvemonostring(uintptr_t arg)
{
    auto sw = il2cppfunctions::get_string((void *)arg);
    if (!sw)
        sw = monofunctions::get_string((void *)arg);
    if (!sw)
        sw = readmonostring((void *)arg);
    if (!sw)
        return {};
    if (sw.value().size() > TEXT_BUFFER_SIZE)
        return {};
    return sw;
}

void unity_ui_string_embed_fun(uintptr_t &arg, TextBuffer buff)
{
    auto view = buff.viewW();
    auto newstring = il2cppfunctions::create_string(view);
    if (!newstring)
        newstring = monofunctions::create_string(view);
    if (!newstring)
        newstring = createmonostring(view, (MonoString *)arg);
    arg = (uintptr_t)newstring;
}

uintptr_t tryfindmonoil2cpp(const char *_dll, const char *_namespace, const char *_class, const char *_method, int paramCoun, bool strict)
{
    auto addr = il2cppfunctions::get_method_pointer(_dll, _namespace, _class, _method, paramCoun, strict);
    if (addr)
        return addr;
    return monofunctions::get_method_pointer(_dll, _namespace, _class, _method, paramCoun, strict);
}
std::variant<monoloopinfo, il2cpploopinfo> loop_all_methods(std::optional<std::function<void(std::string &)>> show)
{
    auto ms = il2cppfunctions::loop_all_methods(show);
    if (ms.size())
        return ms;
    return monofunctions::loop_all_methods(show);
}