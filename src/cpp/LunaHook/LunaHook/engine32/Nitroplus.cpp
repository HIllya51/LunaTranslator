#include "Nitroplus.h"

bool InsertNitroplusHook()
{
	const BYTE bytes[] = {0xb0, 0x74, 0x53};
	DWORD addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
	{
		ConsoleOutput("Nitroplus: pattern not exist");
		return false;
	}
	enum : WORD
	{
		sub_esp = 0xec83
	}; // caller pattern: sub esp = 0x83,0xec
	BYTE b = *(BYTE *)(addr + 3) & 3;
	while (*(WORD *)addr != sub_esp)
		addr--;
	HookParam hp;
	hp.address = addr;
	hp.offset = -0x14 + (b << 2);
	hp.type = CODEC_ANSI_BE;
	ConsoleOutput("INSERT Nitroplus");
	return NewHook(hp, "Nitroplus");
	// RegisterEngineType(ENGINE_Nitroplus);
}
bool InsertNitroplus2Hook()
{

	/*
	 * Sample games:
	 * https://vndb.org/v428
	 */
	BYTE bytes[] = {
		0x8D, 0xB4, 0x29, XX4, // lea esi,[ecx+ebp+0000415C]
		0x74, 0x20,			   // je Django.exe+6126E
		0x8D, 0xBC, 0xBD, XX4, // lea edi,[ebp+edi*4+0006410C]
		0x8B, 0x56, 0xB0,	   // mov edx,[esi-50]
		0xE8, XX4			   // call Django.exe+51150      << hook here
	};
	enum
	{
		addr_offset = sizeof(bytes) - 5
	};
	ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
	{
		ConsoleOutput("Nitroplus2: pattern not found");
		return false;
	}
	HookParam hp;
	hp.address = addr + addr_offset;
	hp.offset = regoffset(edx);
	hp.type = CODEC_ANSI_BE;
	return NewHook(hp, "Nitroplus2");
}
namespace
{
	//	DRAMAtical Murder re:connect 普及版
	// https://vndb.org/v10895
	bool dmmdrc()
	{
		// BYTE sig[]={
		// 	0xc7,0x04,0x24,0x24,0x53,0x59,0x53,//$SYS
		// 	0xc7,0x44,0x24,0x04,0x54,0x45,0x4d,0x5f,//TEM_
		// 	0xc7,0x44,0x24,0x08,0x6c,0x61,0x73,0x74,//last
		// 	0xc7,0x44,0x24,0x0c,0x5f,0x74,0x65,0x78,//_tex
		// };
		BYTE sig[] = {
			0x8d, 0x89, XX4,
			0x8b, 0xc2,
			0xc1, 0xe8, 0x08,
			0x88, 0x01,
			0x88, 0x51, 0x01,
			0xc6, 0x41, 0x02, 0x00};
		ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = *(DWORD *)(addr + 2);
		hp.type = DIRECT_READ;
		auto succ = NewHook(hp, "dmmdrc");

		BYTE sig2[] = {
			0x68, 0x00, 0x02, 0x00, 0x00,
			0xba, XX4,
			0xe8, XX4};
		memcpy(sig2 + 6, (void *)(addr + 2), 4);
		addr = MemDbg::findBytes(sig2, sizeof(sig2), addr, addr + 0x100);
		if (addr)
		{
			HookParam hp;
			hp.address = addr + sizeof(sig2);
			hp.type = USING_STRING;
			hp.user_value = 0;
			hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
			{
				auto data = context->edx;
				auto l = strlen((char *)data);
				if (hp->user_value > l)
					hp->user_value = 0;
				data += hp->user_value;
				auto len = l - hp->user_value;
				hp->user_value = l;
				buffer->from(data, len);
			};
			succ |= NewHook(hp, "dmmdrc2");
		}
		return succ;
	}
}
namespace
{
	// https://vndb.org/v7738
	// 君と彼女と彼女の恋。
	/*
int __fastcall sub_477820(int a1)
{
  int result; // eax
  __m64 *v2; // eax
  unsigned int v3; // eax
  char *v4; // eax
  _BYTE *v5; // eax
  _WORD v6[11]; // [esp+4h] [ebp-20h] BYREF
  int v7; // [esp+1Ah] [ebp-Ah]
  int v8; // [esp+1Eh] [ebp-6h]
  __int16 v9; // [esp+22h] [ebp-2h]

  result = 0;
  strcpy((char *)v6, "$SYSTEM_last_text");
  *(_DWORD *)&v6[9] = 0;
  v7 = 0;
  v8 = 0;
  v9 = 0;
  if ( dword_61A3B0 != 400 )
  {
	if ( a1 )
	{
	  v3 = strlen(byte_5ADB30);
	  if ( v3 < 0x1F8 )
	  {
		if ( (a1 & 0xFF00) != 0 )
		{
		  v4 = &byte_5ADB30[v3];
		  *v4 = BYTE1(a1);
		  v4[1] = a1;
		  v4[2] = 0;
		}
		else if ( a1 == 2162721 || a1 == 2162751 || a1 == 4128801 || a1 == 4128831 )
		{
		  byte_5ADB30[v3] = BYTE2(a1);
		  byte_5ADB31[v3] = a1;
		  byte_5ADB32[v3] = 0;
		}
		else
		{
		  byte_5ADB30[v3] = a1;
		  byte_5ADB31[v3] = 0;
		}
		v5 = (_BYTE *)dword_623804;
		if ( dword_623804 || (v5 = (_BYTE *)sub_468060(v6)) != 0 )
		{
		  *v5 = 1;
		  sub_471390(v5 + 152, byte_5ADB30, 512);
		}
	  }
	}
	else
	{
	  byte_5ADB30[0] = 0;
	  v2 = (__m64 *)sub_468060(v6);
	  if ( v2 )
	  {
		v2->m64_i8[0] = 1;
		sub_471320(v2 + 19, 1024);
		return 1;
	  }
	}
	return 1;
  }
  return result;
}
*/
#define BYTEn(x, n) (*((BYTE *)&(x) + n))
#define BYTE1(x) BYTEn(x, 1)
#define BYTE2(x) BYTEn(x, 2)
	bool totono()
	{
		BYTE sig[] = {
			0X81, 0XF9, 0X21, 0X00, 0X21, 0X00,
			0X74, XX,
			0X81, 0XF9, 0X3F, 0X00, 0X21, 0X00,
			0X74, XX,
			0X81, 0XF9, 0X21, 0X00, 0X3F, 0X00,
			0X74, XX,
			0X81, 0XF9, 0X3F, 0X00, 0X3F, 0X00,
			0X74, XX};
		BYTE sig2[] = {
			0XC7, 0X44, 0X24, 0X04, 0X24, 0X53, 0X59, 0X53,
			0XC7, 0X44, 0X24, 0X08, 0X54, 0X45, 0X4D, 0X5F,
			0XC7, 0X44, 0X24, 0X0C, 0X6C, 0X61, 0X73, 0X74,
			0XC7, 0X44, 0X24, 0X10, 0X5F, 0X74, 0X65, 0X78};
		ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
		if (!addr)
			addr = MemDbg::findBytes(sig2, sizeof(sig2), processStartAddress, processStopAddress);
		if (!addr)
			return false;
		addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = addr;
		hp.type = USING_STRING | NO_CONTEXT;
		hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
		{
			auto a1 = context->ecx;
			if (!a1)
				return;
			if ((a1 & 0xFF00) != 0)
			{
				char v4[3];
				*v4 = BYTE1(a1);
				v4[1] = a1;
				v4[2] = 0;
				buffer->from(v4);
			}
			else if (a1 == 2162721 || a1 == 2162751 || a1 == 4128801 || a1 == 4128831)
			{
				char byte_5ADB30[3];
				byte_5ADB30[2] = 0;
				byte_5ADB30[0] = BYTE2(a1);
				byte_5ADB30[1] = a1;
				buffer->from(byte_5ADB30);
			}
			else
			{
				char byte_5ADB30[2];
				byte_5ADB30[1] = 0;
				byte_5ADB30[0] = a1;
				buffer->from(byte_5ADB30);
			}
		};
		return NewHook(hp, "Nitroplus3");
	}
}
bool Nitroplus::attach_function()
{
	return InsertNitroplusHook() || InsertNitroplus2Hook() || dmmdrc() || totono();
}

void NitroplusSysFilter(TextBuffer *buffer, HookParam *)
{
	auto text = reinterpret_cast<LPSTR>(buffer->buff);

	if (buffer->size <= 2)
		return buffer->clear();

	StringFilter(buffer, TEXTANDLEN("\x81@"));
	CharReplacer(buffer, '\r', ' ');
	if (cpp_strnstr(text, "<", buffer->size))
	{
		StringFilterBetween(buffer, TEXTANDLEN("<"), TEXTANDLEN(">"));
	}
	while (buffer->size > 1 && ::isspace(*text))
	{
		::memmove(text, text + 1, --buffer->size);
	}
}

bool InsertNitroplusSysHook()
{

	/*
	 * Sample games:
	 * https://vndb.org/r76679
	 */
	const BYTE bytes[] = {
		0x0F, 0x84, XX4,		// je system.dll+5B8CA        <- hook here
		0xEB, 0x04,				// jmp system.dll+5A791
		0x8B, 0x44, 0x24, 0x20, // mov eax,[esp+20]
		0x8B, 0x4C, 0x24, 0x24	// mov ecx,[esp+24]
	};

	HMODULE module = GetModuleHandleW(L"system.dll");
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
	if (!addr)
		return false;

	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(eax);
	hp.type = USING_STRING;
	hp.filter_fun = NitroplusSysFilter;
	return NewHook(hp, "NitroplusSystem");
}
bool Nitroplusplus::attach_function()
{
	return InsertNitroplusSysHook();
}