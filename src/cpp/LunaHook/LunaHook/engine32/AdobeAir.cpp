#include "AdobeAir.h"

/**
 *  jichi 4/15/2014: Insert Adobe AIR hook
 *  Sample games:
 *  華アワセ 蛟編: /HW-C*0:D8@4D04B5:Adobe AIR.dll
 *  華アワセ 姫空木編: /HW-C*0:d8@4E69A7:Adobe AIR.dll
 *
 *  Issue: The game will hang if the hook is injected before loading
 *
 *  /HW-C*0:D8@4D04B5:ADOBE AIR.DLL
 *  - addr: 5047477 = 0x4d04b5
 *  -length_offset: 1
 *  - module: 3506957663 = 0xd107ed5f
 *  - off: 4294967280 = 0xfffffff0 = -0x10
 *  - split: 216 = 0xd8
 *  - type: 90 = 0x5a
 *
 *  0f8f0497  |. eb 69         jmp short adobe_ai.0f8f0502
 *  0f8f0499  |> 83c8 ff       or eax,0xffffffff
 *  0f8f049c  |. eb 67         jmp short adobe_ai.0f8f0505
 *  0f8f049e  |> 8b7d 0c       mov edi,dword ptr ss:[ebp+0xc]
 *  0f8f04a1  |. 85ff          test edi,edi
 *  0f8f04a3  |. 7e 5d         jle short adobe_ai.0f8f0502
 *  0f8f04a5  |. 8b55 08       mov edx,dword ptr ss:[ebp+0x8]
 *  0f8f04a8  |. b8 80000000   mov eax,0x80
 *  0f8f04ad  |. be ff030000   mov esi,0x3ff
 *  0f8f04b2  |> 0fb70a        /movzx ecx,word ptr ds:[edx]
 *  0f8f04b5  |. 8bd8          |mov ebx,eax ; jichi: hook here
 *  0f8f04b7  |. 4f            |dec edi
 *  0f8f04b8  |. 66:3bcb       |cmp cx,bx
 *  0f8f04bb  |. 73 05         |jnb short adobe_ai.0f8f04c2
 *  0f8f04bd  |. ff45 fc       |inc dword ptr ss:[ebp-0x4]
 *  0f8f04c0  |. eb 3a         |jmp short adobe_ai.0f8f04fc
 *  0f8f04c2  |> bb 00080000   |mov ebx,0x800
 *  0f8f04c7  |. 66:3bcb       |cmp cx,bx
 *  0f8f04ca  |. 73 06         |jnb short adobe_ai.0f8f04d2
 *  0f8f04cc  |. 8345 fc 02    |add dword ptr ss:[ebp-0x4],0x2
 *  0f8f04d0  |. eb 2a         |jmp short adobe_ai.0f8f04fc
 *  0f8f04d2  |> 81c1 00280000 |add ecx,0x2800
 *  0f8f04d8  |. 8bde          |mov ebx,esi
 *  0f8f04da  |. 66:3bcb       |cmp cx,bx
 *  0f8f04dd  |. 77 19         |ja short adobe_ai.0f8f04f8
 *  0f8f04df  |. 4f            |dec edi
 *  0f8f04e0  |.^78 b7         |js short adobe_ai.0f8f0499
 *  0f8f04e2  |. 42            |inc edx
 *  0f8f04e3  |. 42            |inc edx
 *  0f8f04e4  |. 0fb70a        |movzx ecx,word ptr ds:[edx]
 *  0f8f04e7  |. 81c1 00240000 |add ecx,0x2400
 *  0f8f04ed  |. 66:3bcb       |cmp cx,bx
 *  0f8f04f0  |. 77 06         |ja short adobe_ai.0f8f04f8
 *  0f8f04f2  |. 8345 fc 04    |add dword ptr ss:[ebp-0x4],0x4
 *  0f8f04f6  |. eb 04         |jmp short adobe_ai.0f8f04fc
 *  0f8f04f8  |> 8345 fc 03    |add dword ptr ss:[ebp-0x4],0x3
 *  0f8f04fc  |> 42            |inc edx
 *  0f8f04fd  |. 42            |inc edx
 *  0f8f04fe  |. 85ff          |test edi,edi
 *  0f8f0500  |.^7f b0         \jg short adobe_ai.0f8f04b2
 *  0f8f0502  |> 8b45 fc       mov eax,dword ptr ss:[ebp-0x4]
 *  0f8f0505  |> 5f            pop edi
 *  0f8f0506  |. 5e            pop esi
 *  0f8f0507  |. 5b            pop ebx
 *  0f8f0508  |. c9            leave
 *  0f8f0509  \. c3            retn
 */
bool InsertAdobeAirHook()
{
  DWORD base = (DWORD)GetModuleHandleW(L"Adobe AIR.dll");
  if (!base)
  {
    return false;
  }

  // ULONG processStartAddress, processStopAddress;
  // if (!NtInspect::getModuleMemoryRange(L"Adobe AIR.dll", &startAddress, &stopAddress)) {
  //   ConsoleOutput("Adobe AIR: module not found");
  //   return false;
  // }

  const BYTE bytes[] = {
      0x0f, 0xb7, 0x0a, // 0f8f04b2  |> 0fb70a        /movzx ecx,word ptr ds:[edx]
      0x8b, 0xd8,       // 0f8f04b5  |. 8bd8          |mov ebx,eax ; jichi: hook here
      0x4f,             // 0f8f04b7  |. 4f            |dec edi
      0x66, 0x3b, 0xcb, // 0f8f04b8  |. 66:3bcb       |cmp cx,bx
      0x73, 0x05,       // 0f8f04bb  |. 73 05         |jnb short adobe_ai.0f8f04c2
      0xff, 0x45, 0xfc, // 0f8f04bd  |. ff45 fc       |inc dword ptr ss:[ebp-0x4]
      0xeb, 0x3a        // 0f8f04c0  |. eb 3a         |jmp short adobe_ai.0f8f04fc
  };
  enum
  {
    addr_offset = 0x0f8f04b5 - 0x0f8f04b2
  }; // = 3. 0 also works.
  enum
  {
    range = 0x600000
  }; // larger than relative addresses
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), base, base + range);
  // GROWL(reladdr);
  if (!addr)
  {
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  // hp.module = module;
  hp.offset = regoffset(edx);
  hp.split = 0xd8;
  // hp.type = USING_SPLIT|MODULE_OFFSET|CODEC_UTF16|DATA_INDIRECT; // 0x5a;
  hp.type = USING_SPLIT | CODEC_UTF16 | DATA_INDIRECT;

  if (NewHook(hp, "Adobe AIR"))
    return true;
  hp.type |= BREAK_POINT;
  return NewHook(hp, "Adobe AIR");
}

bool AdobeAIRhook2()
{
  auto hmodule = (DWORD)GetModuleHandle(L"Adobe AIR.dll");
  if (hmodule == 0)
    return false;
  enum
  {
    range = 0x600000
  }; // larger than relative addresses

  auto [minAddress, maxAddress] = std::make_pair(hmodule, hmodule + range);
  const BYTE bs[] = {
      // トリック・オア・アリス
      0x66, 0x83, 0xF8, 0x19,
      0x77, XX,
      0x81, 0xC7, 0xE0, 0xFF, 0x00, 0x00};
  auto addr = MemDbg::findBytes(bs, sizeof(bs), minAddress, maxAddress);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  const BYTE start[] = {0xC2, 0x10, 0x00}; // retn    10h，+3
  addr = reverseFindBytes(start, 3, addr - 0x1000, addr);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 3;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | CODEC_UTF16;

  return NewHook(hp, "AdobeAIR");
}

/**
 *  Artikash 12/8/2018: Update AIRNovel hook for version 31.0.0.96
 *  Sample game: https://vndb.org/v22252: /HQ4*8:4*4@12FF9A:Adobe AIR.dll
 *  This function is called from Adobe AIR.FREGetObjectAsUTF8+5A
 *  First function parameter points to a struct containing a pointer to the text along with info about the type of text
 *  wchar_t* at offset 8
 */
bool InsertAIRNovelHook()
{
  wcscpy_s(spDefault.boundaryModule, L"Adobe AIR.dll");
  if (DWORD FREGetObjectAsUTF8 = (DWORD)GetProcAddress(GetModuleHandleW(L"Adobe AIR.dll"), "FREGetObjectAsUTF8"))
  {
    DWORD func = FREGetObjectAsUTF8 + 0x5a + 5 + *(int *)(FREGetObjectAsUTF8 + 0x5b);
    HookParam hp;
    hp.address = func;
    hp.type = CODEC_UTF16 | USING_STRING /*|USING_SPLIT|SPLIT_INDIRECT*/ | DATA_INDIRECT; // Artikash 12/14/2018: doesn't seem to be a good split anymore
    hp.offset = stackoffset(1);
    hp.split = stackoffset(1);
    hp.index = 0x8;
    hp.split_index = 0x4;
    // hp.filter_fun = [](void* str, DWORD* len, HookParam* hp, BYTE index)  // removes some of the garbage threads
    //{
    //	return *len < 4 &&
    //		*(char*)str != '[' &&
    //		*(char*)str != ';' &&
    //		*(char*)str != '&' &&
    //		*(char*)str != '*' &&
    //		*(char*)str != '\n' &&
    //		*(char*)str != '\t' &&
    //		memcmp((char*)str, "app:/", 5);
    // };

    ConsoleOutput("INSERT AIRNovel");

    return NewHook(hp, "AIRNovel");
  }
  return false;
}
bool adobelair3()
{
  // 虚構英雄ジンガイアVol3
  DWORD base = (DWORD)GetModuleHandleW(L"Adobe AIR.dll");
  if (!base)
    return false;
  BYTE sig[] = {
      0x8b, 0x85, XX4,
      0x8B, 0x4E, 0x04,
      0x85, 0xC9,
      0x0F, 0x85, XX4,
      0xFF, 0x70, 0x14,
      0x8B, 0x78, 0x0c,
      0x8b, 0xcf,
      0x68, 0xb8, 0x00, 0x00, 0x00,
      0xff, 0x15, XX4,
      0xff, 0xd7,
      0x8b, 0xc8,
      0x83, 0xc4, 0x08,
      0x85, 0xc9,
      0x0f, 0x85, XX4};
  enum
  {
    range = 0x600000
  }; // larger than relative addresses
  auto [minAddress, maxAddress] = std::make_pair(base, base + range);
  auto addr = MemDbg::findBytes(sig, sizeof(sig), minAddress, maxAddress);
  HookParam hp;
  hp.address = addr;
  hp.type = CODEC_UTF8 | USING_STRING | NO_CONTEXT;
  hp.offset = stackoffset(1);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    // 若当前还有5个字符，则这个句子会显示5次，然后substr(1,len-1)，直到结束，总共显示5+4+3+2+1次
    auto ws = buffer->strAW(CP_UTF8);
    static int leng = 0;
    if (ws.length() <= leng)
    {
      leng = ws.length();
      return buffer->clear();
    }
    leng = ws.length();
  };
  return NewHook(hp, "AIRNovel");
}
bool AdobeAir::attach_function()
{

  bool b1 = InsertAdobeAirHook();
  b1 |= AdobeAIRhook2();
  b1 |= adobelair3();
  b1 = b1 || InsertAIRNovelHook(); // 乱码太多了这个
  return b1;
}