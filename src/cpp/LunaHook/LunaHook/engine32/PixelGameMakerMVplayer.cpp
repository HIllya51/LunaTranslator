#include "PixelGameMakerMVplayer.h"

namespace agtk
{
  namespace TextGui
  {
    bool updateText()
    {
      bool succ = false;
      for (auto func : {
               "?updateText@TextGui@agtk@@QAEXV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@HHMMHHM@Z",
               "?updateText@TextGui@agtk@@QAEXV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@HHMMHH@Z",
               "?updateTextRender@TextGui@agtk@@QAEXV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@HHMMHH@Z",
               "?updateTextRender@TextGui@agtk@@QAEXV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@HHMMHHM@Z",
           })
      {
        auto updatetext = GetProcAddress(GetModuleHandle(NULL), func);
        if (!updatetext)
          continue;
        HookParam hp;
        hp.address = (DWORD)updatetext;
        hp.type = USING_STRING | CODEC_UTF8;
        hp.text_fun = [](hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
        {
          if (s->stack[6] >= 0x10)
          {
            buffer->from((char *)s->stack[1]);
          }
          else
          {
            buffer->from((char *)(&s->stack[1]));
          }
        };
        succ |= NewHook(hp, strSplit(std::string(func).substr(1), "@")[0].c_str());
      }
      return succ;
    }
  }
}
namespace cocos2d
{
  namespace __String
  {
    bool getCString(HMODULE cocos2d)
    {
      /*
      v43[0] = JS_DefineObject(a1, &v37, "text", &off_BB4A98, JS::NullPtr::constNullValue, 7);
        v40 = v43[0];
        JS_DefineFunctions(a1, v43, &off_BB4A6C);
        v34[0] = v41;
        v34[1] = -127;
        JS_DefineProperty(a1, v43, &unk_9F7908, v34, 5, 0, 0);
        v9 = (cocos2d::__String *)(*(int (__thiscall **)(cocos2d::__Dictionary *))(*(_DWORD *)TextData + 20))(TextData);
        CString = (char *)cocos2d::__String::getCString(v9);
        <---------CString
        sub_442F10(v45, CString);
        v47 = 0;
        v33[0] = (int)sub_6303F0(a1, (int)v45);
        v33[1] = v11;
        v47 = -1;
        sub_4434D0(v45);
        JS_DefineProperty(a1, v43, "name", v33, 5, 0, 0);
        v32[0] = (*(int (__thiscall **)(cocos2d::__Dictionary *))(*(_DWORD *)TextData + 28))(TextData);
        v32[1] = -127;
        JS_DefineProperty(a1, v43, "fontId", v32, 5, 0, 0);
        v31[0] = (*(int (__thiscall **)(cocos2d::__Dictionary *))(*(_DWORD *)TextData + 36))(TextData);
        v31[1] = -127;
        JS_DefineProperty(a1, v43, "letterSpacing", v31, 5, 0, 0);
        v30[0] = (*(int (__thiscall **)(cocos2d::__Dictionary *))(*(_DWORD *)TextData + 44))(TextData);
        v30[1] = -127;
        JS_DefineProperty(a1, v43, "lineSpacing", v30, 5, 0, 0);

      */
      auto PgetCString = GetProcAddress(cocos2d, "?getCString@__String@cocos2d@@QBEPBDXZ");
      if (!PgetCString)
        return false;
      HookParam hp;
      hp.address = (DWORD)PgetCString;
      hp.type = USING_STRING | CODEC_UTF8 | FULL_STRING;
      hp.text_fun = [](hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        char *result; // eax
        auto _this = s->argof_thiscall();
        result = (char *)_this + 28;
        if (*((DWORD *)_this + 12) >= 0x10u)
          return buffer->from(*(char **)result);
        return buffer->from(result);
      };
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        auto s = buffer->strA();
        if (all_ascii(s))
          return buffer->clear();
        if (s.find(":") != s.npos && s.find("/") != s.npos)
          return buffer->clear();
      };
      return NewHook(hp, "getCString");
    }
  }
  bool hook()
  {
    auto cocos2d = GetModuleHandle(L"libcocos2d.dll");
    if (!cocos2d)
      return false;

    return __String::getCString(cocos2d);
  }
}
bool PixelGameMakerMVplayer::attach_function()
{
  return agtk::TextGui::updateText() | cocos2d::hook();
}