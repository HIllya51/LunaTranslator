#pragma once

#include "textthread.h"
namespace Host
{
	using HostInfoHandler = std::function<void(HOSTINFO type, const std::wstring &)>;
	using ProcessEventHandler = std::function<void(DWORD)>;
	using ThreadEventHandler = std::function<void(TextThread &)>;
	using HookEventHandler = std::function<void(const HookParam &, const std::wstring &text)>;
	using HookInsertHandler = std::function<void(DWORD, uint64_t, const std::wstring &)>;
	using EmbedCallback = std::function<void(const std::wstring &, const ThreadParam &)>;
	using I18NQueryCallback = std::function<std::optional<std::wstring>(const std::wstring &str)>;
	void Start(std::optional<ProcessEventHandler> Connect, std::optional<ProcessEventHandler> Disconnect, std::optional<ThreadEventHandler> Create, std::optional<ThreadEventHandler> Destroy, std::optional<TextThread::OutputCallback> Output, std::optional<HostInfoHandler> hostinfo, std::optional<HookInsertHandler> hookinsert, std::optional<EmbedCallback> embed, std::optional<I18NQueryCallback> i18nQueryCallback);
	void ConnectAndInjectProcess(DWORD processId);
	void ConnectProcess(DWORD processId);
	bool CheckIfNeedInject(DWORD processId);
	void DetachProcess(DWORD processId);
	void InsertHook(DWORD processId, HookParam hp);
	void ResetLanguage();
	void InsertPCHooks(DWORD processId, int which);
	void RemoveHook(DWORD processId, uint64_t address);
	void FindHooks(DWORD processId, SearchParam sp, HookEventHandler HookFound = {}, LPCWSTR addresses = nullptr);
	CommonSharedMem *GetCommonSharedMem(DWORD pid);
	TextThread *GetThread(int64_t handle);
	TextThread &GetThread(ThreadParam tp);
	void InfoOutput(HOSTINFO type, std::wstring text);
	void AddConsoleOutput(std::wstring text);

	inline int defaultCodepage = SHIFT_JIS;

	bool CheckIsUsingEmbed(ThreadParam tp);

}
