#pragma once

#include "textthread.h"
namespace Host
{
	using ConsoleHandler = std::function<void(const std::wstring &)>;
	using ProcessEventHandler = std::function<void(DWORD)>;
	using ThreadEventHandler = std::function<void(TextThread &)>;
	using HookEventHandler = std::function<void(const HookParam &, const std::wstring &text)>;
	using HookInsertHandler = std::function<void(DWORD, uint64_t, const std::wstring &)>;
	using EmbedCallback = std::function<void(const std::wstring &, const ThreadParam &)>;
	void Start(ProcessEventHandler Connect, ProcessEventHandler Disconnect, ThreadEventHandler Create, ThreadEventHandler Destroy, TextThread::OutputCallback Output, bool createconsole = true);
	void StartEx(std::optional<ProcessEventHandler> Connect, std::optional<ProcessEventHandler> Disconnect, std::optional<ThreadEventHandler> Create, std::optional<ThreadEventHandler> Destroy, std::optional<TextThread::OutputCallback> Output, std::optional<ConsoleHandler> console, std::optional<HookInsertHandler> hookinsert, std::optional<EmbedCallback> embed, std::optional<ConsoleHandler> warning);
	void InjectProcess(DWORD processId, const std::wstring locationX = L"");
	bool CreatePipeAndCheck(DWORD processId);

	void DetachProcess(DWORD processId);

	void InsertHook(DWORD processId, HookParam hp);
	void RemoveHook(DWORD processId, uint64_t address);
	void FindHooks(DWORD processId, SearchParam sp, HookEventHandler HookFound = {});
	CommonSharedMem *GetCommonSharedMem(DWORD pid);
	TextThread *GetThread(int64_t handle);
	TextThread &GetThread(ThreadParam tp);

	void AddConsoleOutput(std::wstring text);
	void Warning(std::wstring text);

	inline int defaultCodepage = SHIFT_JIS;

	constexpr ThreadParam console{0, 0, 0, 0};
	bool CheckIsUsingEmbed(ThreadParam tp);

}
