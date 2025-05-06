#include "ShinaRio.h"

/********************************************************************************************
ShinaRio hook:
  Game folder contains rio.ini.
  Problem of default hook GetTextExtentPoint32A is that the text repeat one time.
  But KF just can't resolve the issue. ShinaRio engine always perform integrity check.
  So it's very difficult to insert a hook into the game module. Freaka suggests to refine
  the default hook by adding split parameter on the stack. So far there is 2 different
  version of ShinaRio engine that needs different split parameter. Seems this value is
  fixed to the last stack frame. We just navigate to the entry. There should be a
  sub esp,* instruction. This value plus 4 is just the offset we need.

  New ShinaRio engine (>=2.48) uses different approach.
********************************************************************************************/
namespace
{
  // jichi 3/1/2015: hook for old ShinaRio games
  // Used to merge correct text thread.
  // 1. Only keep threads with 0 and -1 split
  // 2. Skip the thread withb 0 split and with minimum return address
  // void SpecialHookShina1(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
  //{
  //  static DWORD min_retaddr = -1;
  //  DWORD s = *(DWORD *)(esp_base + hp->split);
  //  if (s == 0 || (s & 0xffff) == 0xffff) { // only keep threads with 0 and -1 split
  //    if (s == 0 && retof(esp_base) <= min_retaddr) {
  //      min_retaddr = retof(esp_base);
  //      return;
  //    }
  //    *split = FIXED_SPLIT_VALUE;
  //    // Follow the same logic as the hook.
  //    *data = *(DWORD *)*data; // DATA_INDIRECT
  //    *len = LeadByteTable[*data & 0xff];
  //  }
  //}

  // jichi 8/27/2013
  // Return ShinaRio version number
  // The head of Rio.ini usually looks like:
  //     [椎名里�v2.49]
  // This function will return 49 in the above case.
  //
  // Games from アトリエさく�do not have Rio.ini, but $procname.ini.
  int GetShinaRioVersion()
  {
    int ret = 0;
    HANDLE hFile = CreateFileW(L"RIO.INI", FILE_READ_DATA, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hFile == INVALID_HANDLE_VALUE)
    {
      size_t len = ::wcslen(processName);
      if (len > 3)
      {
        wchar_t fname[MAX_PATH];
        ::wcscpy(fname, processName);
        fname[len - 1] = 'i';
        fname[len - 2] = 'n';
        fname[len - 3] = 'i';
        hFile = CreateFileW(fname, FILE_READ_DATA, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
      }
    }

    if (hFile != INVALID_HANDLE_VALUE)
    {
      // char *buffer,*version;//,*ptr;
      enum
      {
        BufferSize = 0x40
      };
      char buffer[BufferSize]{};
      DWORD DUMMY;
      ReadFile(hFile, buffer, BufferSize, &DUMMY, nullptr);
      CloseHandle(hFile);
      // if (buffer[0] == '[') {
      buffer[0x3f] = 0; // jichi 8/24/2013: prevent strstr from overflow
      if (char *version = ::strstr(buffer, "v2."))
        ::sscanf(version + 3, "%d", &ret); // +3 to skip "v2."
      //}
    }
    return ret;
  }

  bool IsSJIS(char *text)
  {
    for (int i = 0; i < 3; ++i)
      if (!IsShiftjisWord(((WORD *)text)[i]))
        return false;
    return true;
  }

} // unnamed namespace

// jichi 8/24/2013: Rewrite ShinaRio logic.
// Test games: ���×Ｓ��　(PK), version ShinaRio 2.47
bool InsertShinaHook(int ver)
{

  if (ver >= 50)
  {
    PcHooks::hookGDIFunctions(GetGlyphOutlineA);
    PcHooks::hookGDIFunctions(GetTextExtentPoint32A);
    trigger_fun = [](LPVOID funcAddr, hook_context *context)
    {
      bool ret = false;
      if (funcAddr != GetGlyphOutlineA && funcAddr != GetTextExtentPoint32A)
        return false;
      for (int i = 0; i < 100; ++i)
      {
        // Address of text is somewhere on stack in call to func. Search for it.
        DWORD addr = *((DWORD *)context->esp + i);
        // ConsoleOutput(std::to_string((DWORD)*addr).c_str());
        if (IthGetMemoryRange((void *)addr, nullptr, nullptr) && strlen((char *)addr) > 9)
        {
          if (IsSJIS((char *)addr) || strstr((char *)addr, "_r"))
          {
            HookParam hp;
            hp.type = DIRECT_READ;
            hp.address = addr;
            hp.codepage = 932;
            hp.filter_fun = [](TextBuffer *buffer, HookParam *)
            {
              StringFilter(buffer, TEXTANDLEN("_r"));
              buffer->from(re::sub(buffer->strA(), "_t!.*?[/>]"));
            };
            ConsoleOutput("triggered: adding dynamic reader");
            ret |= NewHook(hp, "ShinaRio READ");
          }
        };
      }
      return ret;
    };
    ConsoleOutput("ShinaRio 2.50+: adding trigger");
  }
  // 被embedshinario取代
  /*
  if (ver >= 48) { // v2.48, v2.49
    HookParam hp;
    hp.address = (DWORD)::GetTextExtentPoint32A;
    hp.text_fun = SpecialHookShina2;
    hp.type = USING_STRING;
    ConsoleOutput("INSERT ShinaRio > 2.47");
    NewHook(hp, "ShinaRio");
    //RegisterEngineType(ENGINE_SHINA);
    return true;

  } else if (ver > 40) { // <= v2.47. Older games like あやかしびと does not require hcode
    // jichi 3/13/2015: GetGlyphOutlineA is not hooked, which might produce correct text
    // BOOL GetTextExtentPoint32(HDC hdc, LPCTSTR lpString, int c, LPSIZE lpSize);
    enum stack { // current stack
      arg0_retaddr = 0 // pseudo arg
      , arg1_hdc = 4 * 1
      , arg2_lpString = 4 * 2
      , arg3_c = 4 * 3
      , arg4_lpSize = 4 * 4
    };

    HookParam hp;
    hp.address = (DWORD)::GetTextExtentPoint32A;
    hp.offset = arg2_lpString; // 0x8
    hp.length_offset = 1;
    hp.type = DATA_INDIRECT|USING_SPLIT;

    enum { sub_esp = 0xec81 }; // jichi: caller pattern: sub esp = 0x81,0xec
    if (DWORD s = Util::FindCallAndEntryBoth((DWORD)GetTextExtentPoint32A, processStopAddress - processStartAddress, processStartAddress, sub_esp)) {
      ConsoleOutput("INSERT ShinaRio <= 2.47 dynamic split");
      hp.split = *(DWORD *)(s + 2) + 4;
       //RegisterEngineType(ENGINE_SHINA);
      NewHook(hp, "ShinaRio");

    } else {
      // jichi 3/13/2015: GetTextExtentPoint32A is not statically invoked in ���×Ｓ��　(PK)
      // See: http://sakuradite.com/topic/671
      // See: http://www.hongfire.com/forum/showthread.php/36807-AGTH-text-extraction-tool-for-games-translation/page347
      //
      // [Guilty+]Rin x Sen �Hakudaku Onna Kyoushi to Yaroudomo /HB8*0:44@0:GDI32.dll:GetTextExtentPoint32A /Ftext@4339A2:0;choices@4339A2:ffffff
      //
      // addr: 0 , text_fun: 0x0 , function: 135408591 , hook_len: 0 , ind: 0 , length_of
      // fset: 1 , module: 1409538707 , off: 8 , recover_len: 0 , split: 68 , split_ind:
      // 0 , type: 216
      //
      // Message speed needs to be set to something slower then fastest(instant) or text wont show up in agth.
      // Last edited by Freaka; 09-29-2009 at 11:48 AM.

      // Issues:
      // 1. The text speed must NOT to be set to the fastest.
      // 2. There might be a wrong text thread that is almost correct, except that its first character is chopped.
      // Otherwise, the first character will be split in another thread
      ConsoleOutput("INSERT ShinaRio <= 2.47 static split");
      hp.split = 0x44;
      //hp.type |= FIXING_SPLIT|NO_CONTEXT; // merge all threads
      //hp.text_fun = SpecialHookShina1;
      NewHook(hp, "ShinaRio2"); // jichi: mark as ShinaRio2 so that VNR is able to warn user about the text speed issue
    }
    return true;
  }
  ConsoleOutput("ShinaRio: unknown version");

  */
  return false;
}

namespace
{ // unnamed

  namespace ScenarioHook
  {
    namespace Private
    {

      bool isSkippedText(LPCSTR text)
      {
        return 0 == ::strcmp(text, "\x82\x6c\x82\x72\x20\x83\x53\x83\x56\x83\x62\x83\x4e"); // "ＭＳ ゴシック"
      }

      class HookArgument
      {
        DWORD split_;
        //      offset_[0x57];    // [esi]+0x160
        // LPSTR text_;            // current text address

        template <typename strT>
        static strT nextText(strT t)
        {
          t += ::strlen(t);
          return (t[6] && !t[5] && !t[4] && !t[3] && !t[2] && !t[1]) ? t + 6 : nullptr; // 6 continuous zeros
        }

        // Engine::TextRole textRole() const
        //{
        //   static ULONG minSplit_ = UINT_MAX;
        //   minSplit_ = qMin(minSplit_, split_);
        //   return split_ == minSplit_ ? Engine::ScenarioRole :
        //          split_ == minSplit_ + 1 ? Engine::NameRole :
        //          Engine::OtherRole;
        // }

      public:
        static bool isTextList(LPCSTR text) { return nextText(text); }

        // LPSTR textAddress() const { return text_; }

        /**
         *  @param  text
         *  @param  paddingSpace  prepend space to make the first character having two bytes
         */
        void dispatchText(LPSTR text, bool paddingSpace, TextBuffer *b, uintptr_t *role)
        {
          enum
          {
            NameCapacity = 0x20
          }; // including ending '\0'
          static std::string data_;

          if (0 == ::strcmp(text, data_.c_str()))
            return;
          if (isSkippedText(text))
            return;

          // LPSIZE lpSize = (LPSIZE)s->stack[4]; // arg4 of GetTextExtentPoint32A
          // int area = lpSize->cx * lpSize->cy;
          // auto role = lpSize->cx || !lpSize->cy || area > 150 ? Engine::ScenarioRole : Engine::NameRole;
          // auto role = textRole();
          //  * role = Engine::ScenarioRole;
          //  if (::strlen(text) < NameCapacity
          //      && text[NameCapacity - 1] == 0 && text[NameCapacity])
          //    *role = Engine::NameRole;
          b->from(text);
        }
        void dispatchText2(LPSTR text, bool paddingSpace, std::string newData)
        {
          enum
          {
            NameCapacity = 0x20
          }; // including ending '\0'
          static std::string data_;

          if (0 == ::strcmp(text, data_.c_str()))
            return;
          if (isSkippedText(text))
            return;

          // LPSIZE lpSize = (LPSIZE)s->stack[4]; // arg4 of GetTextExtentPoint32A
          // int area = lpSize->cx * lpSize->cy;
          // auto role = lpSize->cx || !lpSize->cy || area > 150 ? Engine::ScenarioRole : Engine::NameRole;
          // auto role = textRole();
          auto role = Engine::ScenarioRole;
          if (::strlen(text) < NameCapacity && text[NameCapacity - 1] == 0 && text[NameCapacity])
            role = Engine::NameRole;

          std::string oldData = text;
          //    auto newData=oldData+"XX";
          if (newData == oldData)
            return;
          if (paddingSpace && !newData.empty() && (signed char)newData[0] > 0) // prepend space for thin char
            newData.insert(0, "  ");
          // .prepend(' ');
          data_ = newData;

          if (role == Engine::NameRole && newData.size() >= NameCapacity)
          {
            data_ = newData.substr(0, NameCapacity - 1);
            ::strncpy(text, newData.c_str(), NameCapacity);
            text[NameCapacity] = 0;
          }
          else
          {
            ::strcpy(text, newData.c_str());
            if (oldData.size() > newData.size())
              ::memset(text + newData.size(), 0, oldData.size() - newData.size());
          }
        }

        void dispatchTextList2(LPSTR text, bool paddingSpace, std::string newData1)
        {

          enum
          {
            role = Engine::OtherRole
          };
          std::vector<LPSTR> save;
          auto newdata = strSplit(newData1, "|");

          for (auto p = text; p; p = nextText(p))
          {
            save.push_back(p);
          }
          if (save.size() != newdata.size())
            return;
          int i = 0;
          for (auto p = text; p; p = nextText(p))
          {
            std::string oldData = p;
            auto newData = newdata[i];
            i++;
            if (newData != oldData)
            {
              if (newData.size() > oldData.size())
                newData = newData.substr(0, oldData.size());
              else
                while (newData.size() < oldData.size())
                  newData.push_back(' ');
              ::memcpy(p, newData.c_str(), oldData.size());
            }
          }
        }
        void dispatchTextList(LPSTR text, bool paddingSpace, TextBuffer *buffer, uintptr_t *role)
        {
          static std::unordered_set<UINT64> hashes_;
          // enum { role = Engine::OtherRole };
          std::string save;
          for (auto p = text; p; p = nextText(p))
          {
            std::string oldData = p;
            save += ("|" + oldData);
          }
          buffer->from(save);
        }

        // void dispatch(LPSTR text)
        //{
        //   if (nextText(text))
        //     dispatchTextList(text);
        //   else
        //     dispatchText(text);
        // }
      };

      /**
       *
       *  BOOL GetTextExtentPoint32(HDC hdc, LPCTSTR lpString, int c, LPSIZE lpSize);
       *
       *  Scenario:
       *  0012F4EC   0043784C  /CALL to GetTextExtentPoint32A from .00437846
       *  0012F4F0   9A010C64  |hDC = 9A010C64
       *  0012F4F4   004C0F30  |Text = "Y"
       *  0012F4F8   00000001  |TextLen = 0x1
       *  0012F4FC   00504DA4  \pSize = .00504DA4
       *  0012F500   00503778  .00503778
       *  0012F504   00439EBE  RETURN to .00439EBE from .00437790
       *  0012F508   00503778  .00503778
       *  0012F50C   00914CC0  .00914CC0
       *  0012F510   00000001
       *  0012F514   00503778  .00503778
       *  0012F518   0069EB80  .0069EB80
       *  0012F51C   00000000
       *  0012F520   00914CC0  .00914CC0
       *  0012F524   0600A0AE
       *  0012F528   0012F53C  ASCII "ps"
       *  0012F52C   76DD23CB  user32.ClientToScreen
       *  0012F530   75D0BA46  kernel32.Sleep
       *
       *  pSize:
       *  00504DA4  0C 00 00 00 18 00 00 00 18 00 00 00 15 00 00 00  .............
       *  00504DB4  03 00 00 00 00 00 00 00 00 00 00 00 0C 00 00 00  ...............
       *  00504DC4  1B 00 00 00 90 01 00 00 00 00 00 00 60 00 00 00  ...・......`...
       *  00504DD4  60 00 00 00 00 FF A5 02 00 00 00 36 80 00 00 00  `....･...6...
       *  00504DE4  01 00 00 00 00 00 00 00 00 00 00 00 0D 00 00 00  ...............
       *  00504DF4  00 00 00 00 00 00 00 00 00 00 00 00 64 00 00 00  ............d...
       *  00504E04  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E14  82 6C 82 72 20 83 53 83 56 83 62 83 4E 00 00 00  ＭＳ ゴシック...
       *  00504E24  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  Name:
       *  0012F4EC   0043784C  /CALL to GetTextExtentPoint32A from .00437846
       *  0012F4F0   9A010C64  |hDC = 9A010C64
       *  0012F4F4   004C0F30  |Text = "Y"
       *  0012F4F8   00000001  |TextLen = 0x1
       *  0012F4FC   00506410  \pSize = .00506410
       *  0012F500   00504DE4  .00504DE4
       *  0012F504   00439EBE  RETURN to .00439EBE from .00437790
       *  0012F508   00504DE4  .00504DE4
       *  0012F50C   00914CC0  .00914CC0
       *  0012F510   00000001
       *  0012F514   00504DE4  .00504DE4
       *  0012F518   006A1868  .006A1868
       *  0012F51C   00000000
       *  0012F520   00914CC0  .00914CC0
       *
       *  pSize:
       *  00506410  07 00 00 00 0D 00 00 00 0D 00 00 00 0B 00 00 00  ..............
       *  00506420  02 00 00 00 00 00 00 00 00 00 00 00 07 00 00 00  ..............
       *  00506430  0F 00 00 00 90 01 00 00 00 00 00 00 60 00 00 00  ...・......`...
       *  00506440  60 00 00 00 00 FF A5 02 00 00 00 36 80 00 00 00  `....･...6...
       *  00506450  02 00 00 00 00 00 00 00 00 00 00 00 18 00 00 00  ..............
       *  00506460  00 00 00 00 00 00 00 00 00 00 00 00 64 00 00 00  ............d...
       *  00506470  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00506480  82 6C 82 72 20 83 53 83 56 83 62 83 4E 00 00 00  ＭＳ ゴシック...
       *  00506490  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  Values of esi:
       *
       *  Name:
       *  00504DE4  01 00 00 00 B6 0C 0A 76 02 00 00 00 0D 00 00 00  ...ｶ..v.......
       *  00504DF4  00 00 00 00 00 00 00 00 00 00 00 00 64 00 00 00  ............d...
       *  00504E04  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E14  82 6C 82 72 20 83 53 83 56 83 62 83 4E 00 00 00  ＭＳ ゴシック...
       *  00504E24  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E34  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E44  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E54  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E64  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E74  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  ...
       *  00504F44  7C 78 FF 05 3E 00 00 00 3E 00 00 00 02 00 00 00  |x>...>......
       *  00504F54  3E 00 00 00 02 00 00 00 06 00 00 00 00 00 00 00  >.............
       *  00504F64  0C 00 00 00 00 00 00 00 01 00 00 00 31 D9 D3 00  ...........1ﾙﾓ.
       *  00504F74  00 00 00 00 00 00 00 00 00 00 00 00 00 05 00 00  ...............
       *
       *  00504DE4  01 00 00 00 35 06 0A 89 02 00 00 00 0D 00 00 00  ...5.・.......
       *  00504DF4  00 00 00 00 00 00 00 00 00 00 00 00 64 00 00 00  ............d...
       *  00504E04  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E14  82 6C 82 72 20 83 53 83 56 83 62 83 4E 00 00 00  ＭＳ ゴシック...
       *  00504E24  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E34  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E44  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E54  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E64  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E74  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E84  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504E94  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504EA4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504EB4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504EC4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504ED4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504EE4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504EF4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504F04  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00504F14  FF FF FF FF 01 00 00 00 00 01 00 00 00 01 00 00  .........
       *  00504F24  00 01 00 00 FF FF FF 00 00 00 00 00 00 00 00 00  ............
       *  00504F34  01 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00  ............
       *  00504F44  7C 78 0C 06 3E 00 00 00 3E 00 00 00 02 00 00 00  |x.>...>......
       *  00504F54  3E 00 00 00 02 00 00 00 06 00 00 00 00 00 00 00  >.............
       *  00504F64  0C 00 00 00 00 00 00 00 01 00 00 00 C3 46 04 01  ...........ﾃF
       *  00504F74  00 00 00 00 00 00 00 00 00 00 00 00 00 05 00 00  ...............
       *  00504F84  00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00  ...............
       *  00504F94  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  Scenario:
       *  00503778  00 00 00 00 99 12 0A 24 02 00 00 00 18 00 00 00  ....・.$......
       *  00503788  00 00 00 00 00 00 00 00 00 00 00 00 64 00 00 00  ............d...
       *  00503798  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  005037A8  82 6C 82 72 20 83 53 83 56 83 62 83 4E 00 00 00  ＭＳ ゴシック...
       *  005037B8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  ...
       *  005038D8  7C 70 0C 06 24 01 00 00 24 01 00 00 17 00 00 00  |p.$..$.....
       *  005038E8  24 01 00 00 17 00 00 00 0C 00 00 00 2A 00 00 00  $.........*...
       *  005038F8  18 00 00 00 00 00 00 00 01 00 00 00 6D C6 05 01  ..........mﾆ
       *  00503908  00 00 00 00 00 00 00 00 00 00 00 00 18 04 00 00  ..............
       *  00503918  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503928  0D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503938  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503948  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  00503778  00 00 00 00 40 12 0A 9A 02 00 00 00 18 00 00 00  ....@.・......
       *  00503788  00 00 00 00 00 00 00 00 00 00 00 00 64 00 00 00  ............d...
       *  00503798  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  005037A8  82 6C 82 72 20 83 53 83 56 83 62 83 4E 00 00 00  ＭＳ ゴシック...
       *  005037B8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  005037C8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  005037D8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  005037E8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  005037F8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503808  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503818  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503828  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503838  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503848  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503858  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503868  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503878  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503888  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  00503898  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  005038A8  FF FF FF FF 01 00 00 00 00 01 00 00 00 01 00 00  .........
       *  005038B8  00 01 00 00 FF FF FF 00 00 00 00 00 00 00 00 00  ............
       *  005038C8  01 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00  ............
       *  005038D8  7C 70 0C 06 E4 01 00 00 E4 01 00 00 2C 00 00 00  |p.・..・..,...
       *  005038E8  E4 01 00 00 2C 00 00 00 0C 00 00 00 2A 00 00 00  ・..,.......*...
       *  005038F8  18 00 00 00 00 00 00 00 01 00 00 00 5A F5 11 01  ..........Z・
       *  00503908  00 00 00 00 00 00 00 00 00 00 00 00 18 04 00 00  ..............
       *  00503918  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  Sample game: あやかしびと (2.34)
       *  Scenario, value of ebp:
       *  0012FD68  B1 69 3F 77 38 51 42 00 29 42 01 73 38 00 00 00  ｱi?w8QB.)Bs8...
       *  0012FD78  BF 01 00 00 F4 7E 4F 00 02 00 00 00 29 42 01 73  ｿ..O....)Bs
       *  0012FD88  40 00 00 00 40 00 00 00 40 00 00 00 2C E1 71 00  @...@...@...,痃.
       *  0012FD98  00 00 00 00 00 00 00 00 38 E1 71 00 38 00 8A 01  ........8痃.8.・
       *  0012FDA8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0012FDB8  01 00 00 00 EE BA 92 05 F4 24 72 00 85 E9 40 00  ...鋓・・r.・@.  ; jichi: text in 0x0592BAEE
       *  0012FDC8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0012FDD8  C6 08 42 00 02 00 00 00 01 00 00 00 00 00 00 00  ﾆB...........
       *  0012FDE8  00 00 00 00 88 FF 12 00 00 F0 FD 7F 01 00 00 00  ....・..・...
       *  0012FDF8  29 42 01 73 39 F8 B2 90 44 12 0D 64 40 12 0D 64  )Bs9織.d@.d
       *  0012FE08  00 00 00 00 78 FF 12 00 00 00 00 00 00 00 00 00  ....x.........
       *  0012FE18  00 00 00 00 FC FD 12 00 0D 6B E5 75 78 FF 12 00  ....・..k蛄x.
       *  0012FE28  00 00 00 00 E8 3B 29 00 00 00 00 00 01 07 8F 00  ....・).....・
       *  0012FE38  6C FE 12 00 18 67 13 77 F1 31 B1 90 00 00 00 00  l.gw・ｱ・...
       *  0012FE48  E8 3B 29 00 00 00 00 00 00 00 00 00 40 FE 12 00  ・).........@.
       *  0012FE58  68 FE 12 00 F1 2F 13 77 FC 2F 13 77 E8 3B 29 00  h.・w・w・).
       *  0012FE68  7C FE 12 00 25 47 0B 64 00 00 00 00 00 00 00 00  |.%Gd........
       *  0012FE78  CC 3C 29 00 8C FE 12 00 B2 3D 0B 64 CC 3C 29 00  ﾌ<).・.ｲ=dﾌ<).
       *  0012FE88  E8 3B 29 00 AC FE 12 00 20 5B 0B 64 E8 3B 29 00  ・).ｬ. [d・).
       *  0012FE98  00 00 00 00 00 00 00 00 A0 51 50 00 08 80 49 00  ........QP.I.
       *  0012FEA8  00 08 02 00 F8 FE 12 00 9B 28 40 00 EC 3B 29 00  ..・.・@.・).
       *  0012FEB8  61 2B 1D 6F A0 D5 CF 11 BF C7 44 45 53 54 00 00  a+oﾕﾏｿﾇDEST..
       *  0012FEC8  01 67 40 00 68 07 8F 00 00 00 40 00 00 00 00 00  g@.h・..@.....
       *  0012FED8  00 00 00 00 00 F0 FD 7F 8B 22 35 72 28 00 00 00  .....・・5r(...
       *  0012FEE8  EF 7E E7 71 28 00 00 00 33 C4 B1 8D 00 01 00 00  ・輌(...3ﾄｱ・..
       *
       *  Name:
       *  0635C4D0  96 B3 90 FC 00 00 00 00 00 00 00 00 00 00 00 00  無線............
       *  0635C4E0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0635C4F0  96 B3 90 FC 00 00 00 00 00 00 00 00 00 00 00 00  無線............
       *  0635C500  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0635C510  CF 03 07 00 12 70 76 00 12 70 6E 00 12 6E 00 12  ﾏ.pv.pn.n.
       *  0635C520  70 6D 00 12 6D 6E 00 12 66 70 00 12 63 00 80 02  pm.mn.fp.c.
       *  0635C530  06 00 12 70 76 00 12 70 6E 00 12 6E 00 12 70 6D  .pv.pn.n.pm
       *  0635C540  00 12 6D 6E 00 12 66 70 00 16 03 04 0A 00 00 00  .mn.fp.....
       */
      int hookStackIndex_; // hook argument index on the stack
      int textOffset_;     // distance of the text from the hook argument
      bool backtrackText_; // whether backtrack to find text address
      void hookafter(hook_context *s, TextBuffer buffer)
      {

        std::string newData = buffer.strA() + "\x20\x81\x40\x20";

        DWORD argaddr;
        if (hookStackIndex_ == 1)
          argaddr = s->esi;
        else if (hookStackIndex_ == 2)
          argaddr = s->ebp;
        else
          return;
        auto arg = (HookArgument *)argaddr;
        if (Engine::isAddressReadable((argaddr + textOffset_)) == false)
        {
          return;
        }
        LPSTR textAddress = (LPSTR) * (DWORD *)(argaddr + textOffset_),
              charAddress = (LPSTR)s->stack[2]; // arg2 of GetTextExtentPoint32A is the current character's address
                                                // charAddress = LPSTR(s->ebp + 0x60c);
        if (Engine::isAddressWritable(textAddress))
        {
          LPSTR text = textAddress;
          if (backtrackText_)
          {
            for (int i = 0; i < 1500 && *--text; i++)
              ;
            if (*text)
              return;
            text++;
          }
          if (!*text)
            return;
          if (arg->isTextList(text))
          {
            if (backtrackText_) // old shinario games have re-translate problems
              return;
            return;
            arg->dispatchTextList2(text, backtrackText_, newData);
          }
          else
            arg->dispatchText2(text, backtrackText_, newData);
          if (backtrackText_ && Engine::isAddressWritable(charAddress))
          {
            if (textAddress - text == 2)
            { // for wide character
              if ((signed char)textAddress[-2] < 0)
              {
                charAddress[0] = textAddress[-2];
                charAddress[1] = textAddress[-1];
              }
              else
              {
                charAddress[0] = textAddress[-1];
                charAddress[1] = 0;
              }
            }
            else if (textAddress - text == 1)
            { // for thin character
              charAddress[0] = textAddress[-1];
              charAddress[1] = 0;
            }
          }
        }
      }
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        DWORD argaddr;
        if (hookStackIndex_ == 1)
          argaddr = s->esi;
        else if (hookStackIndex_ == 2)
          argaddr = s->ebp;
        else
          return;
        *role = argaddr;
        auto arg = (HookArgument *)argaddr;
        if (Engine::isAddressReadable((argaddr + textOffset_)) == false)
        {
          buffer->from((LPSTR)s->stack[2]);
          return;
        }
        LPSTR textAddress = (LPSTR) * (DWORD *)(argaddr + textOffset_),
              charAddress = (LPSTR)s->stack[2]; // arg2 of GetTextExtentPoint32A is the current character's address
                                                // charAddress = LPSTR(s->ebp + 0x60c);
        if (Engine::isAddressWritable(textAddress))
        {
          LPSTR text = textAddress;
          if (backtrackText_)
          {
            for (int i = 0; i < 1500 && *--text; i++)
              ;
            if (*text)
              return;
            text++;
          }
          if (!*text)
            return;

          if (arg->isTextList(text))
          {
            if (backtrackText_) // old shinario games have re-translate problems
              return;
            arg->dispatchTextList(text, backtrackText_, buffer, role);
          }
          else
            arg->dispatchText(text, backtrackText_, buffer, role);
          return;
          if (backtrackText_ && Engine::isAddressWritable(charAddress))
          {
            if (textAddress - text == 2)
            { // for wide character
              if ((signed char)textAddress[-2] < 0)
              {
                charAddress[0] = textAddress[-2];
                charAddress[1] = textAddress[-1];
              }
              else
              {
                charAddress[0] = textAddress[-1];
                charAddress[1] = 0;
              }
            }
            else if (textAddress - text == 1)
            { // for thin character
              charAddress[0] = textAddress[-1];
              charAddress[1] = 0;
            }
          }
        }
      }

    } // namespace Private

    /**
     *  Sample game: 幻創のイデア (RIO 2.49)
     *  Text painted by GetGlyphOutlineA.
     *  Debugged by attaching to GetTextExtentPoint32A.
     *  There is only one GetTextExtentPoint32A in the game, where only 'Y' (0x59) is calculated.
     *  Text is in a large memory region that can be modified.
     *
     *  When the text contains new line (_r), the same text will be invoked twice.
     *  Need to avoid immediate duplicate.
     *
     *  Sample game: Vestige 体験版 (RIO 2.47)
     *  Text accessed character by character
     *
     *  Scenario caller of get GetTextExtentPoint32A
     *  0043372D   05 00010000      ADD EAX,0x100
     *  00433732   66:8B1445 045548>MOV DX,WORD PTR DS:[EAX*2+0x485504]
     *  0043373A   EB 2D            JMP SHORT .00433769
     *  0043373C   33C9             XOR ECX,ECX
     *  0043373E   8B8D 60010000    MOV ECX,DWORD PTR SS:[EBP+0x160]
     *  00433744   8A09             MOV CL,BYTE PTR DS:[ECX]
     *  00433746   80F9 20          CMP CL,0x20
     *  00433749   74 2E            JE SHORT .00433779
     *  0043374B   8B85 C0050000    MOV EAX,DWORD PTR SS:[EBP+0x5C0]
     *  00433751   81E1 FF000000    AND ECX,0xFF
     *  00433757   85C0             TEST EAX,EAX
     *  00433759   74 06            JE SHORT .00433761
     *  0043375B   81C1 00010000    ADD ECX,0x100
     *  00433761   66:8B144D 045548>MOV DX,WORD PTR DS:[ECX*2+0x485504]
     *  00433769   B8 02000000      MOV EAX,0x2
     *  0043376E   66:8995 0C060000 MOV WORD PTR SS:[EBP+0x60C],DX
     *  00433775   894424 58        MOV DWORD PTR SS:[ESP+0x58],EAX
     *  00433779   8B4C24 1C        MOV ECX,DWORD PTR SS:[ESP+0x1C]
     *  0043377D   898D 60010000    MOV DWORD PTR SS:[EBP+0x160],ECX
     *  00433783   8B8D 78010000    MOV ECX,DWORD PTR SS:[EBP+0x178]
     *  00433789   83F9 FF          CMP ECX,-0x1
     *  0043378C   8BB5 68010000    MOV ESI,DWORD PTR SS:[EBP+0x168]
     *  00433792   75 3E            JNZ SHORT .004337D2
     *  00433794   85DB             TEST EBX,EBX
     *  00433796   74 3A            JE SHORT .004337D2
     *  00433798   8B85 10160000    MOV EAX,DWORD PTR SS:[EBP+0x1610]
     *  0043379E   85C0             TEST EAX,EAX
     *  004337A0   74 12            JE SHORT .004337B4
     *  004337A2   8B95 14160000    MOV EDX,DWORD PTR SS:[EBP+0x1614]
     *  004337A8   894424 2C        MOV DWORD PTR SS:[ESP+0x2C],EAX
     *  004337AC   895424 30        MOV DWORD PTR SS:[ESP+0x30],EDX
     *  004337B0   03F0             ADD ESI,EAX
     *  004337B2   EB 36            JMP SHORT .004337EA
     *  004337B4   8B4C24 58        MOV ECX,DWORD PTR SS:[ESP+0x58]
     *  004337B8   8D4424 2C        LEA EAX,DWORD PTR SS:[ESP+0x2C]
     *  004337BC   50               PUSH EAX
     *  004337BD   51               PUSH ECX
     *  004337BE   8D85 0C060000    LEA EAX,DWORD PTR SS:[EBP+0x60C]
     *  004337C4   50               PUSH EAX
     *  004337C5   53               PUSH EBX
     *  004337C6   FF15 A0B04700    CALL DWORD PTR DS:[0x47B0A0]             ; gdi32.GetTextExtentPoint32A
     *  004337CC   037424 2C        ADD ESI,DWORD PTR SS:[ESP+0x2C]
     *  004337D0   EB 18            JMP SHORT .004337EA
     *  004337D2   83F8 02          CMP EAX,0x2
     *  004337D5   75 06            JNZ SHORT .004337DD
     *  004337D7   8B8D 80010000    MOV ECX,DWORD PTR SS:[EBP+0x180]
     *  004337DD   8B95 84010000    MOV EDX,DWORD PTR SS:[EBP+0x184]
     *  004337E3   0FAFD0           IMUL EDX,EAX
     *  004337E6   03F1             ADD ESI,ECX
     *  004337E8   03F2             ADD ESI,EDX
     *  004337EA   3BB5 9C010000    CMP ESI,DWORD PTR SS:[EBP+0x19C]
     *  004337F0   72 68            JB SHORT .0043385A
     *  004337F2   8D85 0C060000    LEA EAX,DWORD PTR SS:[EBP+0x60C]
     *  004337F8   50               PUSH EAX
     *  004337F9   8D85 B8020000    LEA EAX,DWORD PTR SS:[EBP+0x2B8]
     *  004337FF   50               PUSH EAX
     *  00433800   E8 6D230100      CALL .00445B72
     *  00433805   83C4 08          ADD ESP,0x8
     *  00433808   85C0             TEST EAX,EAX
     *  0043380A   74 4E            JE SHORT .0043385A
     *  0043380C   8B8D 68010000    MOV ECX,DWORD PTR SS:[EBP+0x168]
     *  00433812   8B95 6C010000    MOV EDX,DWORD PTR SS:[EBP+0x16C]
     *  00433818   8B85 64010000    MOV EAX,DWORD PTR SS:[EBP+0x164]
     *  0043381E   8985 68010000    MOV DWORD PTR SS:[EBP+0x168],EAX
     *  00433824   8995 74010000    MOV DWORD PTR SS:[EBP+0x174],EDX
     *  0043382A   8B95 6C010000    MOV EDX,DWORD PTR SS:[EBP+0x16C]
     *  00433830   898D 70010000    MOV DWORD PTR SS:[EBP+0x170],ECX
     *  00433836   8B8D 7C010000    MOV ECX,DWORD PTR SS:[EBP+0x17C]
     *  0043383C   03D1             ADD EDX,ECX
     *  0043383E   8995 6C010000    MOV DWORD PTR SS:[EBP+0x16C],EDX
     *  00433844   8B95 A8010000    MOV EDX,DWORD PTR SS:[EBP+0x1A8]
     *  0043384A   0195 68010000    ADD DWORD PTR SS:[EBP+0x168],EDX
     *  00433850   C785 A4010000 01>MOV DWORD PTR SS:[EBP+0x1A4],0x1
     *  0043385A   8B85 B4010000    MOV EAX,DWORD PTR SS:[EBP+0x1B4]
     *  00433860   85C0             TEST EAX,EAX
     *  00433862   0F85 F6000000    JNZ .0043395E
     *  00433868   8B85 68010000    MOV EAX,DWORD PTR SS:[EBP+0x168]
     *  0043386E   3B85 64010000    CMP EAX,DWORD PTR SS:[EBP+0x164]
     *  00433874   74 0E            JE SHORT .00433884
     *  00433876   8B85 AC010000    MOV EAX,DWORD PTR SS:[EBP+0x1AC]
     *  0043387C   85C0             TEST EAX,EAX
     *  0043387E   0F84 E4000000    JE .00433968
     *  00433884   8B85 A4010000    MOV EAX,DWORD PTR SS:[EBP+0x1A4]
     *  0043388A   85C0             TEST EAX,EAX
     *  0043388C   0F84 D6000000    JE .00433968
     *  00433892   8BB5 60010000    MOV ESI,DWORD PTR SS:[EBP+0x160]
     *  00433898   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  0043389A   3C 81            CMP AL,0x81
     *  0043389C   72 13            JB SHORT .004338B1
     *  0043389E   3C 9F            CMP AL,0x9F
     *  004338A0   76 08            JBE SHORT .004338AA
     *  004338A2   3C E0            CMP AL,0xE0
     *  004338A4   72 0B            JB SHORT .004338B1
     *  004338A6   3C FC            CMP AL,0xFC
     *  004338A8   77 07            JA SHORT .004338B1
     *  004338AA   B8 01000000      MOV EAX,0x1
     *  004338AF   EB 02            JMP SHORT .004338B3
     *  004338B1   33C0             XOR EAX,EAX
     *  004338B3   8D48 01          LEA ECX,DWORD PTR DS:[EAX+0x1]
     *  004338B6   8BD1             MOV EDX,ECX
     *  004338B8   C1E9 02          SHR ECX,0x2
     *  004338BB   C74424 18 000000>MOV DWORD PTR SS:[ESP+0x18],0x0
     *  004338C3   8D7C24 18        LEA EDI,DWORD PTR SS:[ESP+0x18]
     *  004338C7   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
     *  004338C9   8BCA             MOV ECX,EDX
     *  004338CB   83E1 03          AND ECX,0x3
     *  004338CE   8D85 0C060000    LEA EAX,DWORD PTR SS:[EBP+0x60C]
     *  004338D4   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[>
     *  004338D6   50               PUSH EAX
     *  004338D7   8DB5 B8030000    LEA ESI,DWORD PTR SS:[EBP+0x3B8]
     *  004338DD   56               PUSH ESI
     *  004338DE   E8 8F220100      CALL .00445B72
     *  004338E3   83C4 08          ADD ESP,0x8
     *  004338E6   85C0             TEST EAX,EAX
     *  004338E8   74 2C            JE SHORT .00433916
     *  004338EA   8D4424 18        LEA EAX,DWORD PTR SS:[ESP+0x18]
     *  004338EE   50               PUSH EAX
     *  004338EF   56               PUSH ESI
     *  004338F0   E8 7D220100      CALL .00445B72
     *  004338F5   83C4 08          ADD ESP,0x8
     *  004338F8   85C0             TEST EAX,EAX
     *  004338FA   75 34            JNZ SHORT .00433930
     *  004338FC   8D4C24 18        LEA ECX,DWORD PTR SS:[ESP+0x18]
     *  00433900   51               PUSH ECX
     *  00433901   8D95 B8010000    LEA EDX,DWORD PTR SS:[EBP+0x1B8]
     *  00433907   52               PUSH EDX
     *  00433908   E8 65220100      CALL .00445B72
     *  0043390D   83C4 08          ADD ESP,0x8
     *  00433910   85C0             TEST EAX,EAX
     *  00433912   75 3E            JNZ SHORT .00433952
     *  00433914   EB 1A            JMP SHORT .00433930
     *  00433916   8D85 0C060000    LEA EAX,DWORD PTR SS:[EBP+0x60C]
     *  0043391C   50               PUSH EAX
     *  0043391D   8D95 B8010000    LEA EDX,DWORD PTR SS:[EBP+0x1B8]
     *  00433923   52               PUSH EDX
     *  00433924   E8 49220100      CALL .00445B72
     *  00433929   83C4 08          ADD ESP,0x8
     *  0043392C   85C0             TEST EAX,EAX
     *  0043392E   74 22            JE SHORT .00433952
     *  00433930   8B85 70010000    MOV EAX,DWORD PTR SS:[EBP+0x170]
     *  00433936   8B8D 74010000    MOV ECX,DWORD PTR SS:[EBP+0x174]
     *  0043393C   8985 68010000    MOV DWORD PTR SS:[EBP+0x168],EAX
     *  00433942   898D 6C010000    MOV DWORD PTR SS:[EBP+0x16C],ECX
     *  00433948   C785 B4010000 01>MOV DWORD PTR SS:[EBP+0x1B4],0x1
     *  00433952   C785 AC010000 00>MOV DWORD PTR SS:[EBP+0x1AC],0x0
     *  0043395C   EB 0A            JMP SHORT .00433968
     *  0043395E   C785 B4010000 00>MOV DWORD PTR SS:[EBP+0x1B4],0x0
     *  00433968   85DB             TEST EBX,EBX
     *  0043396A   0F84 1A070000    JE .0043408A
     *  00433970   8B85 10160000    MOV EAX,DWORD PTR SS:[EBP+0x1610]
     *  00433976   85C0             TEST EAX,EAX
     *  00433978   74 10            JE SHORT .0043398A
     *  0043397A   8B95 14160000    MOV EDX,DWORD PTR SS:[EBP+0x1614]
     *  00433980   894424 2C        MOV DWORD PTR SS:[ESP+0x2C],EAX
     *  00433984   895424 30        MOV DWORD PTR SS:[ESP+0x30],EDX
     *  00433988   EB 18            JMP SHORT .004339A2
     *  0043398A   8B4C24 58        MOV ECX,DWORD PTR SS:[ESP+0x58]
     *  0043398E   8D4424 2C        LEA EAX,DWORD PTR SS:[ESP+0x2C]
     *  00433992   50               PUSH EAX
     *  00433993   51               PUSH ECX
     *  00433994   8D85 0C060000    LEA EAX,DWORD PTR SS:[EBP+0x60C]    ; jichi: This is the individual character
     *  0043399A   50               PUSH EAX
     *  0043399B   53               PUSH EBX
     *  0043399C   FF15 A0B04700    CALL DWORD PTR DS:[0x47B0A0]             ; gdi32.GetTextExtentPoint32A	; jichi: called here
     *  004339A2   8B85 68010000    MOV EAX,DWORD PTR SS:[EBP+0x168]
     *  004339A8   8B5424 2C        MOV EDX,DWORD PTR SS:[ESP+0x2C]
     *  004339AC   8B8D 6C010000    MOV ECX,DWORD PTR SS:[EBP+0x16C]
     *  004339B2   8D3410           LEA ESI,DWORD PTR DS:[EAX+EDX]
     *  004339B5   8B5424 30        MOV EDX,DWORD PTR SS:[ESP+0x30]
     *  004339B9   8BF9             MOV EDI,ECX
     *  004339BB   03CA             ADD ECX,EDX
     */
    bool attach(int ver)
    {
      // if (ver < 247) // currently only >= 2.48 is supported
      //   return false;

      if (ver >= 248)
      {
        Private::hookStackIndex_ = 1; // winhook_stack_indexof(esi);
        Private::backtrackText_ = false;
      }
      else
      {                               // <= 247
        Private::hookStackIndex_ = 2; // winhook_stack_indexof(ebp);
        Private::backtrackText_ = true;
      }

      if (ver >= 240)
        Private::textOffset_ = 0x160;
      else
        Private::textOffset_ = 0x54; // Sample game: あやかしびと (2.34)
      HookParam hp;
      hp.address = (ULONG)::GetTextExtentPoint32A;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
      hp.lineSeparator = L"_r";
      hp.embed_hook_font = F_GetGlyphOutlineA;
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        auto s = buffer->strA();
        if (endWith(s, "\x20\x81\x40\x20"))
          return buffer->clear();
        static std::string last;
        if (last == s)
          return buffer->clear();
        last = s;
        strReplace(s, "\n");
        buffer->from(re::sub(s, "_t!.*?[/>]"));
      };
      return NewHook(hp, "EmbedShinario");
    }

  } // namespace ScenarioHook
} // unnamed namespace

bool ShinaRio::attach_function()
{
  int ver = GetShinaRioVersion();
  if (ver <= 20)
  {
    // https://vndb.org/v3419
    PcHooks::hookGDIFunctions(GetTextExtentPoint32A);
    return true;
  }
  auto _h = InsertShinaHook(ver);
  auto e = ScenarioHook::attach(ver + 200);
  return _h || e;
}