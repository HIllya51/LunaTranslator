#include "Unicorn.h"
/**
 *  jichi 9/16/2013: a-unicorn / gesen18
 *  See (CaoNiMaGeBi): http://tieba.baidu.com/p/2586681823
 *  Pattern: 2bce8bf8
 *      2bce      sub ecx,esi ; hook here
 *      8bf8      mov eds,eax
 *      8bd1      mov edx,ecx
 *
 *  /HBN-20*0@xxoo
 *  - length_offset: 1
 *  - off: 4294967260 (0xffffffdc)
 *  - type: 1032 (0x408)
 */
bool InsertUnicornHook()
{
  // pattern: 2bce8bf8
  const BYTE bytes[] = {
      0x2b, 0xce, // sub ecx,esi ; hook here
      0x8b, 0xf8  // mov edi,eax
  };
  // enum { addr_offset = 0 };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Unicorn: pattern not exist");
    return false;
  }

  HookParam hp;
  hp.type = NO_CONTEXT | DATA_INDIRECT;
  hp.offset = regoffset(edi);
  hp.address = addr;

  // index = SearchPattern(processStartAddress, size,ins, sizeof(ins));
  // GROWL_DWORD2(base, index);

  ConsoleOutput("INSERT Unicorn");
  return NewHook(hp, "Unicorn");
}
namespace
{ // unnamed
  // A simple but very inefficient implementation for LRU cache.

  namespace ScenarioHook
  {

    lru_cache<uint64_t> textCache_(30); // capacity = 30

    namespace Private
    {

      class TextStorage
      {
        LPSTR text_;
        std::string oldData_,
            newData_;
        int lineCount_;
        bool saved_;

      public:
        TextStorage()
            : text_(nullptr), lineCount_(0), saved_(false) {}

        bool isEmpty() const
        {
          return lineCount_ == 0;
        }

        void clear()
        {
          text_ = nullptr;
          lineCount_ = 0;
          saved_ = false;
          oldData_.clear();
          newData_.clear();
        }

        std::string load(char *textAddress);
        void save();
        bool restore(); // recover old text
      } textStorage_;

      // Hook

      ULONG textOffset_; // = 0x114;

      std::string sourceData_;
      LPSTR targetText_;
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        // Sample game:  三極姫4 ～天華繚乱 天命の恋絵巻～
        // 004B76BB   51               PUSH ECX
        // 004B76BC   8BCB             MOV ECX,EBX
        // 004B76BE   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
        // 004B76C2   E8 89A5FFFF      CALL Sangokuh.004B1C50	; jichi: name caller
        // 004B76C7   E8 44A5FFFF      CALL Sangokuh.004B1C10
        // 004B76CC   85C0             TEST EAX,EAX
        // 004B76CE   0F8E F6000000    JLE Sangokuh.004B77CA
        // 004B76D4   8BF8             MOV EDI,EAX
        // 004B76D6   EB 08            JMP SHORT Sangokuh.004B76E0
        // 004B76D8   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
        // 004B76DF   90               NOP
        // 004B76E0   33C0             XOR EAX,EAX
        // 004B76E2   B9 0F000000      MOV ECX,0xF
        // 004B76E7   898C24 FC000000  MOV DWORD PTR SS:[ESP+0xFC],ECX
        // 004B76EE   898424 F8000000  MOV DWORD PTR SS:[ESP+0xF8],EAX
        // 004B76F5   888424 E8000000  MOV BYTE PTR SS:[ESP+0xE8],AL
        // 004B76FC   898C24 18010000  MOV DWORD PTR SS:[ESP+0x118],ECX
        // 004B7703   898424 14010000  MOV DWORD PTR SS:[ESP+0x114],EAX
        // 004B770A   888424 04010000  MOV BYTE PTR SS:[ESP+0x104],AL
        // 004B7711   8D9424 84040000  LEA EDX,DWORD PTR SS:[ESP+0x484]
        // 004B7718   52               PUSH EDX
        // 004B7719   8BCB             MOV ECX,EBX
        // 004B771B   C68424 AC060000 01 MOV BYTE PTR SS:[ESP+0x6AC],0x1
        // 004B7723   E8 28A5FFFF      CALL Sangokuh.004B1C50	; jichi: scenario caller
        // 004B7728   8D8424 84040000  LEA EAX,DWORD PTR SS:[ESP+0x484]
        // 004B772F   50               PUSH EAX
        // 004B7730   8D8C24 E8000000  LEA ECX,DWORD PTR SS:[ESP+0xE8]
        //
        // Sample game: 天極姫 ～新世大乱･双界の覇者達～
        // Name caller:
        // 0049A83B   E8 D0AFFFFF      CALL .00495810
        // 0049A840   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
        // 0049A844   8D8424 EC010000  LEA EAX,DWORD PTR SS:[ESP+0x1EC]
        // 0049A84B   50               PUSH EAX
        // 0049A84C   E8 DFAFFFFF      CALL .00495830 ; jichi: name caller
        // 0049A851   E8 9AAFFFFF      CALL .004957F0
        // 0049A856   BD 0F000000      MOV EBP,0xF
        // 0049A85B   85C0             TEST EAX,EAX
        // 0049A85D   0F8E E3000000    JLE .0049A946

        auto retaddr = s->stack[0];
        *role = 0;
        // if (retaddr == 0x4b7728)
        if ((*(DWORD *)(retaddr - 5 - 8) & 0x00ffffff) == 0x2484c6) // 004B771B   C68424 AC060000 01 MOV BYTE PTR SS:[ESP+0x6AC],0x1
          *role = Engine::ScenarioRole;
        // else if (retaddr == 0x4b76c7)
        else if ((*(DWORD *)(retaddr - 5 - 8) & 0x00ffffff) == 0x0024848d     // 0049A844   8D8424 EC010000  LEA EAX,DWORD PTR SS:[ESP+0x1EC]
                 || (*(DWORD *)(retaddr - 5 - 4) & 0x00ffffff) == 0x00244489) // 004B76BE   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
          *role = Engine::NameRole;
        // else
        //   return true;
        if (*role != Engine::ScenarioRole && !textStorage_.isEmpty())
        {
          textStorage_.restore();
          textStorage_.clear();
        }
        if (!*role)
          return;

        auto text = (LPSTR) * (DWORD *)(s->ecx + textOffset_); // [ecx+0x114]
        if (!*text || all_ascii(text))                         // allspaces is only needed when textstorage is enabled though
          return;

        if (!textStorage_.isEmpty())
        {
          textStorage_.restore();
          textStorage_.clear();
        }

        bool textStorageEnabled = *role == Engine::ScenarioRole && Engine::isAddressWritable(text);
        std::string oldData;
        if (textStorageEnabled)
          oldData = textStorage_.load(text);
        else
          oldData = text;

        if (*role == Engine::NameRole)
          strReplace(oldData, "\x81\x40");
        // oldData.replace("\x81\x40", ""); // remove spaces in the middle of names
        buffer->from(oldData);
      }
      void hookafter2(hook_context *s, TextBuffer buffer)
      {

        auto newData = buffer.strA();
        auto retaddr = s->stack[0];
        int role = 0;
        // if (retaddr == 0x4b7728)
        if ((*(DWORD *)(retaddr - 5 - 8) & 0x00ffffff) == 0x2484c6) // 004B771B   C68424 AC060000 01 MOV BYTE PTR SS:[ESP+0x6AC],0x1
          role = Engine::ScenarioRole;
        // else if (retaddr == 0x4b76c7)
        else if ((*(DWORD *)(retaddr - 5 - 8) & 0x00ffffff) == 0x0024848d     // 0049A844   8D8424 EC010000  LEA EAX,DWORD PTR SS:[ESP+0x1EC]
                 || (*(DWORD *)(retaddr - 5 - 4) & 0x00ffffff) == 0x00244489) // 004B76BE   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
          role = Engine::NameRole;
        // else
        //   return true;
        if (role != Engine::ScenarioRole && !textStorage_.isEmpty())
        {
          textStorage_.restore();
          textStorage_.clear();
        }
        if (!role)
          return;
        auto text = (LPSTR) * (DWORD *)(s->ecx + textOffset_); // [ecx+0x114]
        if (!*text || all_ascii(text))                         // allspaces is only needed when textstorage is enabled though
          return;
        if (!textStorage_.isEmpty())
        {
          textStorage_.restore();
          textStorage_.clear();
        }
        bool textStorageEnabled = role == Engine::ScenarioRole && Engine::isAddressWritable(text);
        std::string oldData;
        if (textStorageEnabled)
          oldData = textStorage_.load(text);
        else
          oldData = text;
        if (role == Engine::NameRole)
          strReplace(oldData, "\x81\x40");
        // oldData.replace("\x81\x40", ""); // remove spaces in the middle of names
        if (oldData == newData)
        {
          if (textStorageEnabled)
            textStorage_.clear();
          return;
        }
        if (textStorageEnabled)
          textStorage_.save();
        sourceData_ = newData;
        targetText_ = (LPSTR)s->stack[1]; // arg1
        textCache_.put(simplehash::hashByteArraySTD(newData));
      }
      void hookAfter(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        if (targetText_)
        {
          ::strcpy(targetText_, sourceData_.c_str());
          targetText_ = nullptr;
        }
      }

    } // namespace Private

    /**
     *  Sample text
     *
     *  Sample game:  三極姫4 ～天華繚乱 天命の恋絵巻～
     *
     *  01FE881C  81 40 92 6A 81 40 00 01 81 75 82 BB 81 41 82 BB  　男　.「そ、そ
     *  01FE882C  82 F1 82 C8 81 63 81 63 82 BB 82 EA 82 AA 8D C5  んな……それが最
     *  01FE883C  8C E3 82 CC 90 48 97 BF 82 C8 82 CC 82 C9 81 63  後の食料なのに…
     *  01FE884C  81 63 81 49 81 76 00 00 00 00 FF FF FF FF FF FF  …！」....
     *  01FE885C  FF FF 11 19 00 1B 00 0F 19 00 1D 00 03 00 00 00  .......
     *  01FE886C  03 00 00 00 00 01 97 AA 92 44 81 5C 81 5C 00 00  ....略奪――..
     *
     *  01FE8758  01 00 00 00 01 00 00 00 93 90 81 40 91 AF 00 02  ......盗　賊.
     *  01FE8768  81 75 82 C7 82 A4 82 B9 82 B1 82 EA 82 C1 82 DB  「どうせこれっぽ
     *  01FE8778  82 C1 82 BF 82 CC 90 48 97 BF 82 AA 82 A0 82 C1  っちの食料があっ
     *  01FE8788  82 BD 82 C6 82 B1 82 EB 82 C5 81 41 8B 51 82 A6  たところで、飢え
     *  01FE8798  82 C4 8E 80 00 00 00 00 FF FF FF FF FF FF FF FF  て死....
     *  01FE87A8  0A 82 CA 82 CC 82 CD 93 AF 82 B6 82 BE 82 EB 81  .ぬのは同じだろ・
     *  01FE87B8  49 81 40 82 D9 82 E7 91 53 95 94 82 E6 82 B1 82  I　ほら全部よこ・
     *  01FE87C8  B9 82 C1 81 49 81 76 00 00 00 00 FF FF FF FF FF  ｹっ！」....
     *  01FE87D8  FF FF FF 11 19 00 16 00 19 19 00 18 00 32 00 00  ....2..
     *  01FE87E8  00 44 61 74 61 5C 76 6F 69 63 65 5C 65 74 63 5C  .Data\voice\etc\
     *  01FE87F8  65 74 63 4A 5F 70 63 41 5F 30 30 30 31 2E 76 6F  etcJ_pcA_0001.vo
     *  01FE8808  69 00 00 00 00 00 00 0F 19 00 19 00 02 00 00 00  i...........
     *
     *  Sample game: 戦極姫6
     *
     *  023AF0E8  82 BB 82 CC 90 BA 82 F0 95 B7 82 AB 81 41 90 B0  その声を聞き、晴
     *  023AF0F8  90 4D 82 CD 82 B7 82 C1 82 C6 95 5C 8F EE 82 F0  信はすっと表情を
     *  023AF108  88 F8 82 AB 92 F7 82 DF 82 BD 81 42 00 00 00 00  引き締めた。....
     *  023AF118  BE BE BE FF FF FF FF FF 11 0E 00 1E 00 0F 0E 00  ｾｾｾ...
     *  023AF128  20 00 03 00 00 00 03 00 00 00 95 90 93 63 90 4D   .......武田信
     *  023AF138  94 C9 00 01 81 75 90 4D 8C D5 97 6C 82 CD 81 41  繁.「信虎様は、
     *  023AF148  97 5C 92 E8 82 C7 82 A8 82 E8 82 BE 82 BB 82 A4  予定どおりだそう
     *  023AF158  82 BE 81 76 00 00 00 00 BE BE BE FF FF FF FF FF  だ」....ｾｾｾ
     *  023AF168  11 0E 00 22 00 0F 0E 00 24 00 04 00 00 00 04 00  ."..$.....
     *  023AF178  00 00 00 02 95 94 89 AE 82 C9 82 CD 82 A2 82 C1  ...部屋にはいっ
     *  023AF188  82 C4 82 AB 82 BD 90 4D 94 C9 82 CD 81 41 90 B0  てきた信繁は、晴
     *  023AF198  90 4D 82 CC 91 4F 82 D6 82 C6 8D 98 82 F0 82 A8  信の前へと腰をお
     *  023AF1A8  82 EB 82 B5 8C FC 82 A9 00 00 00 00 BE BE BE FF  ろし向か....ｾｾｾ
     *  023AF1B8  FF FF FF FF 0A 82 A2 82 A0 82 A4 81 42 00 00 00  .いあう。...
     *  023AF1C8  00 BE BE BE FF FF FF FF FF 11 0E 00 27 00 01 0E  .ｾｾｾ.'.
     *  023AF1D8  00 2A 00 84 D9 07 00 02 00 00 00 E8 18 00 00 01  .*.・....・..
     *  023AF1E8  60 00 00 00 E9 18 00 00 01 5B 00 00 00 19 0E 00  `...・..[....
     *  023AF1F8  2C 00 06 00 00 00 44 61 74 61 5C 76 6F 69 63 65  ,....Data\voice
     *  023AF208  5C 73 69 6E 67 65 6E 5C 73 69 6E 67 65 6E 5F 30  \singen\singen_0
     *  023AF218  30 34 33 2E 76 6F 69 00 00 00 00 00 00 0F 0E 00  043.voi.......
     *
     *  Sample game: 天極姫 ～新世大乱･双界の覇者達～
     *  0211F8AA  82 91 80 82 BD 82 BF 82 CD 82 B1 82 CC 90 A2 8A  ｑたちはこの世・
     *  0211F8BA  45 82 C9 93 CB 91 52 8C BB 82 EA 82 BD 81 42 82  Eに突然現れた。・
     *  0211F8CA  BB 82 B5 82 C4 82 B1 82 B1 82 CC 96 AF 82 BD 82  ｻしてここの民た・
     *  0211F8DA  BF 82 CD 00 00 00 00 BE BE BE FF FF FF FF FF 0A  ｿは....ｾｾｾ.
     *  0211F8EA  91 82 91 80 82 BD 82 BF 82 F0 81 41 92 B7 82 AD  曹操たちを、長く
     *  0211F8FA  91 B1 82 A2 82 BD 90 ED 97 90 82 F0 8F 49 82 ED  続いた戦乱を終わ
     *  0211F90A  82 E7 82 B9 82 E9 89 70 97 59 82 C6 81 41 96 7B  らせる英雄と、本
     *  0211F91A  8B 43 82 C5 00 00 00 00 BE BE BE FF FF FF FF FF  気で....ｾｾｾ
     *  0211F92A  0A 90 4D 82 B6 82 C4 82 A2 82 E9 82 C6 82 A2 82  .信じているとい・
     *  0211F93A  A4 82 B1 82 C6 82 BE 82 C1 82 BD 81 42 00 00 00  ､ことだった。...
     */
    // 三極姫4: 00 00 00 00 ff ff ff ff ff ff ff ff 0a
    // 戦極姫6: 00 00 00 00 be be be ff ff ff ff ff 0a
    // enum { TextSeparatorSize = 12 };
    static inline bool isTextSeparator(LPCSTR text)
    {
      // return 0 == ::memcmp(p, "\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x0a", 13);
      return 0 == ::memcmp(text, "\x00\x00\x00\x00", 4) && 0 == ::memcmp(text + 8, "\xff\xff\xff\xff\x0a", 5);
    }
    std::string Private::TextStorage::load(char *text)
    {
      text_ = text;
      std::string data = text;
      lineCount_ = 1;
      LPCSTR p = text + ::strlen(text);
      for (; isTextSeparator(p); p += ::strlen(p))
      {
        lineCount_++;
        p += 12;
        data.append(p);
      }
      oldData_ = std::string(text, p - text);
      return data;
    }

    void Private::TextStorage::save()
    {
      if (lineCount_ <= 1)
        return;
      LPSTR p = text_ + ::strlen(text_);
      while (isTextSeparator(p))
      {
        p += 12 + 1; // +1 for the extra 0xa
        if (size_t size = ::strlen(p))
        {
          ::memset(p, ' ', size);
          p += size;
        }
      }
      newData_ = std::string(text_, p - text_);
    }

    bool Private::TextStorage::restore()
    {
      if (!saved_ || !Engine::isAddressWritable(text_, oldData_.size()) || ::memcmp(text_, newData_.c_str(), newData_.size()))
        return false;
      if (::memcmp(text_, oldData_.c_str(), oldData_.size()))
        ::memcpy(text_, oldData_.c_str(), oldData_.size());
      saved_ = false;
      return true;
    }

    /**
     *  Sample game:  三極姫4 ～天華繚乱 天命の恋絵巻～
     *
     *  Function found by hardware breakpoint scenario text.
     *
     *  The memory copy function:
     *  004B1C4D   CC               INT3
     *  004B1C4E   CC               INT3
     *  004B1C4F   CC               INT3
     *  004B1C50   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]	; jichi: source text in eax, beforeAddress
     *  004B1C56   8B5424 04        MOV EDX,DWORD PTR SS:[ESP+0x4]		; jichi: target address in edx
     *  004B1C5A   56               PUSH ESI
     *  004B1C5B   33F6             XOR ESI,ESI
     *  004B1C5D   8038 00          CMP BYTE PTR DS:[EAX],0x0
     *  004B1C60   74 1D            JE SHORT Sangokuh.004B1C7F
     *  004B1C62   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]
     *  004B1C68   8A00             MOV AL,BYTE PTR DS:[EAX]
     *  004B1C6A   8802             MOV BYTE PTR DS:[EDX],AL
     *  004B1C6C   FF81 14010000    INC DWORD PTR DS:[ECX+0x114]
     *  004B1C72   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]
     *  004B1C78   42               INC EDX
     *  004B1C79   46               INC ESI
     *  004B1C7A   8038 00          CMP BYTE PTR DS:[EAX],0x0
     *  004B1C7D  ^75 E3            JNZ SHORT Sangokuh.004B1C62
     *  004B1C7F   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]
     *  004B1C85   8A00             MOV AL,BYTE PTR DS:[EAX]
     *  004B1C87   8802             MOV BYTE PTR DS:[EDX],AL
     *  004B1C89   FF81 14010000    INC DWORD PTR DS:[ECX+0x114]
     *  004B1C8F   8BC6             MOV EAX,ESI ; jichi: copied count
     *  004B1C91   5E               POP ESI
     *  004B1C92   C2 0400          RETN 0x4 ; jichi: afterAddress
     *  004B1C95   CC               INT3
     *  004B1C96   CC               INT3
     *  004B1C97   CC               INT3
     *
     *  The very large caller function:
     *
     *  004B76AB   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
     *  004B76AF   E8 7CA5FFFF      CALL Sangokuh.004B1C30
     *  004B76B4   8D8C24 7C030000  LEA ECX,DWORD PTR SS:[ESP+0x37C]
     *  004B76BB   51               PUSH ECX
     *  004B76BC   8BCB             MOV ECX,EBX
     *  004B76BE   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
     *  004B76C2   E8 89A5FFFF      CALL Sangokuh.004B1C50	; jichi: name caller
     *  004B76C7   E8 44A5FFFF      CALL Sangokuh.004B1C10
     *  004B76CC   85C0             TEST EAX,EAX
     *  004B76CE   0F8E F6000000    JLE Sangokuh.004B77CA
     *  004B76D4   8BF8             MOV EDI,EAX
     *  004B76D6   EB 08            JMP SHORT Sangokuh.004B76E0
     *  004B76D8   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
     *  004B76DF   90               NOP
     *  004B76E0   33C0             XOR EAX,EAX
     *  004B76E2   B9 0F000000      MOV ECX,0xF
     *  004B76E7   898C24 FC000000  MOV DWORD PTR SS:[ESP+0xFC],ECX
     *  004B76EE   898424 F8000000  MOV DWORD PTR SS:[ESP+0xF8],EAX
     *  004B76F5   888424 E8000000  MOV BYTE PTR SS:[ESP+0xE8],AL
     *  004B76FC   898C24 18010000  MOV DWORD PTR SS:[ESP+0x118],ECX
     *  004B7703   898424 14010000  MOV DWORD PTR SS:[ESP+0x114],EAX
     *  004B770A   888424 04010000  MOV BYTE PTR SS:[ESP+0x104],AL
     *  004B7711   8D9424 84040000  LEA EDX,DWORD PTR SS:[ESP+0x484]
     *  004B7718   52               PUSH EDX
     *  004B7719   8BCB             MOV ECX,EBX
     *  004B771B   C68424 AC060000 01 MOV BYTE PTR SS:[ESP+0x6AC],0x1
     *  004B7723   E8 28A5FFFF      CALL Sangokuh.004B1C50	; jichi: scenario caller
     *  004B7728   8D8424 84040000  LEA EAX,DWORD PTR SS:[ESP+0x484]
     *  004B772F   50               PUSH EAX
     *  004B7730   8D8C24 E8000000  LEA ECX,DWORD PTR SS:[ESP+0xE8]
     *
     *  Sample game: 戦極姫6
     *  004A6C88   CC               INT3
     *  004A6C89   CC               INT3
     *  004A6C8A   CC               INT3
     *  004A6C8B   CC               INT3
     *  004A6C8C   CC               INT3
     *  004A6C8D   CC               INT3
     *  004A6C8E   CC               INT3
     *  004A6C8F   CC               INT3
     *  004A6C90   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]
     *  004A6C96   8B5424 04        MOV EDX,DWORD PTR SS:[ESP+0x4]
     *  004A6C9A   56               PUSH ESI
     *  004A6C9B   33F6             XOR ESI,ESI
     *  004A6C9D   8038 00          CMP BYTE PTR DS:[EAX],0x0
     *  004A6CA0   74 1D            JE SHORT .004A6CBF
     *  004A6CA2   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]
     *  004A6CA8   8A00             MOV AL,BYTE PTR DS:[EAX]
     *  004A6CAA   8802             MOV BYTE PTR DS:[EDX],AL
     *  004A6CAC   FF81 14010000    INC DWORD PTR DS:[ECX+0x114]
     *  004A6CB2   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]
     *  004A6CB8   42               INC EDX
     *  004A6CB9   46               INC ESI
     *  004A6CBA   8038 00          CMP BYTE PTR DS:[EAX],0x0
     *  004A6CBD  ^75 E3            JNZ SHORT .004A6CA2
     *  004A6CBF   8B81 14010000    MOV EAX,DWORD PTR DS:[ECX+0x114]
     *  004A6CC5   8A00             MOV AL,BYTE PTR DS:[EAX]
     *  004A6CC7   8802             MOV BYTE PTR DS:[EDX],AL
     *  004A6CC9   FF81 14010000    INC DWORD PTR DS:[ECX+0x114]
     *  004A6CCF   8BC6             MOV EAX,ESI
     *  004A6CD1   5E               POP ESI
     *  004A6CD2   C2 0400          RETN 0x4
     *  004A6CD5   CC               INT3
     *  004A6CD6   CC               INT3
     *  004A6CD7   CC               INT3
     *  004A6CD8   CC               INT3
     *  004A6CD9   CC               INT3
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      ULONG beforeAddress;
      {
        const uint8_t bytes[] = {
            0x8b, 0x81, XX4,        // 004b1c50   8b81 14010000    mov eax,dword ptr ds:[ecx+0x114]	; jichi: source text in eax
            0x8b, 0x54, 0x24, 0x04, // 004b1c56   8b5424 04        mov edx,dword ptr ss:[esp+0x4]		; jichi: target address in edx
            0x56,                   // 004b1c5a   56               push esi
            0x33, 0xf6,             // 004b1c5b   33f6             xor esi,esi
            0x80, 0x38, 0x00        // 004b1c5d   8038 00          cmp byte ptr ds:[eax],0x0
        };
        beforeAddress = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
        if (!beforeAddress)
          return false;
      }

      ULONG afterAddress;
      {
        // 004B1C92   C2 0400          RETN 0x4 ; jichi: afterAddress
        // 004B1C95   CC               INT3
        DWORD bytes = 0xcc0004c2;
        afterAddress = MemDbg::findBytes(&bytes, sizeof(bytes), beforeAddress, stopAddress);
        if (!afterAddress || afterAddress - beforeAddress > 0x200) // should within 0x42
          return false;
      }

      // 004b1c50   8b81 14010000    mov eax,dword ptr ds:[ecx+0x114]	; jichi: source text in eax
      Private::textOffset_ = *(DWORD *)(beforeAddress + 2); // 0x114
      HookParam hp;
      hp.address = beforeAddress;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter2;
      hp.offset = stackoffset(1);
      hp.lineSeparator = L"\\n";
      hp.type = EMBED_ABLE | EMBED_DYNA_SJIS;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      auto suc = NewHook(hp, "EMbedUnicorn");
      hp.address = afterAddress;
      hp.text_fun = Private::hookAfter;
      suc |= NewHook(hp, "EMbedUnicorn");
      return suc;
    }

  } // namespace ScenarioHook

  namespace OtherHook
  {
    namespace Private
    {

      // bool isSkippedText(LPCSTR text)
      //{
      //   return 0 == ::strcmp(text, "\x82\x6c\x82\x72\x20\x83\x53\x83\x56\x83\x62\x83\x4e"); // "ＭＳ ゴシック"
      // }

      /**
       *  Sample game:  戦極姫6
       *
       */
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        static std::string data_;
        auto retaddr = s->stack[0];
        // 0052FDCE   83C4 0C          ADD ESP,0xC
        // 0052FDD1  ^EB C1            JMP SHORT .0052FD94
        // if (*(DWORD *)retaddr != 0xeb0cc483)
        //  return true;
        // retaddr = s->stack[7]; // parent caller

        // Scenario/name/other threads to skip:
        // - 0x404062 // there are so many other texts in this thread
        //
        // Other thread to keep:
        // - 0x4769f8: message
        // - 0x4135ba: in-game text that split into lines
        //
        // 004769E9   2BC7             SUB EAX,EDI
        // 004769EB   50               PUSH EAX
        // 004769EC   51               PUSH ECX
        // 004769ED   8D8E C4080000    LEA ECX,DWORD PTR DS:[ESI+0x8C4]
        // 004769F3   E8 B8D1F8FF      CALL .00403BB0   ; jichi; message
        // 004769F8   D9EE             FLDZ
        // 004769FA   8B6C24 18        MOV EBP,DWORD PTR SS:[ESP+0x18]
        // 004769FE   D996 04090000    FST DWORD PTR DS:[ESI+0x904]
        //
        // 004135B1   52               PUSH EDX
        // 004135B2   8D4E 3C          LEA ECX,DWORD PTR DS:[ESI+0x3C]
        // 004135B5   E8 F605FFFF      CALL .00403BB0   ; jichi: in-game caller
        // 004135BA   EB 08            JMP SHORT .004135C4
        // 004135BC   8D4E 3C          LEA ECX,DWORD PTR DS:[ESI+0x3C]
        // if (retaddr != 0x4769f8 && retaddr != 0x4135ba)
        //  return true;
        switch (*(WORD *)retaddr)
        {
        case 0xeed9: // 004769F8   D9EE             FLDZ
        case 0x08eb: // 004135BA   EB 08            JMP SHORT .004135C4
          break;
        default:
          return;
        }
        auto text = (LPCSTR)s->stack[1]; // arg1
        int size = s->stack[2];          // arg2
        if (!text || size <= 2           // avoid painting individual character
            || ::strlen(text) != size || all_ascii(text) || ScenarioHook::textCache_.exists(simplehash::hashCharArray(text)))
          //|| !q->isTextDecodable(text)) // avoid re-translation
          //|| isascii(text[::strlen(text) - 2])
          //|| isSkippedText(text))
          return;
        enum
        {
          role = Engine::OtherRole
        };
        buffer->from(text, size);
        /*    //oldData.replace("\\n", "\n"); // Remove new line. FIXME: automatically adjust line width
            std::string newData = EngineController::instance()->dispatchTextASTD(oldData, role, retaddr);
            if (newData == oldData)
              return true;
            data_ = newData;
            s->stack[1] = (ULONG)data_.c_str();
            s->stack[2] = data_.size();
            return true;*/
      }

      void hookafter(hook_context *s, TextBuffer buffer)
      {
        auto data_ = buffer.strA();
        s->stack[1] = (ULONG)allocateString(data_);
        s->stack[2] = data_.size();
      }
    } // namespace Private

    /**
     *  Sample game:  戦極姫6
     *  Function found by debugging caller of GetGlyphOutlineA.
     *  0052F2DC   CC               INT3
     *  0052F2DD   CC               INT3
     *  0052F2DE   CC               INT3
     *  0052F2DF   CC               INT3
     *  0052F2E0   55               PUSH EBP
     *  0052F2E1   8BEC             MOV EBP,ESP
     *  0052F2E3   57               PUSH EDI
     *  0052F2E4   56               PUSH ESI
     *  0052F2E5   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]  ; jichi: arg2, source text
     *  0052F2E8   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10] ; jichi: arg3, count?
     *  0052F2EB   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]  ; jichi: arg1, target location
     *  0052F2EE   8BC1             MOV EAX,ECX
     *  0052F2F0   8BD1             MOV EDX,ECX
     *  0052F2F2   03C6             ADD EAX,ESI
     *  0052F2F4   3BFE             CMP EDI,ESI
     *  0052F2F6   76 08            JBE SHORT .0052F300
     *  0052F2F8   3BF8             CMP EDI,EAX
     *  0052F2FA   0F82 A4010000    JB .0052F4A4
     *  0052F300   81F9 00010000    CMP ECX,0x100   ; jichi: 0x100 is the threshold
     *  0052F306   72 1F            JB SHORT .0052F327
     *  0052F308   833D 6472D800 00 CMP DWORD PTR DS:[0xD87264],0x0
     *  0052F30F   74 16            JE SHORT .0052F327
     *  0052F311   57               PUSH EDI
     *  0052F312   56               PUSH ESI
     *  0052F313   83E7 0F          AND EDI,0xF
     *  0052F316   83E6 0F          AND ESI,0xF
     *  0052F319   3BFE             CMP EDI,ESI
     *  0052F31B   5E               POP ESI
     *  0052F31C   5F               POP EDI
     *  0052F31D   75 08            JNZ SHORT .0052F327
     *  0052F31F   5E               POP ESI
     *  0052F320   5F               POP EDI
     *  0052F321   5D               POP EBP
     *  0052F322   E9 7C5F0000      JMP .005352A3
     *  0052F327   F7C7 03000000    TEST EDI,0x3
     *  0052F32D   75 15            JNZ SHORT .0052F344
     *  0052F32F   C1E9 02          SHR ECX,0x2
     *  0052F332   83E2 03          AND EDX,0x3
     *  0052F335   83F9 08          CMP ECX,0x8
     *  0052F338   72 2A            JB SHORT .0052F364
     *  0052F33A   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
     *  0052F33C   FF2495 54F45200  JMP DWORD PTR DS:[EDX*4+0x52F454]
     *  0052F343   90               NOP
     *
     *  Here's its parent parent caller:
     *  - arg1: jichi: source text
     *  - arg2: jichi: source size
     *
     *  00403BAB   CC               INT3
     *  00403BAC   CC               INT3
     *  00403BAD   CC               INT3
     *  00403BAE   CC               INT3
     *  00403BAF   CC               INT3
     *  00403BB0   55               PUSH EBP
     *  00403BB1   8B6C24 08        MOV EBP,DWORD PTR SS:[ESP+0x8]
     *  00403BB5   56               PUSH ESI
     *  00403BB6   57               PUSH EDI
     *  00403BB7   8BF1             MOV ESI,ECX
     *  00403BB9   85ED             TEST EBP,EBP
     *  00403BBB   74 46            JE SHORT .00403C03
     *  00403BBD   8B56 18          MOV EDX,DWORD PTR DS:[ESI+0x18]
     *  00403BC0   8D46 04          LEA EAX,DWORD PTR DS:[ESI+0x4]
     *  00403BC3   83FA 10          CMP EDX,0x10
     *  00403BC6   72 04            JB SHORT .00403BCC
     *  00403BC8   8B08             MOV ECX,DWORD PTR DS:[EAX]
     *  00403BCA   EB 02            JMP SHORT .00403BCE
     *  00403BCC   8BC8             MOV ECX,EAX
     *  00403BCE   3BE9             CMP EBP,ECX
     *  00403BD0   72 31            JB SHORT .00403C03
     *  00403BD2   83FA 10          CMP EDX,0x10
     *  00403BD5   72 04            JB SHORT .00403BDB
     *  00403BD7   8B08             MOV ECX,DWORD PTR DS:[EAX]
     *  00403BD9   EB 02            JMP SHORT .00403BDD
     *  00403BDB   8BC8             MOV ECX,EAX
     *  00403BDD   8B7E 14          MOV EDI,DWORD PTR DS:[ESI+0x14]
     *  00403BE0   03F9             ADD EDI,ECX
     *  00403BE2   3BFD             CMP EDI,EBP
     *  00403BE4   76 1D            JBE SHORT .00403C03
     *  00403BE6   83FA 10          CMP EDX,0x10
     *  00403BE9   72 02            JB SHORT .00403BED
     *  00403BEB   8B00             MOV EAX,DWORD PTR DS:[EAX]
     *  00403BED   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
     *  00403BF1   51               PUSH ECX
     *  00403BF2   2BE8             SUB EBP,EAX
     *  00403BF4   55               PUSH EBP
     *  00403BF5   56               PUSH ESI
     *  00403BF6   8BCE             MOV ECX,ESI
     *  00403BF8   E8 D3FEFFFF      CALL .00403AD0
     *  00403BFD   5F               POP EDI
     *  00403BFE   5E               POP ESI
     *  00403BFF   5D               POP EBP
     *  00403C00   C2 0800          RETN 0x8
     *  00403C03   8B7C24 14        MOV EDI,DWORD PTR SS:[ESP+0x14]
     *  00403C07   83FF FE          CMP EDI,-0x2
     *  00403C0A   76 05            JBE SHORT .00403C11
     *  00403C0C   E8 B94F1500      CALL .00558BCA
     *  00403C11   8B46 18          MOV EAX,DWORD PTR DS:[ESI+0x18]
     *  00403C14   3BC7             CMP EAX,EDI
     *  00403C16   73 20            JNB SHORT .00403C38
     *  00403C18   8B56 14          MOV EDX,DWORD PTR DS:[ESI+0x14]
     *  00403C1B   52               PUSH EDX
     *  00403C1C   57               PUSH EDI
     *  00403C1D   8BCE             MOV ECX,ESI
     *  00403C1F   E8 5CFDFFFF      CALL .00403980
     *  00403C24   85FF             TEST EDI,EDI
     *  00403C26   76 56            JBE SHORT .00403C7E
     *  00403C28   8B4E 18          MOV ECX,DWORD PTR DS:[ESI+0x18]
     *  00403C2B   53               PUSH EBX
     *  00403C2C   8D5E 04          LEA EBX,DWORD PTR DS:[ESI+0x4]
     *  00403C2F   83F9 10          CMP ECX,0x10
     *  00403C32   72 2C            JB SHORT .00403C60
     *  00403C34   8B03             MOV EAX,DWORD PTR DS:[EBX]
     *  00403C36   EB 2A            JMP SHORT .00403C62
     *  00403C38   85FF             TEST EDI,EDI
     *  00403C3A  ^75 EA            JNZ SHORT .00403C26
     *  00403C3C   897E 14          MOV DWORD PTR DS:[ESI+0x14],EDI
     *  00403C3F   83F8 10          CMP EAX,0x10
     *  00403C42   72 0E            JB SHORT .00403C52
     *  00403C44   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
     *  00403C47   5F               POP EDI
     *  00403C48   C600 00          MOV BYTE PTR DS:[EAX],0x0
     *  00403C4B   8BC6             MOV EAX,ESI
     *  00403C4D   5E               POP ESI
     *  00403C4E   5D               POP EBP
     *  00403C4F   C2 0800          RETN 0x8
     *  00403C52   8D46 04          LEA EAX,DWORD PTR DS:[ESI+0x4]
     *  00403C55   5F               POP EDI
     *  00403C56   C600 00          MOV BYTE PTR DS:[EAX],0x0
     *  00403C59   8BC6             MOV EAX,ESI
     *  00403C5B   5E               POP ESI
     *  00403C5C   5D               POP EBP
     *  00403C5D   C2 0800          RETN 0x8
     *  00403C60   8BC3             MOV EAX,EBX
     *  00403C62   57               PUSH EDI
     *  00403C63   55               PUSH EBP
     *  00403C64   51               PUSH ECX
     *  00403C65   50               PUSH EAX
     *  00403C66   E8 19C11200      CALL .0052FD84  ; jichi: actual paint function
     *  00403C6B   83C4 10          ADD ESP,0x10
     *  00403C6E   837E 18 10       CMP DWORD PTR DS:[ESI+0x18],0x10
     *  00403C72   897E 14          MOV DWORD PTR DS:[ESI+0x14],EDI
     *  00403C75   72 02            JB SHORT .00403C79
     *  00403C77   8B1B             MOV EBX,DWORD PTR DS:[EBX]
     *  00403C79   C6043B 00        MOV BYTE PTR DS:[EBX+EDI],0x0
     *  00403C7D   5B               POP EBX
     *  00403C7E   5F               POP EDI
     *  00403C7F   8BC6             MOV EAX,ESI
     *  00403C81   5E               POP ESI
     *  00403C82   5D               POP EBP
     *  00403C83   C2 0800          RETN 0x8
     *  00403C86   CC               INT3
     *  00403C87   CC               INT3
     *  00403C88   CC               INT3
     *  00403C89   CC               INT3
     *  00403C8A   CC               INT3
     *  00403C8B   CC               INT3
     *
     *  08BCF938   00403C6B  RETURN to .00403C6B from .0052FD84
     *  08BCF93C   088DC7F0   ; jichi: target location
     *  08BCF940   0000001F   ; jichi: target capacity
     *  08BCF944   08BCFC68   ; jichi: source size
     *  08BCF948   00000010   ; jichi: source size
     *  08BCF94C   00000001
     *  08BCF950   08BCFC69
     *  08BCF954   08BCFC68
     *  08BCF958   0000000F
     *  08BCF95C   00404870  RETURN to .00404870 from .00403BB0
     *  08BCF960   08BCFC68   ; jichi: source text
     *  08BCF964   00000010   ; jichi: source size
     *  08BCF968   0000000F   ; jichi: extra capacity
     *  08BCF96C   008B68F8  .008B68F8
     *  08BCF970   004AC441  RETURN to .004AC441 from .00404850
     *  08BCF974   08BCFC68
     *  08BCF978   2AE30C3B
     *  08BCF97C   004A5710  .004A5710
     *  08BCF980   088D5448
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x72, 0x0E,       // 00403C42   72 0E            JB SHORT .00403C52
          0x8B, 0x46, 0x04, // 00403C44   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
          0x5F,             // 00403C47   5F               POP EDI
          0xC6, 0x00, 0x00, // 00403C48   C600 00          MOV BYTE PTR DS:[EAX],0x0
          0x8B, 0xC6,       // 00403C4B   8BC6             MOV EAX,ESI
          0x5E,             // 00403C4D   5E               POP ESI
          0x5D,             // 00403C4E   5D               POP EBP
          0xC2, 0x08, 0x00  // 00403C4F   C2 0800          RETN 0x8
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      // addr = 0x00403BB0;
      HookParam hp;
      hp.address = addr;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
      hp.lineSeparator = L"\\n";
      hp.embed_hook_font = F_GetGlyphOutlineA;
      return NewHook(hp, "EMbedUnicornOther");
    }

  } // namespace OtherHook
} // unnamed namespace
bool Unicorn::attach_function()
{
  auto embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  if (embed)
  {
    OtherHook::attach(processStartAddress, processStopAddress);
  }
  return InsertUnicornHook() || embed;
}

bool Unicorn_Anesen::attach_function()
{
  //[060908][あねせん] あまからツインズ～双姉といっしょ～
  //[071012][あねせん] おしえて巫女先生弐
  //[071214][あねせん] おしえて巫女先生弐 外伝～ハーレム編～
  const BYTE bytes[] = {
      0x83, 0xFF, 0x20,
      XX2,
      0x0F, 0x84, XX4,
      0x81, 0xFF, 0x40, 0x81, 0x00, 0x00,
      0x0F, 0x84};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;

  HookParam hp;
  hp.type = USING_STRING;
  hp.offset = stackoffset(4);
  hp.address = addr;

  return NewHook(hp, "Unicorn_Anesen");
}