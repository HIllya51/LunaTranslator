/*
  yapi -- Yet Another Process Injector / Your API
  A fusion library that reduce differences between x64, wow64 and x86 processes based on rewolf-wow64ext.

  Copyright (c) 2010-2018 <http://ez8.co> <orca.zhang@yahoo.com>
  This library is released under the MIT License.

  Please see LICENSE file or visit https://github.com/ez8-co/yapi for details.
*/
#pragma once

#include <tchar.h>
#include <windows.h>
#include <vector>
#include <string>

#ifndef NT_SUCCESS
#define NT_SUCCESS(Status)			(((NTSTATUS)(Status)) >= 0)
#endif

#include <TlHelp32.h>

namespace detail {
	static HMODULE hNtDll = LoadLibrary(_T("ntdll.dll"));
	static HANDLE hCurProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, GetCurrentProcessId());

	BOOL Is64BitOS()
	{
		SYSTEM_INFO systemInfo = { 0 };
		GetNativeSystemInfo(&systemInfo);
		return systemInfo.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_AMD64
			|| systemInfo.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_IA64;
	}
	static const BOOL is64BitOS = Is64BitOS();

	struct GCBase
	{
		virtual DWORD64 toDWORD64() = 0;
		virtual void gc() = 0;
	};
	struct GCHelper
	{
		~GCHelper() {
			for (size_t i = 0; i < _ptrs.size(); i++) {
				_ptrs[i]->gc();
				delete _ptrs[i];
			}
		}
		DWORD64 add(GCBase* ptr) { _ptrs.push_back(ptr); return ptr->toDWORD64(); }
	private:
		std::vector<GCBase*> _ptrs;
	};
}

namespace yapi {

	typedef std::basic_string<TCHAR, std::char_traits<TCHAR>, std::allocator<TCHAR> > tstring;

	#ifndef UNICODE
		static std::string _W2T(const wchar_t* wcs)
		{
			int len = ::WideCharToMultiByte(CP_ACP, 0, wcs, -1, NULL, 0, 0, 0);
			std::string ret(len, 0);
			VERIFY(0 != ::WideCharToMultiByte(CP_ACP, 0, wcs, -1, &ret[0], len, 0, 0));
			ret.resize(len - 1);
			return ret;
		}
	#else
		#define _W2T(str) std::wstring(str)
	#endif

	#define REPEAT_0(macro) 
	#define REPEAT_1(macro) REPEAT_0(macro)
	#define REPEAT_2(macro) REPEAT_1(macro) macro(1)
	#define REPEAT_3(macro) REPEAT_2(macro) macro(2)
	#define REPEAT_4(macro) REPEAT_3(macro) macro(3)
	#define REPEAT_5(macro) REPEAT_4(macro) macro(4)
	#define REPEAT_6(macro) REPEAT_5(macro) macro(5)
	#define REPEAT_7(macro) REPEAT_6(macro) macro(6)
	#define REPEAT_8(macro) REPEAT_7(macro) macro(7)
	#define REPEAT_9(macro) REPEAT_8(macro) macro(8)
	#define REPEAT_10(macro) REPEAT_9(macro) macro(9)
	#define REPEAT_11(macro) REPEAT_10(macro) macro(10)
	#define REPEAT_12(macro) REPEAT_11(macro) macro(11)
	#define REPEAT_13(macro) REPEAT_12(macro) macro(12)
	#define REPEAT_14(macro) REPEAT_13(macro) macro(13)
	#define REPEAT_15(macro) REPEAT_14(macro) macro(14)
	#define REPEAT_16(macro) REPEAT_15(macro) macro(15)
	#define REPEAT_17(macro) REPEAT_16(macro) macro(16)
	#define REPEAT_18(macro) REPEAT_17(macro) macro(17)
	#define REPEAT_19(macro) REPEAT_18(macro) macro(18)
	#define REPEAT_20(macro) REPEAT_19(macro) macro(19)

	#define END_MACRO_0(macro) 
	#define END_MACRO_1(macro) macro(1)
	#define END_MACRO_2(macro) macro(2)
	#define END_MACRO_3(macro) macro(3)
	#define END_MACRO_4(macro) macro(4)
	#define END_MACRO_5(macro) macro(5)
	#define END_MACRO_6(macro) macro(6)
	#define END_MACRO_7(macro) macro(7)
	#define END_MACRO_8(macro) macro(8)
	#define END_MACRO_9(macro) macro(9)
	#define END_MACRO_10(macro) macro(10)
	#define END_MACRO_11(macro) macro(11)
	#define END_MACRO_12(macro) macro(12)
	#define END_MACRO_13(macro) macro(13)
	#define END_MACRO_14(macro) macro(14)
	#define END_MACRO_15(macro) macro(15)
	#define END_MACRO_16(macro) macro(16)
	#define END_MACRO_17(macro) macro(17)
	#define END_MACRO_18(macro) macro(18)
	#define END_MACRO_19(macro) macro(19)
	#define END_MACRO_20(macro) macro(20)

	#define REPEAT(n, macro, end_macro) REPEAT_##n (macro) END_MACRO_##n(end_macro)

	#define __ARG(n) P ## n
	#define __PARAM(n) p ## n
	#define __ARG_DECL(n) __ARG(n) __PARAM(n)

	#define TEMPLATE_ARG(n) typename __ARG(n)
	#define VOID_TEMPLATE_ARGS(n) typename __ARG(n),

	#define ARG_DECL(n) __ARG_DECL(n) ,
	#define END_ARG_DECL(n) __ARG_DECL(n)

	#define DECL_VOID_TEMPLATE_ARGS(n) REPEAT(n, VOID_TEMPLATE_ARGS, TEMPLATE_ARG)
	#define DECL_PARAMS_LIST(n) REPEAT(n, ARG_DECL, END_ARG_DECL)

	namespace {
		template <class T>
		struct _UNICODE_STRING_T {
			union {
				struct {
					WORD Length;
					WORD MaximumLength;
				};
				T dummy;
			};
			T Buffer;
		};

		template <typename T>
		struct _LIST_ENTRY_T {
			T Flink;
			T Blink;
		};

		template <typename T>
		struct _PEB_T {
			T dummy01;
			T Mutant;
			T ImageBaseAddress;
			T Ldr;
			// omit unused fields
		};

		typedef _PEB_T<DWORD>   PEB32;
		typedef _PEB_T<DWORD64> PEB64;

		typedef struct _PROCESS_BASIC_INFORMATION32 {
			NTSTATUS ExitStatus;
			UINT32 PebBaseAddress;
			UINT32 AffinityMask;
			UINT32 BasePriority;
			UINT32 UniqueProcessId;
			UINT32 InheritedFromUniqueProcessId;
		} PROCESS_BASIC_INFORMATION32;

		typedef struct _PROCESS_BASIC_INFORMATION64 {
			NTSTATUS ExitStatus;
			UINT32 Reserved0;
			UINT64 PebBaseAddress;
			UINT64 AffinityMask;
			UINT32 BasePriority;
			UINT32 Reserved1;
			UINT64 UniqueProcessId;
			UINT64 InheritedFromUniqueProcessId;
		} PROCESS_BASIC_INFORMATION64;

		template <class T>
		struct _PEB_LDR_DATA_T {
			DWORD Length;
			DWORD Initialized;
			T SsHandle;
			_LIST_ENTRY_T<T> InLoadOrderModuleList;
			// omit unused fields
		};

		typedef _PEB_LDR_DATA_T<DWORD>   PEB_LDR_DATA32;
		typedef _PEB_LDR_DATA_T<DWORD64> PEB_LDR_DATA64;

		template <class T>
		struct _LDR_DATA_TABLE_ENTRY_T {
			_LIST_ENTRY_T<T> InLoadOrderLinks;
			_LIST_ENTRY_T<T> InMemoryOrderLinks;
			_LIST_ENTRY_T<T> InInitializationOrderLinks;
			T DllBase;
			T EntryPoint;
			union {
				DWORD SizeOfImage;
				T dummy01;
			};
			_UNICODE_STRING_T<T> FullDllName;
			_UNICODE_STRING_T<T> BaseDllName;
			// omit unused fields
		};

		typedef _LDR_DATA_TABLE_ENTRY_T<DWORD>   LDR_DATA_TABLE_ENTRY32;
		typedef _LDR_DATA_TABLE_ENTRY_T<DWORD64> LDR_DATA_TABLE_ENTRY64;

		size_t tcslen(const char* str) { return strlen(str); }
		size_t tcslen(const wchar_t* str) { return wcslen(str); }
	}

	DWORD64 WINAPI GetProcAddress(HANDLE hProcess, DWORD64 hModule, const char* funcName);

	#ifdef _WIN64
		typedef NTSTATUS(WINAPI *NT_QUERY_INFORMATION_PROCESS)(
			HANDLE ProcessHandle, ULONG ProcessInformationClass,
			PVOID ProcessInformation, UINT32 ProcessInformationLength,
			UINT32 * ReturnLength);

		static NT_QUERY_INFORMATION_PROCESS NtWow64QueryInformationProcess64 = (NT_QUERY_INFORMATION_PROCESS)GetProcAddress((HMODULE)detail::hNtDll, "NtQueryInformationProcess");
		#define NtWow64ReadVirtualMemory64         ReadProcessMemory

	#else

		namespace {
			typedef NTSTATUS(WINAPI *NT_WOW64_QUERY_INFORMATION_PROCESS64)(
				HANDLE ProcessHandle, UINT32 ProcessInformationClass,
				PVOID ProcessInformation, UINT32 ProcessInformationLength,
				UINT32* ReturnLength);

			typedef NTSTATUS(WINAPI *NT_WOW64_READ_VIRTUAL_MEMORY64)(
				HANDLE ProcessHandle, PVOID64 BaseAddress,
				PVOID BufferData, UINT64 BufferLength,
				PUINT64 ReturnLength);

			static NT_WOW64_QUERY_INFORMATION_PROCESS64 NtWow64QueryInformationProcess64 = (NT_WOW64_QUERY_INFORMATION_PROCESS64)GetProcAddress((HMODULE)detail::hNtDll, "NtWow64QueryInformationProcess64");
			static NT_WOW64_READ_VIRTUAL_MEMORY64 NtWow64ReadVirtualMemory64 = (NT_WOW64_READ_VIRTUAL_MEMORY64)GetProcAddress((HMODULE)detail::hNtDll, "NtWow64ReadVirtualMemory64");
		}

	#endif

	DWORD64 WINAPI GetModuleHandle(HANDLE hProcess, const TCHAR* moduleName)
	{
		if (!moduleName) return 0;
		if (!hProcess) hProcess = detail::hCurProcess;

		HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, GetProcessId(hProcess));
		if (hSnap == INVALID_HANDLE_VALUE) return 0;
		MODULEENTRY32 mod = { sizeof(mod) };
		if (Module32First(hSnap, &mod)) {
			do {
				if (!_tcsicmp(mod.szModule, moduleName)) {
					CloseHandle(hSnap);
					return (DWORD64)mod.hModule;
				}
			} while (Module32Next(hSnap, &mod));
		}
		CloseHandle(hSnap);
		return 0;
	}

	DWORD64 WINAPI GetProcAddress(HANDLE hProcess, DWORD64 hModule, const char* funcName)
	{
		if (!hModule || !funcName) return 0;
		if (!hProcess) hProcess = detail::hCurProcess;

		IMAGE_DOS_HEADER idh;
		NTSTATUS status = ReadProcessMemory(hProcess, (PVOID)hModule, (PVOID)&idh, sizeof(idh), NULL);
		if (!NT_SUCCESS(status)) return 0;

		IMAGE_NT_HEADERS32 inh;
		status = ReadProcessMemory(hProcess, (PVOID)(hModule + idh.e_lfanew), (PVOID)&inh, sizeof(inh), NULL);
		if (!NT_SUCCESS(status)) return 0;

		IMAGE_DATA_DIRECTORY& idd = inh.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];
		if (!idd.VirtualAddress)return 0;

		IMAGE_EXPORT_DIRECTORY ied;
		status = ReadProcessMemory(hProcess, (PVOID)(hModule + idd.VirtualAddress), (PVOID)&ied, sizeof(ied), NULL);
		if (!NT_SUCCESS(status)) return 0;

		std::vector<DWORD> nameTable(ied.NumberOfNames);
		status = ReadProcessMemory(hProcess, (PVOID)(hModule + ied.AddressOfNames), (PVOID)&nameTable[0], sizeof(DWORD) * ied.NumberOfNames, NULL);
		if (!NT_SUCCESS(status)) return 0;

		for (DWORD i = 0; i < ied.NumberOfNames; ++i) {
			std::string func(strlen(funcName), 0);
			status = ReadProcessMemory(hProcess, (PVOID)(hModule + nameTable[i]), (PVOID)&func[0], strlen(funcName), NULL);
			if (!NT_SUCCESS(status)) continue;

			if (func == funcName) {
				WORD ord = 0;
				status = ReadProcessMemory(hProcess, (PVOID)(hModule + ied.AddressOfNameOrdinals + i * sizeof(WORD)), (PVOID)&ord, sizeof(WORD), NULL);
				if (!NT_SUCCESS(status)) continue;

				DWORD rva = 0;
				status = ReadProcessMemory(hProcess, (PVOID)(hModule + ied.AddressOfFunctions + ord * sizeof(DWORD)), (PVOID)&rva, sizeof(DWORD), NULL);
				if (!NT_SUCCESS(status)) continue;

				return hModule + rva;
			}
		}
		return 0;
	}

	DWORD64 WINAPI GetModuleHandle64(HANDLE hProcess, const TCHAR* moduleName)
	{
		if (!moduleName) return 0;
		if (!hProcess) hProcess = detail::hCurProcess;

	#ifndef _WIN64
		if (!NtWow64QueryInformationProcess64 || !NtWow64ReadVirtualMemory64) return 0;
	#endif

		PROCESS_BASIC_INFORMATION64 pbi = { 0 };
		const int ProcessBasicInformation = 0;
		NTSTATUS status = NtWow64QueryInformationProcess64(hProcess, ProcessBasicInformation, &pbi, sizeof(pbi), NULL);
		if (!NT_SUCCESS(status)) return 0;

		PEB64 peb;
		status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)pbi.PebBaseAddress, &peb, sizeof(peb), NULL);
		if (!NT_SUCCESS(status)) return 0;

		PEB_LDR_DATA64 ldr;
		status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)peb.Ldr, (PVOID)&ldr, sizeof(ldr), NULL);
		if (!NT_SUCCESS(status)) return 0;

		DWORD64 LastEntry = peb.Ldr + offsetof(PEB_LDR_DATA64, InLoadOrderModuleList);

		LDR_DATA_TABLE_ENTRY64 head;
		head.InLoadOrderLinks.Flink = ldr.InLoadOrderModuleList.Flink;
		do {
			status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)head.InLoadOrderLinks.Flink, (PVOID)&head, sizeof(head), NULL);
			if (!NT_SUCCESS(status)) continue;

			std::wstring modName((size_t)head.BaseDllName.MaximumLength, 0);
			status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)head.BaseDllName.Buffer, (PVOID)&modName[0], head.BaseDllName.MaximumLength, NULL);
			if (!NT_SUCCESS(status)) continue;

			if (!_tcsicmp(moduleName, _W2T(modName).c_str()))
				return head.DllBase;
		} while (head.InLoadOrderLinks.Flink != LastEntry);
		return 0;
	}

	DWORD64 WINAPI GetProcAddress64(HANDLE hProcess, DWORD64 hModule, const char* funcName)
	{
		if (!hModule || !funcName) return 0;
		if (!hProcess) hProcess = detail::hCurProcess;

#ifndef _WIN64
		if (!NtWow64ReadVirtualMemory64) return 0;
#endif

		IMAGE_DOS_HEADER idh;
		NTSTATUS status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)hModule, (PVOID)&idh, sizeof(idh), NULL);
		if (!NT_SUCCESS(status)) return 0;

		IMAGE_NT_HEADERS64 inh;
		status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)(hModule + idh.e_lfanew), (PVOID)&inh, sizeof(inh), NULL);
		if (!NT_SUCCESS(status)) return 0;

		IMAGE_DATA_DIRECTORY& idd = inh.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];
		if (!idd.VirtualAddress)return 0;

		IMAGE_EXPORT_DIRECTORY ied;
		status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)(hModule + idd.VirtualAddress), (PVOID)&ied, sizeof(ied), NULL);
		if (!NT_SUCCESS(status)) return 0;

		std::vector<DWORD> nameTable(ied.NumberOfNames);
		status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)(hModule + ied.AddressOfNames), (PVOID)&nameTable[0], sizeof(DWORD) * ied.NumberOfNames, NULL);
		if (!NT_SUCCESS(status)) return 0;

		for (DWORD i = 0; i < ied.NumberOfNames; ++i) {
			std::string func(strlen(funcName), 0);
			status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)(hModule + nameTable[i]), (PVOID)&func[0], strlen(funcName), NULL);
			if (!NT_SUCCESS(status)) continue;

			if (func == funcName) {
				WORD ord = 0;
				status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)(hModule + ied.AddressOfNameOrdinals + i * sizeof(WORD)), (PVOID)&ord, sizeof(WORD), NULL);
				if (!NT_SUCCESS(status)) continue;

				DWORD rva = 0;
				status = NtWow64ReadVirtualMemory64(hProcess, (PVOID64)(hModule + ied.AddressOfFunctions + ord * sizeof(DWORD)), (PVOID)&rva, sizeof(DWORD), NULL);
				if (!NT_SUCCESS(status)) continue;

				return hModule + rva;
			}
		}
		return 0;
	}

	DWORD64 GetNtDll64()
    {
		static DWORD64 hNtdll64 = 0;
		if(hNtdll64) return hNtdll64;
		hNtdll64 = GetModuleHandle64(detail::hCurProcess, _T("ntdll.dll"));
		return hNtdll64;
	}

	#ifdef _WIN64

		#define SetLastError64       SetLastError
		#define VirtualQueryEx64     VirtualQueryEx
		#define VirtualAllocEx64     VirtualAllocEx
		#define VirtualFreeEx64      VirtualFreeEx
		#define VirtualProtectEx64   VirtualProtectEx
		#define ReadProcessMemory64  ReadProcessMemory
		#define WriteProcessMemory64 WriteProcessMemory
		#define LoadLibrary64        LoadLibrary
		#define CreateRemoteThread64 CreateRemoteThread

	#else

		namespace {
			#define _(x) __asm __emit (x)
			__declspec(naked) DWORD64 x64Call(DWORD64 func, int argC, ...)
			{
				// see X64Call_disassemble for details
				_(0x55)_(0x8b)_(0xec)_(0x8b)_(0x4d)_(0x10)_(0x8d)_(0x55)_(0x14)_(0x83)_(0xec)_(0x40)_(0x53)_(0x56)_(0x57)_(0x85)
				_(0xc9)_(0x7e)_(0x15)_(0x8b)_(0x45)_(0x14)_(0x8d)_(0x55)_(0x1c)_(0x49)_(0x89)_(0x45)_(0xf0)_(0x8b)_(0x45)_(0x18)
				_(0x89)_(0x4d)_(0x10)_(0x89)_(0x45)_(0xf4)_(0xeb)_(0x08)_(0x0f)_(0x57)_(0xc0)_(0x66)_(0x0f)_(0x13)_(0x45)_(0xf0)
				_(0x85)_(0xc9)_(0x7e)_(0x15)_(0x49)_(0x83)_(0xc2)_(0x08)_(0x89)_(0x4d)_(0x10)_(0x8b)_(0x42)_(0xf8)_(0x89)_(0x45)
				_(0xe8)_(0x8b)_(0x42)_(0xfc)_(0x89)_(0x45)_(0xec)_(0xeb)_(0x08)_(0x0f)_(0x57)_(0xc0)_(0x66)_(0x0f)_(0x13)_(0x45)
				_(0xe8)_(0x85)_(0xc9)_(0x7e)_(0x15)_(0x49)_(0x83)_(0xc2)_(0x08)_(0x89)_(0x4d)_(0x10)_(0x8b)_(0x42)_(0xf8)_(0x89)
				_(0x45)_(0xe0)_(0x8b)_(0x42)_(0xfc)_(0x89)_(0x45)_(0xe4)_(0xeb)_(0x08)_(0x0f)_(0x57)_(0xc0)_(0x66)_(0x0f)_(0x13)
				_(0x45)_(0xe0)_(0x85)_(0xc9)_(0x7e)_(0x15)_(0x49)_(0x83)_(0xc2)_(0x08)_(0x89)_(0x4d)_(0x10)_(0x8b)_(0x42)_(0xf8)
				_(0x89)_(0x45)_(0xd8)_(0x8b)_(0x42)_(0xfc)_(0x89)_(0x45)_(0xdc)_(0xeb)_(0x08)_(0x0f)_(0x57)_(0xc0)_(0x66)_(0x0f)
				_(0x13)_(0x45)_(0xd8)_(0x8b)_(0xc2)_(0xc7)_(0x45)_(0xfc)_(0x00)_(0x00)_(0x00)_(0x00)_(0x99)_(0x0f)_(0x57)_(0xc0)
				_(0x89)_(0x45)_(0xc0)_(0x8b)_(0xc1)_(0x89)_(0x55)_(0xc4)_(0x99)_(0x66)_(0x0f)_(0x13)_(0x45)_(0xc8)_(0x89)_(0x45)
				_(0xd0)_(0x89)_(0x55)_(0xd4)_(0xc7)_(0x45)_(0xf8)_(0x00)_(0x00)_(0x00)_(0x00)_(0x66)_(0x8c)_(0x65)_(0xf8)_(0xb8)
				_(0x2b)_(0x00)_(0x00)_(0x00)_(0x66)_(0x8e)_(0xe0)_(0x89)_(0x65)_(0xfc)_(0x83)_(0xe4)_(0xf0)_(0x6a)_(0x33)_(0xe8)
				_(0x00)_(0x00)_(0x00)_(0x00)_(0x83)_(0x04)_(0x24)_(0x05)_(0xcb)_(0x48)_(0x8b)_(0x4d)_(0xf0)_(0x48)_(0x8b)_(0x55)
				_(0xe8)_(0xff)_(0x75)_(0xe0)_(0x49)_(0x58)_(0xff)_(0x75)_(0xd8)_(0x49)_(0x59)_(0x48)_(0x8b)_(0x45)_(0xd0)_(0xa8)
				_(0x01)_(0x75)_(0x03)_(0x83)_(0xec)_(0x08)_(0x57)_(0x48)_(0x8b)_(0x7d)_(0xc0)_(0x48)_(0x85)_(0xc0)_(0x74)_(0x16)
				_(0x48)_(0x8d)_(0x7c)_(0xc7)_(0xf8)_(0x48)_(0x85)_(0xc0)_(0x74)_(0x0c)_(0xff)_(0x37)_(0x48)_(0x83)_(0xef)_(0x08)
				_(0x48)_(0x83)_(0xe8)_(0x01)_(0xeb)_(0xef)_(0x48)_(0x83)_(0xec)_(0x20)_(0xff)_(0x55)_(0x08)_(0x48)_(0x8b)_(0x4d)
				_(0xd0)_(0x48)_(0x8d)_(0x64)_(0xcc)_(0x20)_(0x5f)_(0x48)_(0x89)_(0x45)_(0xc8)_(0xe8)_(0x00)_(0x00)_(0x00)_(0x00)
				_(0xc7)_(0x44)_(0x24)_(0x04)_(0x23)_(0x00)_(0x00)_(0x00)_(0x83)_(0x04)_(0x24)_(0x0d)_(0xcb)_(0x66)_(0x8c)_(0xd8)
				_(0x66)_(0x8e)_(0xd0)_(0x8b)_(0x65)_(0xfc)_(0x66)_(0x8b)_(0x45)_(0xf8)_(0x66)_(0x8e)_(0xe0)_(0x8b)_(0x45)_(0xc8)
				_(0x8b)_(0x55)_(0xcc)_(0x5f)_(0x5e)_(0x5b)_(0x8b)_(0xe5)_(0x5d)_(0xc3)
			}
			#undef _
		}

		class X64Call
		{
	        template<typename char_t>
	        struct StringHelper : detail::GCBase
	        {
	            StringHelper(const char_t* v) : name(0) {
	                name = new _UNICODE_STRING_T<DWORD64>;
	                name->Buffer = (DWORD64)v;
	                name->Length = (WORD)tcslen(v) * sizeof(char_t);
	                name->MaximumLength = name->Length;
	            }
	            virtual void gc() { delete name; }
	            virtual DWORD64 toDWORD64() { return (DWORD64)name; }
			private:
	            _UNICODE_STRING_T<DWORD64>* name;
	        };
			template<typename T>
			DWORD64 ToDWORD64(T v, detail::GCHelper*) {
				return DWORD64(v);
			}
			template<> DWORD64 ToDWORD64<const char*>(const char* v, detail::GCHelper* helper) { return helper->add(new StringHelper<char>(v)); }
			template<> DWORD64 ToDWORD64<const wchar_t*>(const wchar_t* v, detail::GCHelper* helper) { return helper->add(new StringHelper<wchar_t>(v)); }
			template<> DWORD64 ToDWORD64<char*>(char* v, detail::GCHelper* helper) { return helper->add(new StringHelper<char>(v)); }
			template<> DWORD64 ToDWORD64<wchar_t*>(wchar_t* v, detail::GCHelper* helper) { return helper->add(new StringHelper<wchar_t>(v)); }

		private:
			DWORD64 func;

		public:
			X64Call(const char* funcName)                 : func(GetProcAddress64(0, GetNtDll64(), funcName)) {}
			X64Call(DWORD64 module, const char* funcName) : func(GetProcAddress64(0, module, funcName))       {}

			operator DWORD64() { return func; }

			DWORD64 operator()() { return func && x64Call(func, 0); }

		#define __TO_DWORD64_DECL(n) ToDWORD64(__PARAM(n), &helper)
		#define TO_DWORD64_DECL(n) __TO_DWORD64_DECL(n) ,
		#define END_TO_DWORD64_DECL(n) __TO_DWORD64_DECL(n)
		#define CALLERS(n) template<DECL_VOID_TEMPLATE_ARGS(n)> DWORD64 operator()(DECL_PARAMS_LIST(n)) { detail::GCHelper helper; return func && x64Call(func, n, REPEAT(n, TO_DWORD64_DECL, END_TO_DWORD64_DECL)); }
			CALLERS( 1) CALLERS( 2) CALLERS( 3) CALLERS( 4) CALLERS( 5) CALLERS( 6) CALLERS( 7) CALLERS( 8) CALLERS( 9) CALLERS(10)
			CALLERS(11) CALLERS(12) CALLERS(13) CALLERS(14) CALLERS(15) CALLERS(16) CALLERS(17) CALLERS(18) CALLERS(19) CALLERS(20)
		#undef CALLERS
		#undef END_TO_DWORD64_DECL
		#undef TO_DWORD64_DECL
		#undef __TO_DWORD64_DECL
		};

		VOID WINAPI SetLastError64(DWORD64 status)
		{
			typedef ULONG (WINAPI *RTL_NTSTATUS_TO_DOS_ERROR)(NTSTATUS Status);
			typedef ULONG (WINAPI *RTL_SET_LAST_WIN32_ERROR)(NTSTATUS Status);

			static RTL_NTSTATUS_TO_DOS_ERROR RtlNtStatusToDosError = (RTL_NTSTATUS_TO_DOS_ERROR)GetProcAddress(detail::hNtDll, "RtlNtStatusToDosError");
			static RTL_SET_LAST_WIN32_ERROR RtlSetLastWin32Error = (RTL_SET_LAST_WIN32_ERROR)GetProcAddress(detail::hNtDll, "RtlSetLastWin32Error");
	    
			if (RtlNtStatusToDosError && RtlSetLastWin32Error)
				RtlSetLastWin32Error(RtlNtStatusToDosError((DWORD)status));
		}

		SIZE_T WINAPI VirtualQueryEx64(HANDLE hProcess, DWORD64 lpAddress, MEMORY_BASIC_INFORMATION64* lpBuffer, SIZE_T dwLength)
		{
			static X64Call NtQueryVirtualMemory("NtQueryVirtualMemory");
			if (!NtQueryVirtualMemory) return 0;

			DWORD64 ret = 0;
			DWORD64 status = NtQueryVirtualMemory(hProcess, lpAddress, 0, lpBuffer, dwLength, &ret);
			if (!status) return (SIZE_T)ret;

			SetLastError64(ret);
			return FALSE;
		}

		DWORD64 WINAPI VirtualAllocEx64(HANDLE hProcess, DWORD64 lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect)
		{
			static X64Call NtAllocateVirtualMemory("NtAllocateVirtualMemory");
			if (!NtAllocateVirtualMemory) return 0;

			DWORD64 tmpAddr = lpAddress;
			DWORD64 tmpSize = dwSize;
			DWORD64 ret = NtAllocateVirtualMemory(hProcess, &tmpAddr, 0, &tmpSize, flAllocationType, flProtect);
			if (!ret) return tmpAddr;

			SetLastError64(ret);
			return FALSE;
		}

		BOOL WINAPI VirtualFreeEx64(HANDLE hProcess, DWORD64 lpAddress, SIZE_T dwSize, DWORD dwFreeType)
		{
			static X64Call NtFreeVirtualMemory("NtFreeVirtualMemory");
			if (!NtFreeVirtualMemory) return 0;

			DWORD64 tmpAddr = lpAddress;
			DWORD64 tmpSize = dwSize;
			DWORD64 ret = NtFreeVirtualMemory(hProcess, &tmpAddr, &tmpSize, dwFreeType);
			if (!ret) return TRUE;

			SetLastError64(ret);
			return FALSE;
		}

		BOOL WINAPI VirtualProtectEx64(HANDLE hProcess, DWORD64 lpAddress, SIZE_T dwSize, DWORD flNewProtect, DWORD* lpflOldProtect)
		{
			static X64Call NtProtectVirtualMemory("NtProtectVirtualMemory");
			if (!NtProtectVirtualMemory) return 0;

			DWORD64 tmpAddr = lpAddress;
			DWORD64 tmpSize = dwSize;
			DWORD64 ret = NtProtectVirtualMemory(hProcess, &tmpAddr, &tmpSize, flNewProtect, lpflOldProtect);
			if (!ret) return TRUE;

			SetLastError64(ret);
			return FALSE;
		}

		BOOL WINAPI ReadProcessMemory64(HANDLE hProcess, DWORD64 lpBaseAddress, LPVOID lpBuffer, SIZE_T nSize, SIZE_T* lpNumberOfBytesRead)
		{
			static X64Call NtReadVirtualMemory("NtReadVirtualMemory");
			if (!NtReadVirtualMemory) return 0;

			DWORD64 read = 0;
			DWORD64 ret = NtReadVirtualMemory(hProcess, lpBaseAddress, lpBuffer, nSize, &read);
			if (!ret) {
				if (lpNumberOfBytesRead) *lpNumberOfBytesRead = (SIZE_T)read;
				return TRUE;
			}

			SetLastError64(ret);
			return FALSE;
		}

		BOOL WINAPI WriteProcessMemory64(HANDLE hProcess, DWORD64 lpBaseAddress, LPVOID lpBuffer, SIZE_T nSize, SIZE_T* lpNumberOfBytesWritten)
		{
			static X64Call NtWriteVirtualMemory("NtWriteVirtualMemory");
			if (!NtWriteVirtualMemory) return 0;

			DWORD64 written = 0;
			DWORD64 ret = NtWriteVirtualMemory(hProcess, lpBaseAddress, lpBuffer, nSize, &written);
			if (!ret) {
				if (lpNumberOfBytesWritten) *lpNumberOfBytesWritten = (SIZE_T)written;
				return TRUE;
			}

			SetLastError64(ret);
			return FALSE;
		}

		HANDLE WINAPI CreateRemoteThread64(HANDLE hProcess,
											LPSECURITY_ATTRIBUTES lpThreadAttributes,
											SIZE_T dwStackSize,
											DWORD64 lpStartAddress,
											DWORD64 lpParameter,
											DWORD dwCreationFlags,
											LPDWORD lpThreadId)
		{
			static X64Call RtlCreateUserThread("RtlCreateUserThread");
			if (!RtlCreateUserThread) return 0;

			BOOLEAN createSuspended = dwCreationFlags & CREATE_SUSPENDED;
			ULONG stackSize = dwStackSize;
			DWORD64 handle = 0;
			DWORD64 status = RtlCreateUserThread(hProcess, lpThreadAttributes, createSuspended, 0, (dwCreationFlags & STACK_SIZE_PARAM_IS_A_RESERVATION) ? &stackSize : NULL, &stackSize, lpStartAddress, lpParameter, &handle, NULL);
			if (!status) return (HANDLE)handle;

			SetLastError64(status);
			return NULL;
		}

	#endif

	class ProcessWriter
	{
	public:
		template<typename T>
		ProcessWriter(HANDLE hProcess, T content, SIZE_T dwSize, DWORD flProtect = PAGE_READWRITE)
			: _autoRelease(TRUE)
			, _hProcess(hProcess)
			, _dw64Address(0)
			, _dwSize(dwSize)
		{
			if (!(_dw64Address = VirtualAllocEx64(hProcess, NULL, dwSize, MEM_COMMIT | MEM_RESERVE, flProtect)))
				return;
			SIZE_T written = 0;
			if (!WriteProcessMemory64(hProcess, _dw64Address, (PVOID)content, dwSize, &written) || written != dwSize) {
				VirtualFreeEx64(hProcess, _dw64Address, _dwSize, MEM_DECOMMIT);
				_dw64Address = 0;
			}
		}
		~ProcessWriter() {
			if (_dw64Address && _autoRelease)
				VirtualFreeEx64(_hProcess, _dw64Address, _dwSize, MEM_DECOMMIT);
		}
		void SetDontRelese() {
			_autoRelease = FALSE;
		}
		operator DWORD64() {
			return (DWORD64)_dw64Address;
		}
	#ifdef _WIN64
		template<typename T>
		operator T*() {
			return (T*)_dw64Address;
		}
	#endif

	private:
		BOOL _autoRelease;
		HANDLE _hProcess;
	#ifdef _WIN64
		LPVOID _dw64Address;
	#else
		DWORD64 _dw64Address;
	#endif
		SIZE_T _dwSize;
	};

	namespace {

		std::string makeShellCode(int cnt, bool is64Bit)
		{
			if(is64Bit) {
				// see X64Delegator_disassemble for details
				static const unsigned char kTmpl_x64[] = { 0x40, 0x53, 0x48, 0x83, 0xec, 0x20, 0x48, 0x8b, 0xd9, 0x48, 0x85, 0xc9, 0x74, 0x1d, 0x48, 0x83, 
														   0x39, 0x00, 0x48, 0x8b, 0x41, 0x08, 0x74, 0x0b, 0xff, 0xd0, 0x48, 0x89, 0x03, 0x48, 0x83, 0xc4, 
														   0x20, 0x5b, 0xc3, 0x48, 0x83, 0xc4, 0x20, 0x5b, 0x48, 0xff, 0xe0, 0x33, 0xc0, 0x48, 0x83, 0xc4, 
														   0x20, 0x5b, 0xc3 };

				std::string templ_x64((const char*)kTmpl_x64, sizeof(kTmpl_x64));
				if(!cnt) return templ_x64;

				templ_x64[13] += (cnt <= 4) ? cnt * 4 : (cnt - 4) * 9 + 16;
				if(cnt >= 1)
					templ_x64[16] = 0x3b;

				if(cnt < 3) {
					if(cnt >= 1) {
						templ_x64.insert(22, "\x48\x8b\x49\x10", 4);
					}
					if(cnt >= 2) {
						templ_x64.insert(22, "\x48\x8b\x51\x18", 4);
					}
				}
				else {
					templ_x64[20] = 0x49;
					templ_x64[21] = 0x10;
					templ_x64.insert(22, "\x48\x8B\x53\x18", 4);
					templ_x64.insert(22, "\x4c\x8b\x43\x20", 4);
					templ_x64.insert(22, "\x48\x8b\x43\x08", 4);
					if(cnt >= 4) {
						templ_x64.insert(26, "\x4c\x8b\x4b\x28", 4);
					}
					if(cnt >= 5) {
						templ_x64.insert(18, "\x4c\x8B\x53\x30", 4);
						templ_x64.insert(42, "\x4c\x89\x54\x24\x20", 5);
					}
					if(cnt >= 6) {
						templ_x64[21] = 0x38;
						templ_x64.insert(22, "\x4c\x8b\x5b\x30", 4);
						templ_x64[50] = 0x28;
						templ_x64.insert(51, "\x4c\x89\x5c\x24\x20", 5);
					}
					// TODO
				}
				return templ_x64;
			}
			// see X86Delegator_disassemble for details
			static const unsigned char kTmpl_x86[] = { 0x55, 0x8b, 0xec, 0x51, 0x83, 0x7d, 0x08, 0x00, 0x74, 0x0c, 0x8b ,0x45, 0x08, 0x8b, 0x08, 0xff, 
													   0xd0, 0x89, 0x45, 0xfc, 0xeb, 0x07, 0xc7, 0x45, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x8b, 0x45, 0xfc,
													   0x8b, 0xe5, 0x5d, 0xc3 };
			std::string templ_x86((const char*)kTmpl_x86, sizeof(kTmpl_x86));
			// je distance
			templ_x86[9] += cnt * 7;
			templ_x86[16] += ((1 - cnt) % 3 + 3) % 3;
			int pos = 13;
			for(int i = 0; i < cnt; ++i) {
				switch(i % 3) {
					case 0:
						templ_x86.insert(pos, "\x8b\x48\xcc\x51\x8b\x55\x08", 7);
						break;
					case 1:
						templ_x86.insert(pos, "\x8b\x42\xcc\x50\x8b\x4d\x08", 7);
						break;
					case 2:
						templ_x86.insert(pos, "\x8b\x51\xcc\x52\x8b\x45\x08", 7);
						break;
				}
				templ_x86[pos + 2] = (cnt - i) << 2;
				pos += 7;
			}
			switch(cnt % 3) {
				case 0:
					templ_x86[pos + 1] = 0x08;
					break;
				case 1:
					templ_x86[pos + 1] = 0x02;
					break;
				case 2:
					templ_x86[pos + 1] = 0x11;
					break;
			}
			return templ_x86;
		}

		template<int argCnt, bool is64Bit>
		const std::string& shellCode() {
			static std::string kCode = makeShellCode(argCnt, is64Bit);
			return kCode;
		}

	}

	class YAPICall
	{
		template<typename T>
		DWORD64 ToDWORD64(T v, HANDLE hProcess, detail::GCHelper*) {
			return DWORD64(v);
		}
	    template<typename char_t>
	    struct StringHelper : detail::GCBase
	    {
	        StringHelper(HANDLE hProcess, const char_t* v) : name(0) {
				name = new ProcessWriter(hProcess, v, (tcslen(v) + 1) * sizeof(char_t));
	        }
	        virtual void gc() { delete name; }
	        virtual DWORD64 toDWORD64() { return (DWORD64)*name; }
		private:
	        ProcessWriter* name;
	    };
		template<> DWORD64 ToDWORD64<const char*>(const char* v, HANDLE hProcess, detail::GCHelper* helper) { return helper->add(new StringHelper<char>(hProcess, v)); }
		template<> DWORD64 ToDWORD64<const wchar_t*>(const wchar_t* v, HANDLE hProcess, detail::GCHelper* helper) { return helper->add(new StringHelper<wchar_t>(hProcess, v)); }
		template<> DWORD64 ToDWORD64<char*>(char* v, HANDLE hProcess, detail::GCHelper* helper) { return helper->add(new StringHelper<char>(hProcess, v)); }
		template<> DWORD64 ToDWORD64<wchar_t*>(wchar_t* v, HANDLE hProcess, detail::GCHelper* helper) { return helper->add(new StringHelper<wchar_t>(hProcess, v)); }

	private:
		HANDLE _hProcess;
		ProcessWriter* _sc;
		DWORD64 func;
		BOOL _dw64Ret;
		DWORD _dwTimeout;
		BOOL _is64Bit;

		template<int argCnt>
		bool initShellCoder(ProcessWriter*& sc) {
			if(sc) return false;
			const std::string& shellcode = _is64Bit ? shellCode<argCnt, 1>() : shellCode<argCnt, 0>();
			sc = new ProcessWriter(_hProcess, shellcode.data(), shellcode.size() + 1, PAGE_EXECUTE_READWRITE);
			return true;
		}

		template<typename T>
		DWORD64 call(const std::vector<T>& param) {
			ProcessWriter p(_hProcess, &param[0], sizeof(T) * (param.size()));
			if (!p) return -1;
			HANDLE hThread = 0;
			if (_is64Bit)
				hThread = CreateRemoteThread64(_hProcess, NULL, 0, *_sc, p, 0, NULL);
			else {
#ifdef _WIN64
				// see X64toX86_disassemble for details
				static const unsigned char kTmpl_x64_to_x86[] = { 0x48, 0x89, 0x4c, 0x24, 0x08, 0x48, 0x83, 0xec, 0x28, 0x48, 0x8b, 0x44, 0x24, 0x30, 0x8b, 0x48, 
																  0x08, 0x48, 0x8b, 0x44, 0x24, 0x30, 0x6a, 0x33, 0xe8, 0x00, 0x00, 0x00, 0x00, 0x83, 0x04, 0x24, 
																  0x05, 0xcb, 0xff, 0xd0, 0xe8, 0x00, 0x00, 0x00, 0x00, 0xc7, 0x44, 0x24, 0x04, 0x23, 0x00, 0x00, 
																  0x00, 0x83, 0x04, 0x24, 0x0d, 0xcb, 0x48, 0x83, 0xc4, 0x28, 0xc3 };
				std::string x86_shellcode((char*)kTmpl_x64_to_x86, sizeof(kTmpl_x64_to_x86));
				ProcessWriter* sc = new ProcessWriter(_hProcess, x86_shellcode.data(), x86_shellcode.size() + 1, PAGE_EXECUTE_READWRITE);
				sc->SetDontRelese();
				hThread = CreateRemoteThread64(_hProcess, NULL, 0, *_sc, p, 0, NULL);
#else
				hThread = CreateRemoteThread(_hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)(DWORD64)*_sc, (PVOID)(DWORD64)p, 0, NULL);
#endif
			}
			if (!hThread) return -1;
			if (WaitForSingleObject(hThread, _dwTimeout) != WAIT_OBJECT_0) {
				_sc->SetDontRelese();
				CloseHandle(hThread);
				return -1;
			}
			if (!_is64Bit || !_dw64Ret) {
				DWORD ret = 0;
				GetExitCodeThread(hThread, &ret);
				CloseHandle(hThread);
				return ret;
			}
			DWORD64 ret = 0;
			CloseHandle(hThread);
			ReadProcessMemory64(_hProcess, p, &ret, sizeof(DWORD64), NULL);
			return ret;
		}

	public:
		YAPICall(HANDLE hProcess, const char* funcName)
			: _hProcess(hProcess)
			, _sc(0)
			, func(GetProcAddress64(hProcess, GetNtDll64(), funcName))
			, _dw64Ret(FALSE)
			, _dwTimeout(INFINITE)
			, _is64Bit(detail::is64BitOS)
		{
		}
		YAPICall(HANDLE hProcess, DWORD64 moudle, const char* funcName)
			: _hProcess(hProcess)
			, _sc(0)
			, func(GetProcAddress64(hProcess, moudle, funcName))
			, _dw64Ret(FALSE)
			, _dwTimeout(INFINITE)
			, _is64Bit(detail::is64BitOS)
		{
		}
		YAPICall(HANDLE hProcess, const TCHAR* modName, const char* funcName)
			: _hProcess(hProcess)
			, _sc(0)
			, func(GetProcAddress64(hProcess, GetModuleHandle64(hProcess, modName), funcName))
			, _dw64Ret(FALSE)
			, _dwTimeout(INFINITE)
			, _is64Bit(detail::is64BitOS)
		{
			if(!func) {
				func = GetProcAddress(hProcess, GetModuleHandle(hProcess, modName), funcName);
				_is64Bit = FALSE;
			}
		}

		~YAPICall() { if (_sc) delete _sc; }

		operator DWORD64() { return func; }

		YAPICall& Dw64() { _dw64Ret = TRUE; return *this;  }
		YAPICall& Timeout(DWORD dwTimeout) { _dwTimeout = dwTimeout; return *this; }

	#define TO_DWORD64_ARRAY_DECL(n) param[n + 1] = ToDWORD64(__PARAM(n), _hProcess, &helper);
	#define TO_DWORD_ARRAY_DECL(n) param[n] = (DWORD)ToDWORD64(__PARAM(n), _hProcess, &helper);

	#define CALLERSX(n) \
		DWORD64 operator()(DECL_PARAMS_LIST(n)) {\
			bool b = initShellCoder<n>(_sc);\
			if(!b || !func || !_sc || !*_sc) return -1;\
			detail::GCHelper helper;\
			if(_is64Bit) {\
				std::vector<DWORD64> param(n + 2, 0);\
				param[0] = _dw64Ret;\
				param[1] = func;\
				REPEAT(n, TO_DWORD64_ARRAY_DECL, TO_DWORD64_ARRAY_DECL)\
				return call<DWORD64>(param);\
			}\
			std::vector<DWORD> param(n + 1, 0);\
			param[0] = (DWORD)func;\
			REPEAT(n, TO_DWORD_ARRAY_DECL, TO_DWORD_ARRAY_DECL)\
			return call<DWORD>(param);\
		}
	#define CALLERS(n) template<DECL_VOID_TEMPLATE_ARGS(n)> CALLERSX(n)
		CALLERSX( 0)
		CALLERS( 1) CALLERS( 2) CALLERS( 3) CALLERS( 4) CALLERS( 5) CALLERS( 6) /*CALLERS( 7) CALLERS( 8) CALLERS( 9) CALLERS(10)
		CALLERS(11) CALLERS(12) CALLERS(13) CALLERS(14) CALLERS(15) CALLERS(16) CALLERS(17) CALLERS(18) CALLERS(19) CALLERS(20)*/
	#undef CALLERSX
	#undef CALLERS
	#undef TO_DWORD_ARRAY_DECL
	#undef TO_DWORD64_ARRAY_DECL
	};

	#define YAPI(h, m, f) YAPICall(h, m, #f)
}
