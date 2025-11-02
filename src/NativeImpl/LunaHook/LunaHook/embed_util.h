#ifndef __LUNA_EMBED_ENGINE_H_97D10217_04C3_42C6_9FCA_23DC5002B9EB
#define __LUNA_EMBED_ENGINE_H_97D10217_04C3_42C6_9FCA_23DC5002B9EB

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
void patch_fun_ptrs_patch_once();
inline std::vector<std::pair<void *, void *>> patch_fun_ptrs = {};
bool ReplaceFunction(PVOID oldf, PVOID newf, PVOID *pOrigin = nullptr);
bool check_embed_able(const ThreadParam &tp);
bool checktranslatedok(TextBuffer buff);
#endif