#include "Lucifen.h"
/********************************************************************************************
Lucifen hook:
  Game folder contains *.lpk. Used by Navel games.
  Hook is same to GetTextExtentPoint32A, use ESP to split name.
********************************************************************************************/
bool InsertLucifenHook()
{
  // BOOL GetTextExtentPoint32(
  //   _In_   HDC hdc,
  //   _In_   LPCTSTR lpString,
  //   _In_   int c,
  //   _Out_  LPSIZE lpSize
  // );
  HookParam hp;
  hp.address = (DWORD)::GetTextExtentPoint32A;
  hp.offset = stackoffset(2); // arg2 lpString
  hp.split = regoffset(esp);
  hp.length_offset = 3;
  hp.type = USING_STRING | USING_SPLIT;
  ConsoleOutput("INSERT Lucifen");
  return NewHook(hp, "Lucifen");
  // RegisterEngineType(ENGINE_LUCIFEN);
}
namespace
{
  bool hook()
  {
    // まじかるカナン -RISEA-
    auto oldoutline = (ULONG)GetProcAddress(GetModuleHandle(L"gdi32.dll"), "GetGlyphOutline");
    auto addr = MemDbg::findCallerAddress(oldoutline, 0xec8b55, processStartAddress, processStopAddress);
    if (!addr)
      addr = MemDbg::findCallerAddress((ULONG)GetGlyphOutlineA, 0xec8b55, processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.split = stackoffset(6);
    hp.type = CODEC_ANSI_BE | USING_SPLIT;
    return NewHook(hp, "Lucifen2");
  }
}

void hookBefore_navel(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{

  auto text = std::string((char *)s->stack[1]); // text in arg1

  if (text.find("$&") != text.npos)
  {
    text = text.substr(text.find("$&") + 2);
  }
  if (text[text.size() - 1] == '$')
    text = text.substr(0, text.size() - 1);

  buffer->from(text);
}
void hookafter_navel(hook_context *s, TextBuffer buffer)
{
  auto text = std::string((char *)s->stack[1]); // text in arg1
  auto split = s->stack[0];                     // retaddr

  std::string newData = buffer.strA();

  if (text.find("$&") != text.npos)
  {
    newData = text.substr(0, text.find("$&") + 2) + newData;
  }
  if (text[text.size() - 1] == '$')
    newData = newData + "$";

  strcpy((char *)s->stack[1], newData.c_str());
  // s->stack[1] = (ULONG)newData.data();
}

bool attach_navel(ULONG startAddress, ULONG stopAddress) // attach scenario
{
  // 通过搜索3C 9F(i > 0x9Fu shiftjis范围判断)找到。
  //   int __thiscall sub_455AB0(int this, _BYTE *a2)
  // {
  //   LPCSTR **v2; // ebx
  //   int v3; // edi
  //   _BYTE *v4; // ebp
  //   char v5; // cl
  //   _BYTE *v6; // ebx
  //   int v7; // esi
  //   unsigned __int8 v8; // al
  //   char v9; // al
  //   const CHAR **v10; // ebx
  //   bool v11; // zf
  //   const CHAR *v12; // eax
  //   unsigned int v13; // esi
  //   char *v14; // eax
  //   char *v16; // ecx
  //   unsigned __int8 v17; // al
  //   char v18; // al
  //   const CHAR ***v19; // ebp
  //   const CHAR *v20; // esi
  //   int v21; // eax
  //   unsigned __int8 v22; // al
  //   char v23; // cl
  //   int v24; // esi
  //   LPCSTR **j; // ebp
  //   char v26; // al
  //   LPCSTR **v27; // ebx
  //   char v28; // al
  //   char v29; // al
  //   char v30; // al
  //   unsigned int v31; // esi
  //   unsigned __int8 *v32; // eax
  //   char v33; // al
  //   int v34; // eax
  //   unsigned __int8 *v35; // ebx
  //   unsigned __int8 v36; // al
  //   char v37; // al
  //   const CHAR ***v38; // ebp
  //   const CHAR *v39; // esi
  //   int v40; // eax
  //   CHAR *v41; // edi
  //   char v42; // al
  //   unsigned __int8 v43; // al
  //   unsigned __int8 v44; // al
  //   unsigned __int16 *v45; // ebp
  //   unsigned __int16 *v46; // edi
  //   unsigned int v47; // eax
  //   __int16 v48; // dx
  //   unsigned __int16 *v49; // esi
  //   unsigned int v51; // [esp+14h] [ebp-4h]
  //   char *i; // [esp+1Ch] [ebp+4h]
  //   unsigned int v53; // [esp+1Ch] [ebp+4h]

  const uint8_t bytes[] = {
      0x50,
      0xff, 0x15, 0xfc, 0xd0, 0x4e, 0x00,
      0x03, 0xf0,
      0x83, 0xc3, 0x04,
      0xb1, 0x01};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;

  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
  hp.text_fun = hookBefore_navel;
  hp.embed_fun = hookafter_navel;
  hp.embed_hook_font = F_GetGlyphOutlineA | F_GetTextExtentPoint32A;
  return NewHook(hp, "LucifenEmbed");
}
namespace
{ // unnamed
  namespace ScenarioHook
  {

    std::unordered_set<UINT64> textHashes_;

    namespace Private
    {

      ULONG scenarioOffset_,
          nameOffset_;

      std::string replaceNewLines(const std::string &data)
      {
        std::string ret;
        // ret.replace("\n", 1, "\x00\x5b\x0c\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00", 0xc + 2);
        for (auto p = data.c_str(); *p;)
          if (*p == '\n')
          {
            ret.append("\x00\x5b\x0c\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00", 0xc + 2);
            p++;
          }
          else
          {
            ret.push_back(*p++);
            if (*p && dynsjis::isleadbyte(p[-1]))
              ret.push_back(*p++);
          }

        // std::string ret;
        // do {
        //   ret.append(start, p - start);
        //   if (dynsjis::prevchar(p, start) == p - 1) {
        //     ret.append("\x00\x5b\x0c\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00", 0xc + 2);
        //     p++;
        //   } else {
        //     start = p;
        //     p = ::strchr(p, '\n');
        //   }
        // } while (p && *p);
        return ret;
      }

      /**
       *  Sample game: 猫撫ディストーション
       *
       *  0x5b is the text to skip next character
       *
       *  Ruby:
       *  014BB52C  81 77 8C F5 00 5B 1C 00 00 00 1B 00 00 00 01 00  『光.[.......
       *  014BB53C  00 00 03 0B 00 00 00 83 72 83 62 83 4F 83 6F 83  .....ビッグバ・
       *  014BB54C  93 00 81 78 82 CC 91 4F 81 5C 81 5C 00 5B 0C 00  ・』の前――.[..
       *  014BB55C  00 00 0E 00 00 00 00 00 00 00 82 C2 82 DC 82 E8  .........つまり
       *  014BB56C  81 41 89 46 92 88 82 AA 90 B6 82 DC 82 EA 82 E9  、宇宙が生まれる
       *  014BB57C  91 4F 82 A9 82 E7 82 A0 82 C1 82 BD 82 E0 82 CC  前からあったもの
       *  014BB58C  81 42 00 00 00 00 00 00 00 00 00 00 00 00 00 00  。..............
       *  014BB59C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  No ruby:
       *  014BB52C  82 B6 82 E1 82 A0 81 41 81 77 8C BE 97 74 81 78  じゃあ、『言葉』
       *  014BB53C  82 C1 82 C4 89 BD 82 C8 82 F1 82 BE 81 48 6F 83  って何なんだ？o・
       *  014BB54C  93 00 81 78 82 CC 91 4F 81 5C 81 5C 00 5B 0C 00  ・』の前――.[..
       *  014BB55C  00 00 0E 00 00 00 00 00 00 00 82 C2 82 DC 82 E8  .........つまり
       *  014BB56C  81 41 89 46 92 88 82 AA 90 B6 82 DC 82 EA 82 E9  、宇宙が生まれる
       *  014BB57C  91 4F 82 A9 82 E7 82 A0 82 C1 82 BD 82 E0 82 CC  前からあったもの
       *  014BB58C  81 42 00 00 00 00 00 00 00 00 00 00 00 00 00 00  。..............
       *  014BB59C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014BB5AC  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014BB5BC  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014BB5CC  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  014BB52C  96 85 82 CC 8B D5 00 5B 16 00 00 00 1B 00 00 00  妹の琴.[......
       *  014BB53C  01 00 00 00 03 05 00 00 00 82 B1 82 C6 00 8E 71  ......こと.子
       *  014BB54C  00 5B 14 00 00 00 1B 00 00 00 01 00 00 00 03 03  .[.........
       *  014BB55C  00 00 00 82 B1 00 82 CD 82 BB 82 A4 8C BE 82 C1  ...こ.はそう言っ
       *  014BB56C  82 BD 81 42 82 C6 82 A2 82 A4 88 D3 96 A1 82 F0  た。という意味を
       *  014BB57C  97 5E 82 A6 82 BD 82 CC 81 76 82 BD 82 E0 82 CC  与えたの」たもの
       *  014BB58C  81 42 00 00 00 00 00 00 00 00 00 00 00 00 00 00  。..............
       *  014BB59C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014BB5AC  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014BB5BC  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014BB5CC  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  New line:
       *  014D7D39  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7D49  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7D59  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7D69  00 00 00 00 00 01 00 E6 01 00 00 54 01 00 00 00  ......・..T...
       *  014D7D79  00 00 00 B0 11 52 00 D8 CD 4D 01 44 EE E9 07 D8  ...ｰR.ﾘﾍMD鵫ﾘ
       *  014D7D89  CD 4D 01 00 00 00 00 00 00 00 00 00 00 00 00 00  ﾍM.............
       *  014D7D99  00 00 00 F0 50 4E 01 0C 53 4E 01 F0 54 4E 01 10  ...N.SNN
       *  014D7DA9  00 00 00 00 00 00 00 82 BB 82 B5 82 C4 89 B4 82  .......そして俺・
       *  014D7DB9  C9 82 E0 81 41 00 5B 0C 00 00 00 0E 00 00 00 00  ﾉも、.[........
       *  014D7DC9  00 00 00 90 7E 96 5B 82 CC 82 B1 82 EB 82 A9 82  ...厨房のころか・
       *  014D7DD9  E7 8E 6C 94 4E 8A D4 81 41 96 88 93 FA 91 B1 82  邇l年間、毎日続・
       *  014D7DE9  AF 82 C4 82 A2 82 E9 82 B1 82 C6 82 AA 82 A0 82  ｯていることがあ・
       *  014D7DF9  E9 81 42 00 00 00 00 00 00 00 00 00 00 00 00 00  驕B.............
       *  014D7E09  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E19  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E29  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E39  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E49  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E59  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E69  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E79  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E89  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  014D7E99  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       */
      template <typename strT>
      strT ltrimScenarioText(strT p)
      {
        while (p[0] == 0 && p[1] == 0x5b && p[2] > 0)
          p += p[2] + 2;
        return p;
      }
      std::string parseScenarioText(const char *p, const char *end)
      {
        int size = ::strlen(p);
        if (end > p && end - p < size)
          size = end - p;
        std::string ret;
        if (size)
          ret = std::string(p, size);
        // if ((uint8_t)p[ret.size() - 1] == 0x93 && (uint8_t)p[ret.size() - 1] == 0x83)// trim encindg \x83\x93
        //   return ret.left(ret.size() - 2);
        for (p += ret.size(); (!end || p < end) && p[1] == 0x5b && p[2] > 0; p += ret.size())
        {
          // if (p[2] == 0xc && p[6] == 0xe) {
          //   ret.push_back('\n');
          //   ret.push_back('\n'); // insert double new lines
          // }
          p += p[2] + 2;
          size = ::strlen(p);
          if (end > p && end - p < size)
            size = end - p;
          ret.append(p, size);
        }
        return ret;
      }

      // bool dispatchNameText(char *text, ULONG split,hook_context*s,void* data, size_t* len1,uintptr_t*role)
      // {
      //   enum { capacity = 0x10 }; // excluding '\0'
      //   *role = Engine::NameRole ;

      //   if (!*text)
      //     return false;

      //   write_string_overwrite(data,len1,text);
      //   return true;
      // }

      void dispatchScenarioText(char *text, ULONG split, hook_context *s, TextBuffer *buffer, uintptr_t *role)
      {
        // text[0] could be \0
        *role = Engine::ScenarioRole;
        auto scenarioEndAddress = (LPSTR *)(text + 0x1000);
        auto scenarioEnd = *scenarioEndAddress;
        if (!Engine::isAddressReadable(scenarioEnd))
          scenarioEnd = nullptr;
        // DOUT("warning: scenario end NOT FOUND");

        text = ltrimScenarioText(text);
        if (!*text)
          return;
        std::string oldData = parseScenarioText(text, scenarioEnd);
        buffer->from(oldData);
      }
      bool dispatchNameTextafter(char *text, ULONG split, hook_context *s, void *data, uintptr_t len1)
      {
        std::string oldData = text;
        auto newData = std::string((char *)data, len1);
        enum
        {
          capacity = 0x10
        }; // excluding '\0'
        int size = newData.size();
        if (size > capacity)
          size = capacity;
        else if (size < oldData.size())
          ::memset(text + size, 0, oldData.size() - size);

        ::memcpy(text, newData.c_str(), size);
        return true;
      }

      void dispatchScenarioTextafter(char *text, ULONG split, hook_context *s, TextBuffer buffer)
      {
        auto scenarioEndAddress = (LPSTR *)(text + 0x1000);
        auto scenarioEnd = *scenarioEndAddress;
        if (!Engine::isAddressReadable(scenarioEnd))
          scenarioEnd = nullptr;
        // DOUT("warning: scenario end NOT FOUND");

        text = ltrimScenarioText(text);
        if (!*text)
          return;
        std::string oldData = parseScenarioText(text, scenarioEnd);
        auto newData = buffer.strA();
        if (newData.empty() || newData == oldData)
          return;

        if (newData.find('\n') != newData.npos)
          newData = replaceNewLines(newData);

        if (scenarioEnd > text && scenarioEnd - text > newData.size())
          ::memset(text + newData.size(), 0, scenarioEnd - text - newData.size());
        else if (oldData.size() > newData.size())
          ::memset(text + newData.size(), 0, oldData.size() - newData.size());

        //::strcpy(text, newData.constData());
        ::memcpy(text, newData.c_str(), newData.size() + 1);

        *scenarioEndAddress = text + newData.size(); // FIXME: THis sometimes does not work
      }
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        auto self = (LPSTR)s->ecx;
        ULONG retaddr = s->stack[0];
        //  bool b1=  dispatchNameText(self + nameOffset_, retaddr,s,data,len1,role);
        dispatchScenarioText(self + scenarioOffset_, retaddr, s, buffer, split);
      }
      void hookafter(hook_context *s, TextBuffer buffer)
      {
        auto self = (LPSTR)s->ecx;
        ULONG retaddr = s->stack[0];
        //  dispatchNameTextafter(self + nameOffset_, retaddr,s,data,len1);
        dispatchScenarioTextafter(self + scenarioOffset_, retaddr, s, buffer);
      }
    } // namespace Private

    /**
     *  Debugging method:
     *  - Hijack GetGlyphOutlineA
     *    There is only one GetGlyphOutlineA
     *  - Find all text in memory
     *    There are two matches.
     *    One is current text with fixed address
     *    One is all text with fixed address
     *  - Find all text address on the stack
     *    There is one function use it as arg1 and as future text
     *    ecx is the current text instead
     *
     *  Sample game: プリズム・プリンセス
     *  name = ecx + 0xadd1
     *  scenario = ecx + 0xae48
     *  scenario end = ecx + 0xbe48
     *
     *  00441E3F   90               NOP
     *  00441E40   83EC 1C          SUB ESP,0x1C
     *  00441E43   53               PUSH EBX
     *  00441E44   56               PUSH ESI
     *  00441E45   8BF1             MOV ESI,ECX
     *  00441E47   8B9E 48BE0000    MOV EBX,DWORD PTR DS:[ESI+0xBE48]
     *  00441E4D   2BDE             SUB EBX,ESI
     *  00441E4F   81EB 48AE0000    SUB EBX,0xAE48
     *  00441E55   75 0B            JNZ SHORT .00441E62
     *  00441E57   5E               POP ESI
     *  00441E58   B8 01000000      MOV EAX,0x1
     *  00441E5D   5B               POP EBX
     *  00441E5E   83C4 1C          ADD ESP,0x1C
     *  00441E61   C3               RETN
     *  00441E62   8B86 AC040000    MOV EAX,DWORD PTR DS:[ESI+0x4AC]
     *  00441E68   55               PUSH EBP
     *  00441E69   57               PUSH EDI
     *  00441E6A   50               PUSH EAX
     *  00441E6B   8BCE             MOV ECX,ESI
     *  00441E6D   E8 9E6CFFFF      CALL .00438B10
     *  00441E72   8A96 DE050000    MOV DL,BYTE PTR DS:[ESI+0x5DE]
     *  00441E78   8B8E 909E0000    MOV ECX,DWORD PTR DS:[ESI+0x9E90]
     *  00441E7E   8BBE 489E0000    MOV EDI,DWORD PTR DS:[ESI+0x9E48]
     *  00441E84   84D2             TEST DL,DL
     *  00441E86   0F94C0           SETE AL
     *  00441E89   84C0             TEST AL,AL
     *  00441E8B   884424 13        MOV BYTE PTR SS:[ESP+0x13],AL
     *  00441E8F   C741 20 00000000 MOV DWORD PTR DS:[ECX+0x20],0x0
     *  00441E96   74 0D            JE SHORT .00441EA5
     *  00441E98   8BCE             MOV ECX,ESI
     *
     *  00441E9A   E8 4136FFFF      CALL .004354E0
     *  00441E9F   8987 A8030000    MOV DWORD PTR DS:[EDI+0x3A8],EAX
     *  00441EA5   8D86 48AE0000    LEA EAX,DWORD PTR DS:[ESI+0xAE48]	; jichi: this is the scenari text
     *  00441EAB   53               PUSH EBX
     *  00441EAC   50               PUSH EAX
     *  00441EAD   8BCF             MOV ECX,EDI
     *  00441EAF   E8 EC6B0000      CALL .00448AA0
     *  00441EB4   8D9E E2AD0000    LEA EBX,DWORD PTR DS:[ESI+0xADE2]	; jichi: this is the character name
     *  00441EBA   8D86 D1AD0000    LEA EAX,DWORD PTR DS:[ESI+0xADD1]	; jichi: this is the name text
     *  00441EC0   53               PUSH EBX
     *  00441EC1   50               PUSH EAX
     *  00441EC2   8BCF             MOV ECX,EDI
     *  00441EC4   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
     *  00441EC8   E8 836B0000      CALL .00448A50
     *
     *  00441ECD   8A4424 13        MOV AL,BYTE PTR SS:[ESP+0x13]
     *  00441ED1   84C0             TEST AL,AL
     *  00441ED3   74 30            JE SHORT .00441F05
     *  00441ED5   6A 01            PUSH 0x1
     *  00441ED7   8BCF             MOV ECX,EDI
     *  00441ED9   E8 726D0000      CALL .00448C50
     *  00441EDE   803B 00          CMP BYTE PTR DS:[EBX],0x0
     *  00441EE1   74 22            JE SHORT .00441F05
     *  00441EE3   8B86 00AE0000    MOV EAX,DWORD PTR DS:[ESI+0xAE00]
     *  00441EE9   85C0             TEST EAX,EAX
     *  00441EEB   75 18            JNZ SHORT .00441F05
     *  00441EED   8B86 AC040000    MOV EAX,DWORD PTR DS:[ESI+0x4AC]
     *  00441EF3   8D97 D1030000    LEA EDX,DWORD PTR DS:[EDI+0x3D1]
     *  00441EF9   8996 00AE0000    MOV DWORD PTR DS:[ESI+0xAE00],EDX
     *  00441EFF   8986 C0040000    MOV DWORD PTR DS:[ESI+0x4C0],EAX
     *  00441F05   8A86 30A60000    MOV AL,BYTE PTR DS:[ESI+0xA630]
     *  00441F0B   84C0             TEST AL,AL
     *  00441F0D   0F84 DB000000    JE .00441FEE
     *  00441F13   8B86 C0A00000    MOV EAX,DWORD PTR DS:[ESI+0xA0C0]
     *  00441F19   85C0             TEST EAX,EAX
     *  00441F1B   0F84 CD000000    JE .00441FEE
     *  00441F21   8B96 E0A00000    MOV EDX,DWORD PTR DS:[ESI+0xA0E0]
     *  00441F27   8DAE E0A00000    LEA EBP,DWORD PTR DS:[ESI+0xA0E0]
     *  00441F2D   6A 00            PUSH 0x0
     *  00441F2F   8BCD             MOV ECX,EBP
     *  00441F31   FF92 B4000000    CALL DWORD PTR DS:[EDX+0xB4]
     *  00441F37   8B86 489E0000    MOV EAX,DWORD PTR DS:[ESI+0x9E48]
     *  00441F3D   8D8E 5C470000    LEA ECX,DWORD PTR DS:[ESI+0x475C]
     *  00441F43   8D96 14680000    LEA EDX,DWORD PTR DS:[ESI+0x6814]
     *  00441F49   898E E4050000    MOV DWORD PTR DS:[ESI+0x5E4],ECX
     *  00441F4F   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
     *  00441F53   89AE 489E0000    MOV DWORD PTR DS:[ESI+0x9E48],EBP
     *  00441F59   C686 D8A00000 01 MOV BYTE PTR DS:[ESI+0xA0D8],0x1
     *  00441F60   8996 E8050000    MOV DWORD PTR DS:[ESI+0x5E8],EDX
     *  00441F66   8B87 B4030000    MOV EAX,DWORD PTR DS:[EDI+0x3B4]
     *  00441F6C   6A 01            PUSH 0x1
     *  00441F6E   8D4C24 20        LEA ECX,DWORD PTR SS:[ESP+0x20]
     *  00441F72   6A 01            PUSH 0x1
     *  00441F74   51               PUSH ECX
     *  00441F75   50               PUSH EAX
     *  00441F76   8BCD             MOV ECX,EBP
     *  00441F78   E8 935D0000      CALL .00447D10
     *  00441F7D   8B5424 18        MOV EDX,DWORD PTR SS:[ESP+0x18]
     *  00441F81   8D8E EC050000    LEA ECX,DWORD PTR DS:[ESI+0x5EC]
     *  00441F87   8996 489E0000    MOV DWORD PTR DS:[ESI+0x9E48],EDX
     *  00441F8D   8D96 A4260000    LEA EDX,DWORD PTR DS:[ESI+0x26A4]
     *  00441F93   85C0             TEST EAX,EAX
     *  00441F95   C686 D8A00000 00 MOV BYTE PTR DS:[ESI+0xA0D8],0x0
     *  00441F9C   898E E4050000    MOV DWORD PTR DS:[ESI+0x5E4],ECX
     *  00441FA2   8996 E8050000    MOV DWORD PTR DS:[ESI+0x5E8],EDX
     *  00441FA8   7E 44            JLE SHORT .00441FEE
     *  00441FAA   8A86 31A60000    MOV AL,BYTE PTR DS:[ESI+0xA631]
     *  00441FB0   84C0             TEST AL,AL
     *  00441FB2   74 0A            JE SHORT .00441FBE
     *  00441FB4   33C0             XOR EAX,EAX
     *  00441FB6   8A86 32A60000    MOV AL,BYTE PTR DS:[ESI+0xA632]
     *  00441FBC   EB 02            JMP SHORT .00441FC0
     *  00441FBE   33C0             XOR EAX,EAX
     *  00441FC0   8B4C24 28        MOV ECX,DWORD PTR SS:[ESP+0x28]
     *  00441FC4   8B6C24 20        MOV EBP,DWORD PTR SS:[ESP+0x20]
     *  00441FC8   8B97 B8030000    MOV EDX,DWORD PTR DS:[EDI+0x3B8]
     *  00441FCE   50               PUSH EAX
     *  00441FCF   8B4424 18        MOV EAX,DWORD PTR SS:[ESP+0x18]
     *  00441FD3   2BCD             SUB ECX,EBP
     *  00441FD5   53               PUSH EBX
     *  00441FD6   83C1 04          ADD ECX,0x4
     *  00441FD9   50               PUSH EAX
     *  00441FDA   8B87 B4030000    MOV EAX,DWORD PTR DS:[EDI+0x3B4]
     *  00441FE0   51               PUSH ECX
     *  00441FE1   52               PUSH EDX
     *  00441FE2   50               PUSH EAX
     *  00441FE3   8D8E B8A00000    LEA ECX,DWORD PTR DS:[ESI+0xA0B8]
     *  00441FE9   E8 72290000      CALL .00444960
     *  00441FEE   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
     *  00441FF2   8D86 48AE0000    LEA EAX,DWORD PTR DS:[ESI+0xAE48]
     *  00441FF8   5F               POP EDI
     *  00441FF9   8986 48BE0000    MOV DWORD PTR DS:[ESI+0xBE48],EAX
     *  00441FFF   5D               POP EBP
     *  00442000   C603 00          MOV BYTE PTR DS:[EBX],0x0
     *  00442003   5E               POP ESI
     *  00442004   C601 00          MOV BYTE PTR DS:[ECX],0x0
     *  00442007   33C0             XOR EAX,EAX
     *  00442009   5B               POP EBX
     *  0044200A   83C4 1C          ADD ESP,0x1C
     *  0044200D   C3               RETN
     *  0044200E   90               NOP
     *  0044200F   90               NOP
     *
     *  Sample game: 猫撫ディストーション
     *  name = ecx + 0xc60f
     *  scenario = ecx + 0xc684
     *  scenario end = ecx + 0xd684
     *
     *  0043E11E   90               NOP
     *  0043E11F   90               NOP
     *  0043E120   83EC 18          SUB ESP,0x18
     *  0043E123   53               PUSH EBX
     *  0043E124   55               PUSH EBP
     *  0043E125   56               PUSH ESI
     *  0043E126   8BF1             MOV ESI,ECX
     *  0043E128   57               PUSH EDI
     *  0043E129   8BAE 84D60000    MOV EBP,DWORD PTR DS:[ESI+0xD684]	; jichi: overall offset is around 0xD684
     *  0043E12F   2BEE             SUB EBP,ESI
     *  0043E131   81ED 84C60000    SUB EBP,0xC684
     *  0043E137   896C24 10        MOV DWORD PTR SS:[ESP+0x10],EBP
     *  0043E13B   75 0D            JNZ SHORT .0043E14A
     *  0043E13D   5F               POP EDI
     *  0043E13E   5E               POP ESI
     *  0043E13F   5D               POP EBP
     *  0043E140   B8 01000000      MOV EAX,0x1
     *  0043E145   5B               POP EBX
     *  0043E146   83C4 18          ADD ESP,0x18
     *  0043E149   C3               RETN
     *  0043E14A   8B86 A8040000    MOV EAX,DWORD PTR DS:[ESI+0x4A8]
     *  0043E150   8BCE             MOV ECX,ESI
     *  0043E152   50               PUSH EAX
     *  0043E153   E8 3875FFFF      CALL .00435690
     *  0043E158   8B9E F4B20000    MOV EBX,DWORD PTR DS:[ESI+0xB2F4]
     *  0043E15E   8BBE D8B10000    MOV EDI,DWORD PTR DS:[ESI+0xB1D8]
     *  0043E164   8B43 14          MOV EAX,DWORD PTR DS:[EBX+0x14]
     *  0043E167   85C0             TEST EAX,EAX
     *  0043E169   7D 7C            JGE SHORT .0043E1E7
     *  0043E16B   8B8E 70040000    MOV ECX,DWORD PTR DS:[ESI+0x470]
     *  0043E171   6A 00            PUSH 0x0
     *  0043E173   8D96 20C60000    LEA EDX,DWORD PTR DS:[ESI+0xC620]	; jichi: 0xc620 is the nearest position
     *  0043E179   6A 00            PUSH 0x0
     *  0043E17B   52               PUSH EDX
     *  0043E17C   6A FE            PUSH -0x2
     *  0043E17E   E8 ED93FEFF      CALL .00427570
     *  0043E183   8BE8             MOV EBP,EAX
     *  0043E185   85ED             TEST EBP,EBP
     *  0043E187   7C 0D            JL SHORT .0043E196
     *  0043E189   45               INC EBP
     *  0043E18A   83FD 08          CMP EBP,0x8
     *  0043E18D   7C 09            JL SHORT .0043E198
     *  0043E18F   BD 07000000      MOV EBP,0x7
     *  0043E194   EB 02            JMP SHORT .0043E198
     *  0043E196   33ED             XOR EBP,EBP
     *  0043E198   396B 1C          CMP DWORD PTR DS:[EBX+0x1C],EBP
     *  0043E19B   74 46            JE SHORT .0043E1E3
     *  0043E19D   8B8F 4C020000    MOV ECX,DWORD PTR DS:[EDI+0x24C]
     *  0043E1A3   85C9             TEST ECX,ECX
     *  0043E1A5   75 0D            JNZ SHORT .0043E1B4
     *  0043E1A7   5F               POP EDI
     *  0043E1A8   5E               POP ESI
     *  0043E1A9   5D               POP EBP
     *  0043E1AA   B8 02000000      MOV EAX,0x2
     *  0043E1AF   5B               POP EBX
     *  0043E1B0   83C4 18          ADD ESP,0x18
     *  0043E1B3   C3               RETN
     *  0043E1B4   8BC5             MOV EAX,EBP
     *  0043E1B6   6A 00            PUSH 0x0
     *  0043E1B8   C1E0 04          SHL EAX,0x4
     *  0043E1BB   03C5             ADD EAX,EBP
     *  0043E1BD   6A 00            PUSH 0x0
     *  0043E1BF   6A 00            PUSH 0x0
     *  0043E1C1   6A 00            PUSH 0x0
     *  0043E1C3   8D94C6 48BA0000  LEA EDX,DWORD PTR DS:[ESI+EAX*8+0xBA48]
     *  0043E1CA   52               PUSH EDX
     *  0043E1CB   E8 E0DD0200      CALL .0046BFB0
     *  0043E1D0   896B 1C          MOV DWORD PTR DS:[EBX+0x1C],EBP
     *  0043E1D3   8B07             MOV EAX,DWORD PTR DS:[EDI]
     *  0043E1D5   6A 01            PUSH 0x1
     *  0043E1D7   6A 01            PUSH 0x1
     *  0043E1D9   6A 01            PUSH 0x1
     *  0043E1DB   8BCF             MOV ECX,EDI
     *  0043E1DD   FF90 4C010000    CALL DWORD PTR DS:[EAX+0x14C]
     *  0043E1E3   8B6C24 10        MOV EBP,DWORD PTR SS:[ESP+0x10]
     *  0043E1E7   8BCE             MOV ECX,ESI
     *  0043E1E9   C743 20 00000000 MOV DWORD PTR DS:[EBX+0x20],0x0
     *
     *  0043E1F0   E8 3B46FFFF      CALL .00432830
     *  0043E1F5   8987 A0030000    MOV DWORD PTR DS:[EDI+0x3A0],EAX
     *  0043E1FB   8D86 84C60000    LEA EAX,DWORD PTR DS:[ESI+0xC684]	; jichi: this is scenario
     *  0043E201   55               PUSH EBP
     *  0043E202   50               PUSH EAX
     *  0043E203   8BCF             MOV ECX,EDI
     *  0043E205   E8 765F0000      CALL .00444180
     *  0043E20A   8D9E 20C60000    LEA EBX,DWORD PTR DS:[ESI+0xC620]	; jichi: this is the chara name, such as KOT0
     *  0043E210   8D86 0FC60000    LEA EAX,DWORD PTR DS:[ESI+0xC60F]	; jichi: this is the name address
     *  0043E216   53               PUSH EBX
     *  0043E217   50               PUSH EAX
     *  0043E218   8BCF             MOV ECX,EDI
     *  0043E21A   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
     *  0043E21E   E8 0D5F0000      CALL .00444130
     *
     *  0043E223   6A 01            PUSH 0x1
     *  0043E225   8BCF             MOV ECX,EDI
     *  0043E227   E8 04600000      CALL .00444230
     *  0043E22C   8A86 40BA0000    MOV AL,BYTE PTR DS:[ESI+0xBA40]
     *  0043E232   84C0             TEST AL,AL
     *  0043E234   0F84 DB000000    JE .0043E315
     *  0043E23A   8B86 18B50000    MOV EAX,DWORD PTR DS:[ESI+0xB518]
     *  0043E240   85C0             TEST EAX,EAX
     *  0043E242   0F84 CD000000    JE .0043E315
     *  0043E248   8B96 38B50000    MOV EDX,DWORD PTR DS:[ESI+0xB538]
     *  0043E24E   8DAE 38B50000    LEA EBP,DWORD PTR DS:[ESI+0xB538]
     *  0043E254   6A 00            PUSH 0x0
     *  0043E256   8BCD             MOV ECX,EBP
     *  0043E258   FF92 B4000000    CALL DWORD PTR DS:[EDX+0xB4]
     *  0043E25E   8B86 D8B10000    MOV EAX,DWORD PTR DS:[ESI+0xB1D8]
     *  0043E264   8D8E 70460000    LEA ECX,DWORD PTR DS:[ESI+0x4670]
     *  0043E26A   8D96 28670000    LEA EDX,DWORD PTR DS:[ESI+0x6728]
     *  0043E270   898E F8040000    MOV DWORD PTR DS:[ESI+0x4F8],ECX
     *  0043E276   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
     *  0043E27A   89AE D8B10000    MOV DWORD PTR DS:[ESI+0xB1D8],EBP
     *  0043E280   C686 30B50000 01 MOV BYTE PTR DS:[ESI+0xB530],0x1
     *  0043E287   8996 FC040000    MOV DWORD PTR DS:[ESI+0x4FC],EDX
     *  0043E28D   8B87 AC030000    MOV EAX,DWORD PTR DS:[EDI+0x3AC]
     *  0043E293   6A 01            PUSH 0x1
     *  0043E295   8D4C24 1C        LEA ECX,DWORD PTR SS:[ESP+0x1C]
     *  0043E299   6A 01            PUSH 0x1
     *  0043E29B   51               PUSH ECX
     *  0043E29C   50               PUSH EAX
     *  0043E29D   8BCD             MOV ECX,EBP
     *  0043E29F   E8 DC570000      CALL .00443A80
     *  0043E2A4   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
     *  0043E2A8   8D8E 00050000    LEA ECX,DWORD PTR DS:[ESI+0x500]
     *  0043E2AE   8996 D8B10000    MOV DWORD PTR DS:[ESI+0xB1D8],EDX
     *  0043E2B4   8D96 B8250000    LEA EDX,DWORD PTR DS:[ESI+0x25B8]
     *  0043E2BA   85C0             TEST EAX,EAX
     *  0043E2BC   C686 30B50000 00 MOV BYTE PTR DS:[ESI+0xB530],0x0
     *  0043E2C3   898E F8040000    MOV DWORD PTR DS:[ESI+0x4F8],ECX
     *  0043E2C9   8996 FC040000    MOV DWORD PTR DS:[ESI+0x4FC],EDX
     *  0043E2CF   7E 44            JLE SHORT .0043E315
     *  0043E2D1   8A86 41BA0000    MOV AL,BYTE PTR DS:[ESI+0xBA41]
     *  0043E2D7   84C0             TEST AL,AL
     *  0043E2D9   74 0A            JE SHORT .0043E2E5
     *  0043E2DB   33C0             XOR EAX,EAX
     *  0043E2DD   8A86 42BA0000    MOV AL,BYTE PTR DS:[ESI+0xBA42]
     *  0043E2E3   EB 02            JMP SHORT .0043E2E7
     *  0043E2E5   33C0             XOR EAX,EAX
     *  0043E2E7   8B4C24 24        MOV ECX,DWORD PTR SS:[ESP+0x24]
     *  0043E2EB   8B6C24 1C        MOV EBP,DWORD PTR SS:[ESP+0x1C]
     *  0043E2EF   8B97 B0030000    MOV EDX,DWORD PTR DS:[EDI+0x3B0]
     *  0043E2F5   50               PUSH EAX
     *  0043E2F6   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
     *  0043E2FA   2BCD             SUB ECX,EBP
     *  0043E2FC   53               PUSH EBX
     *  0043E2FD   83C1 04          ADD ECX,0x4
     *  0043E300   50               PUSH EAX
     *  0043E301   8B87 AC030000    MOV EAX,DWORD PTR DS:[EDI+0x3AC]
     *  0043E307   51               PUSH ECX
     *  0043E308   52               PUSH EDX
     *  0043E309   50               PUSH EAX
     *  0043E30A   8D8E 10B50000    LEA ECX,DWORD PTR DS:[ESI+0xB510]
     *  0043E310   E8 7B270000      CALL .00440A90
     *  0043E315   803B 00          CMP BYTE PTR DS:[EBX],0x0
     *  0043E318   74 0C            JE SHORT .0043E326
     *  0043E31A   81C7 C9030000    ADD EDI,0x3C9
     *  0043E320   89BE 3CC60000    MOV DWORD PTR DS:[ESI+0xC63C],EDI
     *  0043E326   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
     *  0043E32A   8D86 84C60000    LEA EAX,DWORD PTR DS:[ESI+0xC684]
     *  0043E330   8986 84D60000    MOV DWORD PTR DS:[ESI+0xD684],EAX
     *  0043E336   5F               POP EDI
     *  0043E337   5E               POP ESI
     *  0043E338   C603 00          MOV BYTE PTR DS:[EBX],0x0
     *  0043E33B   5D               POP EBP
     *  0043E33C   C601 00          MOV BYTE PTR DS:[ECX],0x0
     *  0043E33F   33C0             XOR EAX,EAX
     *  0043E341   5B               POP EBX
     *  0043E342   83C4 18          ADD ESP,0x18
     *  0043E345   C3               RETN
     *  0043E346   90               NOP
     *  0043E347   90               NOP
     *  0043E348   90               NOP
     *  0043E349   90               NOP
     *  0043E34A   90               NOP
     *  0043E34B   90               NOP
     */
    bool attach(ULONG startAddress, ULONG stopAddress) // attach scenario
    {
      const uint8_t bytes[] = {
          0xe8, XX4,            // 0043e1f0   e8 3b46ffff      call .00432830
          0x89, 0x87, XX4,      // 0043e1f5   8987 a0030000    mov dword ptr ds:[edi+0x3a0],eax
          0x8d, 0x86, XX4,      // 0043e1fb   8d86 84c60000    lea eax,dword ptr ds:[esi+0xc684]	; jichi: this is scenario
                                // 0043e201   55               push ebp
                                // 0043e202   50               push eax
          XX4,                  // 0043e203   8bcf             mov ecx,edi
          0xe8, XX4,            // 0043e205   e8 765f0000      call .00444180
          0x8d, 0x9e, XX4,      // 0043e20a   8d9e 20c60000    lea ebx,dword ptr ds:[esi+0xc620]	; jichi: this is the chara name, such as kot0
          0x8d, 0x86, XX4,      // 0043e210   8d86 0fc60000    lea eax,dword ptr ds:[esi+0xc60f]	; jichi: this is the name address
          0x53,                 // 0043e216   53               push ebx
          0x50,                 // 0043e217   50               push eax
          0x8b, 0xcf,           // 0043e218   8bcf             mov ecx,edi
          0x89, 0x44, 0x24, XX, // 0043e21a   894424 18        mov dword ptr ss:[esp+0x18],eax
          0xe8                  //, XX4            // 0043e21e   e8 0d5f0000      call .00444130
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;

      Private::scenarioOffset_ = *(DWORD *)(addr + 2 + 0x0043e1fb - 0x0043e1f0);
      Private::nameOffset_ = *(DWORD *)(addr + 2 + 0x0043e210 - 0x0043e1f0);
      if ((Private::scenarioOffset_ >> 16) || // offset high bits are zero
          (Private::nameOffset_ >> 16))
        return false;

      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.embed_hook_font = F_GetGlyphOutlineA | F_GetTextExtentPoint32A;
      return NewHook(hp, "EmbedLucifen");
    }
  } // namespace ScenarioHook

  namespace ChoiceHook
  {
    namespace Private
    {

      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        static std::string data_;
        auto text = (LPCSTR)s->stack[0]; // arg1 is text
        if (!text || !*text)
          return;
        *split = Engine::ChoiceRole;
        buffer->from(text);
      }
      void hookafter(hook_context *s, TextBuffer buffer)
      {
        auto newData = buffer.strA();
        strcpy((char *)s->stack[0], newData.c_str());
      }

    } // namespace Private

    /**
     *  Debugging method:
     *  - Hijack GetGlyphOutlineA
     *  - Backtrack stack to find text that used as argument
     *
     *  Sample game: プリズム・プリンセス
     *
     *  Text in arg1.
     *
     *  The function is only called by one caller.
     *  I suspect it is a virtual function, and hence caller is hooked.
     *
     *  0044235E   90               NOP
     *  0044235F   90               NOP
     *  00442360   83EC 08          SUB ESP,0x8
     *  00442363   53               PUSH EBX
     *  00442364   56               PUSH ESI
     *  00442365   8BF1             MOV ESI,ECX
     *  00442367   BB 01000000      MOV EBX,0x1
     *  0044236C   8A86 E2050000    MOV AL,BYTE PTR DS:[ESI+0x5E2]
     *  00442372   84C0             TEST AL,AL
     *  00442374   75 14            JNZ SHORT .0044238A
     *  00442376   889E BD040000    MOV BYTE PTR DS:[ESI+0x4BD],BL
     *  0044237C   E8 BFFAFFFF      CALL .00441E40
     *  00442381   85C0             TEST EAX,EAX
     *  00442383   0F94C0           SETE AL
     *  00442386   84C0             TEST AL,AL
     *  00442388   74 16            JE SHORT .004423A0
     *  0044238A   53               PUSH EBX
     *  0044238B   6A 00            PUSH 0x0
     *  0044238D   8BCE             MOV ECX,ESI
     *  0044238F   E8 2C80FFFF      CALL .0043A3C0
     *  00442394   85C0             TEST EAX,EAX
     *  00442396   74 16            JE SHORT .004423AE
     *  00442398   5E               POP ESI
     *  00442399   5B               POP EBX
     *  0044239A   83C4 08          ADD ESP,0x8
     *  0044239D   C2 0400          RETN 0x4
     *  004423A0   8B86 88040000    MOV EAX,DWORD PTR DS:[ESI+0x488]
     *  004423A6   8BCE             MOV ECX,ESI
     *  004423A8   50               PUSH EAX
     *  004423A9   E8 32120700      CALL .004B35E0
     *  004423AE   8B96 949E0000    MOV EDX,DWORD PTR DS:[ESI+0x9E94]
     *  004423B4   55               PUSH EBP
     *  004423B5   8DAE 949E0000    LEA EBP,DWORD PTR DS:[ESI+0x9E94]
     *  004423BB   57               PUSH EDI
     *  004423BC   8BCD             MOV ECX,EBP
     *  004423BE   C686 BD040000 00 MOV BYTE PTR DS:[ESI+0x4BD],0x0
     *  004423C5   FF92 80000000    CALL DWORD PTR DS:[EDX+0x80]
     *  004423CB   8B86 44040000    MOV EAX,DWORD PTR DS:[ESI+0x444]
     *  004423D1   85C0             TEST EAX,EAX
     *  004423D3   74 05            JE SHORT .004423DA
     *  004423D5   83C0 18          ADD EAX,0x18
     *  004423D8   EB 02            JMP SHORT .004423DC
     *  004423DA   33C0             XOR EAX,EAX
     *  004423DC   8B8E A0A00000    MOV ECX,DWORD PTR DS:[ESI+0xA0A0]
     *  004423E2   8B7C24 1C        MOV EDI,DWORD PTR SS:[ESP+0x1C]
     *  004423E6   8B55 00          MOV EDX,DWORD PTR SS:[EBP]
     *  004423E9   51               PUSH ECX
     *  004423EA   8B4F 4C          MOV ECX,DWORD PTR DS:[EDI+0x4C]
     *  004423ED   51               PUSH ECX
     *  004423EE   50               PUSH EAX
     *  004423EF   8BCD             MOV ECX,EBP
     *  004423F1   FF92 AC000000    CALL DWORD PTR DS:[EDX+0xAC]
     *  004423F7   B8 02000000      MOV EAX,0x2
     *  004423FC   8D4F 08          LEA ECX,DWORD PTR DS:[EDI+0x8]
     *  004423FF   8339 00          CMP DWORD PTR DS:[ECX],0x0
     *  00442402   74 0B            JE SHORT .0044240F
     *  00442404   83C0 02          ADD EAX,0x2
     *  00442407   83C1 08          ADD ECX,0x8
     *  0044240A   83F8 12          CMP EAX,0x12
     *  0044240D  ^7C F0            JL SHORT .004423FF
     *  0044240F   D1F8             SAR EAX,1
     *  00442411   48               DEC EAX
     *  00442412   8BF8             MOV EDI,EAX
     *  00442414   8A86 30A60000    MOV AL,BYTE PTR DS:[ESI+0xA630]
     *  0044241A   84C0             TEST AL,AL
     *  0044241C   897C24 14        MOV DWORD PTR SS:[ESP+0x14],EDI
     *  00442420   89BE 9CA00000    MOV DWORD PTR DS:[ESI+0xA09C],EDI
     *  00442426   0F84 B9000000    JE .004424E5
     *  0044242C   8B86 C0A00000    MOV EAX,DWORD PTR DS:[ESI+0xA0C0]
     *  00442432   85C0             TEST EAX,EAX
     *  00442434   0F84 AB000000    JE .004424E5
     *  0044243A   57               PUSH EDI
     *  0044243B   8D8E B8A00000    LEA ECX,DWORD PTR DS:[ESI+0xA0B8]
     *  00442441   885C24 17        MOV BYTE PTR SS:[ESP+0x17],BL
     *  00442445   E8 46270000      CALL .00444B90
     *  0044244A   33DB             XOR EBX,EBX
     *  0044244C   85FF             TEST EDI,EDI
     *  0044244E   7E 64            JLE SHORT .004424B4
     *  00442450   8B5424 1C        MOV EDX,DWORD PTR SS:[ESP+0x1C]
     *  00442454   8D7A 0C          LEA EDI,DWORD PTR DS:[EDX+0xC]
     *  00442457   8A941E B8040000  MOV DL,BYTE PTR DS:[ESI+EBX+0x4B8]
     *  0044245E   8B45 00          MOV EAX,DWORD PTR SS:[EBP]
     *  00442461   6A 00            PUSH 0x0
     *  00442463   6A 00            PUSH 0x0
     *  00442465   84D2             TEST DL,DL
     *  00442467   8B17             MOV EDX,DWORD PTR DS:[EDI]
     *  00442469   6A 00            PUSH 0x0
     *  0044246B   0F954424 28      SETNE BYTE PTR SS:[ESP+0x28]
     *  00442470   8B4C24 28        MOV ECX,DWORD PTR SS:[ESP+0x28]
     *  00442474   6A 00            PUSH 0x0
     *  00442476   6A FF            PUSH -0x1
     *  00442478   6A 00            PUSH 0x0
     *  0044247A   6A FF            PUSH -0x1
     *  0044247C   51               PUSH ECX
     *  0044247D   6A 00            PUSH 0x0
     *  0044247F   52               PUSH EDX
     *  00442480   8BCD             MOV ECX,EBP
     *  00442482   FF90 84000000    CALL DWORD PTR DS:[EAX+0x84]             ; .004BBD00	; jichi: text called here, text on the top
     *  00442488   8A4424 13        MOV AL,BYTE PTR SS:[ESP+0x13]
     *  0044248C   84C0             TEST AL,AL
     *  0044248E   74 18            JE SHORT .004424A8
     *  00442490   8A5424 1C        MOV DL,BYTE PTR SS:[ESP+0x1C]
     *  00442494   8B0F             MOV ECX,DWORD PTR DS:[EDI]
     *  00442496   84D2             TEST DL,DL
     *  00442498   0F94C0           SETE AL
     *  0044249B   50               PUSH EAX
     *  0044249C   51               PUSH ECX
     *  0044249D   8D8E B8A00000    LEA ECX,DWORD PTR DS:[ESI+0xA0B8]
     *  004424A3   E8 48280000      CALL .00444CF0
     *  004424A8   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
     *  004424AC   83C7 08          ADD EDI,0x8
     *  004424AF   43               INC EBX
     *  004424B0   3BD8             CMP EBX,EAX
     *  004424B2  ^7C A3            JL SHORT .00442457
     *  004424B4   8A4424 13        MOV AL,BYTE PTR SS:[ESP+0x13]
     *  004424B8   5F               POP EDI
     *  004424B9   84C0             TEST AL,AL
     *  004424BB   5D               POP EBP
     *  004424BC   74 12            JE SHORT .004424D0
     *  004424BE   8D96 34A60000    LEA EDX,DWORD PTR DS:[ESI+0xA634]
     *  004424C4   8D8E B8A00000    LEA ECX,DWORD PTR DS:[ESI+0xA0B8]
     *  004424CA   52               PUSH EDX
     *  004424CB   E8 B0280000      CALL .00444D80
     *  004424D0   33C0             XOR EAX,EAX
     *  004424D2   81C6 B8040000    ADD ESI,0x4B8
     *  004424D8   8906             MOV DWORD PTR DS:[ESI],EAX
     *  004424DA   8846 04          MOV BYTE PTR DS:[ESI+0x4],AL
     *  004424DD   5E               POP ESI
     *  004424DE   5B               POP EBX
     *  004424DF   83C4 08          ADD ESP,0x8
     *  004424E2   C2 0400          RETN 0x4
     *  004424E5   C64424 13 00     MOV BYTE PTR SS:[ESP+0x13],0x0
     *  004424EA  ^E9 5BFFFFFF      JMP .0044244A
     *  004424EF   90               NOP
     *  004424F0   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
     *  004424F4   8B40 04          MOV EAX,DWORD PTR DS:[EAX+0x4]
     *  004424F7   85C0             TEST EAX,EAX
     *  004424F9   7C 0D            JL SHORT .00442508
     *  004424FB   83F8 05          CMP EAX,0x5
     *  004424FE   7D 08            JGE SHORT .00442508
     *  00442500   C68408 B8040000 >MOV BYTE PTR DS:[EAX+ECX+0x4B8],0x1
     *  00442508   33C0             XOR EAX,EAX
     *  0044250A   C2 0400          RETN 0x4
     *  0044250D   90               NOP
     *  0044250E   90               NOP
     */
    bool attach(ULONG startAddress, ULONG stopAddress) // attach scenario
    {
      const uint8_t bytes[] = {
          0xff, 0x90, 0x84, 0x00, 0x00, 0x00, // 00442482   ff90 84000000    call dword ptr ds:[eax+0x84]             ; .004bbd00	; jichi: text called here, text on the top
          0x8a, 0x44, 0x24, 0x13              // 00442488   8a4424 13        mov al,byte ptr ss:[esp+0x13]
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.embed_hook_font = F_GetGlyphOutlineA | F_GetTextExtentPoint32A;
      return NewHook(hp, "lucifen_choice");
    }
  } // namespace ChoiceHook

  size_t countZero(const char *s, size_t limit = 1500)
  {
    size_t count = 0;
    for (auto p = s; !*p && count < limit; p++, count++)
      ;
    return count == limit ? 0 : count;
  }
  void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto text = (LPSTR)s->stack[1]; // arg1 is text
    if (!text || ::strlen(text) <= 2)
      return;
    *split = Engine::OtherRole;
    buffer->from(text);
  }
  void hookafter(hook_context *s, TextBuffer buffer)
  {
    auto text = (LPSTR)s->stack[1]; // arg1 is text

    enum
    {
      role = Engine::OtherRole
    };
    std::string oldData = text;
    auto split = s->stack[0];
    auto newData = buffer.strA();
    size_t capacity = countZero(text + oldData.size());
    if (!capacity)
      return;
    capacity += oldData.size() - 1;
    if (newData.size() > capacity)
      newData = newData.substr(0, capacity);
    if (newData.size() < oldData.size())
      ::memset(text + newData.size(), 0, oldData.size() - newData.size());
    ::strcpy(text, newData.c_str());
    return;
  }
  bool attach11(ULONG startAddress, ULONG stopAddress) // attach scenario
  {
    // 这个的对话都是一个个字的，但是名字是连续的。
    const uint8_t bytes[] = {
        0x83, 0xec, 0x14,                   // 00461ca0   83ec 14          sub esp,0x14
        0x33, 0xd2,                         // 00461ca3   33d2             xor edx,edx
        0x55,                               // 00461ca5   55               push ebp
        0x56,                               // 00461ca6   56               push esi
        0x8b, 0x74, 0x24, 0x20,             // 00461ca7   8b7424 20        mov esi,dword ptr ss:[esp+0x20]
        0x8b, 0xe9,                         // 00461cab   8be9             mov ebp,ecx
        0x3b, 0xf2,                         // 00461cad   3bf2             cmp esi,edx
        0x0f, 0x84, 0x55, 0x02, 0x00, 0x00, // 00461caf   0f84 55020000    je .00461f0a
        0x39, 0x55, 0x08,                   // 00461cb5   3955 08          cmp dword ptr ss:[ebp+0x8],edx
        0x0f, 0x84, 0x4c, 0x02, 0x00, 0x00, // 00461cb8   0f84 4c020000    je .00461f0a
        0x8b, 0x85, 0x74, 0x20, 0x00, 0x00  // 00461cbe   8b85 74200000    mov eax,dword ptr ss:[ebp+0x2074]
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
    hp.embed_fun = hookafter;
    hp.text_fun = hookBefore;
    hp.embed_hook_font = F_GetGlyphOutlineA | F_GetTextExtentPoint32A;
    return NewHook(hp, "Embedlucifen2");
  }
}
bool Lucifen::attach_function()
{
  bool b1 = ScenarioHook::attach(processStartAddress, processStopAddress) || attach_navel(processStartAddress, processStopAddress);
  if (b1)
  {
    ChoiceHook::attach(processStartAddress, processStopAddress);
    attach11(processStartAddress, processStopAddress);
  }

  bool succ = InsertLucifenHook();
  succ |= hook();
  return succ;
}