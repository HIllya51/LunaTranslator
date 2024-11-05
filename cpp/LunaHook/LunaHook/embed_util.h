#ifndef __LUNA_EMBED_ENGINE_H
#define __LUNA_EMBED_ENGINE_H

extern CommonSharedMem *commonsharedmem;
extern DynamicShiftJISCodec *dynamiccodec;

namespace WinKey
{
    inline bool isKeyPressed(int vk) { return ::GetKeyState(vk) & 0xf0; }
    inline bool isKeyToggled(int vk) { return ::GetKeyState(vk) & 0x0f; }

    inline bool isKeyReturnPressed() { return isKeyPressed(VK_RETURN); }
    inline bool isKeyControlPressed() { return isKeyPressed(VK_CONTROL); }
    inline bool isKeyShiftPressed() { return isKeyPressed(VK_SHIFT); }
    inline bool isKeyAltPressed() { return isKeyPressed(VK_MENU); }
}
namespace Engine
{
    enum TextRole
    {
        UnknownRole = 0,
        ScenarioRole,
        NameRole,
        OtherRole,
        ChoiceRole = OtherRole,
        HistoryRole = OtherRole,
        RoleCount
    };
}
inline std::atomic<void (*)()> patch_fun = nullptr;
bool ReplaceFunction(PVOID oldf, PVOID newf, PVOID *pOrigin = nullptr);
bool check_embed_able(const ThreadParam &tp);
bool checktranslatedok(void *data, size_t len);
#endif