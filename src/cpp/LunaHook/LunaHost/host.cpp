#include "host.h"
#define SEARCH_SJIS_UNSAFE 0
namespace
{
	class ProcessRecord
	{
	public:
		ProcessRecord(DWORD processId, HANDLE pipe) : pipe(pipe),
													  mappedFile2(OpenFileMappingW(FILE_MAP_READ | FILE_MAP_WRITE, FALSE, (EMBED_SHARED_MEM + std::to_wstring(processId)).c_str())),
													  viewMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(processId))

		{
			commonsharedmem = (CommonSharedMem *)MapViewOfFile(mappedFile2, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, sizeof(CommonSharedMem));
			// 放到构造表里就不行，不知道为何。
		}

		~ProcessRecord()
		{
			UnmapViewOfFile(commonsharedmem);
		}

		template <typename T>
		void Send(T data)
		{
			static_assert(sizeof(data) < PIPE_BUFFER_SIZE);
			std::thread([=]
						{ WriteFile(pipe, &data, sizeof(data), DUMMY, nullptr); })
				.detach();
		}

		Host::HookEventHandler OnHookFound = [](auto, auto) {};

		CommonSharedMem *commonsharedmem;

	private:
		HANDLE pipe;
		AutoHandle<> mappedFile2;
		WinMutex viewMutex;
	};

	size_t HashThreadParam(ThreadParam tp) { return std::hash<int64_t>()(tp.processId + tp.addr) + std::hash<int64_t>()(tp.ctx + tp.ctx2); }
	Synchronized<std::unordered_map<ThreadParam, TextThread, Functor<HashThreadParam>>> textThreadsByParams;
	Synchronized<std::unordered_map<DWORD, ProcessRecord>> processRecordsByIds;

	Host::ProcessEventHandler OnConnect, OnDisconnect;
	Host::ThreadEventHandler OnCreate, OnDestroy;
	Host::HostInfoHandler OnHostInfo = 0;
	Host::HookInsertHandler HookInsert = 0;
	Host::EmbedCallback embedcallback = 0;
	TextThread *consolethread = nullptr;
	void RemoveThreads(std::function<bool(ThreadParam)> removeIf)
	{
		std::vector<TextThread *> threadsToRemove;
		for (auto &[tp, thread] : textThreadsByParams.Acquire().contents)
			if (removeIf(tp))
				threadsToRemove.push_back(&thread);
		for (auto thread : threadsToRemove)
		{
			try
			{
				TextThread::syncThreads->erase(thread);
			}
			catch (...)
			{
			}
			OnDestroy(*thread);
			textThreadsByParams->erase(thread->tp);
		}
	}
	void __handlepipethread(HANDLE hookPipe, HANDLE hostPipe, HANDLE pipeAvailableEvent)
	{
		ConnectNamedPipe(hookPipe, nullptr);
		CloseHandle(pipeAvailableEvent);
		WORD hookversion[4];
		BYTE buffer[PIPE_BUFFER_SIZE] = {};
		DWORD bytesRead, processId;
		ReadFile(hookPipe, &processId, sizeof(processId), &bytesRead, nullptr);
		ReadFile(hookPipe, hookversion, sizeof(hookversion), &bytesRead, nullptr);
		if (memcmp(hookversion, LUNA_VERSION, sizeof(hookversion)) != 0)
			Host::InfoOutput(HOSTINFO::Warning, TR[UNMATCHABLEVERSION]);

		processRecordsByIds->try_emplace(processId, processId, hostPipe);
		processRecordsByIds->at(processId).Send(curr_lang);
		OnConnect(processId);
		Host::AddConsoleOutput(FormatString(TR[PROC_CONN], processId));

		while (ReadFile(hookPipe, buffer, PIPE_BUFFER_SIZE, &bytesRead, nullptr))
			switch (*(HostNotificationType *)buffer)
			{
			case HOST_NOTIFICATION_FOUND_HOOK:
			{
				auto info = *(HookFoundNotif *)buffer;
				auto OnHookFound = processRecordsByIds->at(processId).OnHookFound;
				std::wstring wide = info.text;
				if (wide.size() > STRING)
				{
					wcscpy_s(info.hp.hookcode, HOOKCODE_LEN, HookCode::Generate(info.hp, processId).c_str());
					OnHookFound(info.hp, std::move(info.text));
				}
				if (!(info.hp.type & CSHARP_STRING))
				{
					info.hp.type &= ~CODEC_UTF16;
					if (auto converted = StringToWideString((char *)info.text, info.hp.codepage))
#if SEARCH_SJIS_UNSAFE
						if (converted->size())
#else
						if (converted->size() > STRING)
#endif
						{
							wcscpy_s(info.hp.hookcode, HOOKCODE_LEN, HookCode::Generate(info.hp, processId).c_str());
							OnHookFound(info.hp, std::move(converted.value()));
						}
					if (auto converted = StringToWideString((char *)info.text, info.hp.codepage = CP_UTF8))
						if (converted->size() > STRING)
						{
							wcscpy_s(info.hp.hookcode, HOOKCODE_LEN, HookCode::Generate(info.hp, processId).c_str());
							OnHookFound(info.hp, std::move(converted.value()));
						}
				}
			}
			break;
			case HOST_NOTIFICATION_RMVHOOK:
			{
				auto info = *(HookRemovedNotif *)buffer;
				auto sm = Host::GetCommonSharedMem(processId);
				if (sm)
					for (int i = 0; i < ARRAYSIZE(sm->embedtps); i++)
						if (sm->embedtps[i].use && (sm->embedtps[i].tp.addr == info.address) && (sm->embedtps[i].tp.processId == processId))
							ZeroMemory(sm->embedtps + i, sizeof(sm->embedtps[i]));
				RemoveThreads([&](ThreadParam tp)
							  { return tp.processId == processId && tp.addr == info.address; });
			}
			break;
			case HOST_NOTIFICATION_INSERTING_HOOK:
			{
				if (HookInsert)
				{
					auto info = (HookInsertingNotif *)buffer;
					HookInsert(processId, info->addr, info->hookcode);
				}
			}
			break;
			case HOST_NOTIFICATION_TEXT:
			{
				auto info = *(HostInfoNotif *)buffer;
				Host::InfoOutput(info.type, StringToWideString(info.message));
			}
			break;
			default:
			{
				auto data = (TextOutput_T *)buffer;
				auto length = bytesRead - sizeof(TextOutput_T);
				auto tp = data->tp;
				auto hp = data->hp;
				auto _textThreadsByParams = textThreadsByParams.Acquire();

				auto thread = _textThreadsByParams->find(tp);
				if (thread == _textThreadsByParams->end())
				{
					try
					{
						thread = _textThreadsByParams->try_emplace(tp, tp, hp).first;
					}
					catch (std::out_of_range)
					{
						continue;
					} // probably garbage data in pipe, try again
					OnCreate(thread->second);
				}

				thread->second.hp.type = data->type;
				thread->second.Push(data->data, length);

				if (embedcallback)
				{
					auto &hp = thread->second.hp;
					if (hp.type & EMBED_ABLE && Host::CheckIsUsingEmbed(thread->second.tp))
					{
						if (auto t = commonparsestring(data->data, length, &hp, Host::defaultCodepage))
						{
							auto text = t.value();
							if (text.size())
							{
								embedcallback(text, tp);
							}
						}
					}
				}
			}
			break;
			}

		RemoveThreads([&](ThreadParam tp)
					  { return tp.processId == processId; });
		OnDisconnect(processId);
		Host::AddConsoleOutput(FormatString(TR[PROC_DISCONN], processId));
		processRecordsByIds->erase(processId);
	}
	void CreatePipe(int pid)
	{
		HANDLE
		hookPipe = CreateNamedPipeW((std::wstring(HOOK_PIPE) + std::to_wstring(pid)).c_str(), PIPE_ACCESS_INBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, 0, PIPE_BUFFER_SIZE, MAXDWORD, &allAccess),
		hostPipe = CreateNamedPipeW((std::wstring(HOST_PIPE) + std::to_wstring(pid)).c_str(), PIPE_ACCESS_OUTBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, PIPE_BUFFER_SIZE, 0, MAXDWORD, &allAccess);
		HANDLE pipeAvailableEvent = CreateEventW(&allAccess, FALSE, FALSE, (std::wstring(PIPE_AVAILABLE_EVENT) + std::to_wstring(pid)).c_str());

		SetEvent(pipeAvailableEvent);
		std::thread(__handlepipethread, hookPipe, hostPipe, pipeAvailableEvent).detach();
	}
}

namespace Host
{
	std::mutex threadmutex;
	std::mutex outputmutex;
	std::mutex procmutex;

	void SetLanguage(const char *lang)
	{
		curr_lang = map_to_support_lang(lang);
		auto &prs = processRecordsByIds.Acquire().contents;
		for (auto &&[_, record] : prs)
		{
			record.Send(SetLanguageCmd(curr_lang));
		}
	}
	void Start(ProcessEventHandler Connect, ProcessEventHandler Disconnect, ThreadEventHandler Create, ThreadEventHandler Destroy, TextThread::OutputCallback Output, bool createconsole)
	{
		OnConnect = [=](auto &&...args)
		{std::lock_guard _(procmutex);Connect(std::forward<decltype(args)>(args)...); };
		OnDisconnect = [=](auto &&...args)
		{std::lock_guard _(procmutex);Disconnect(std::forward<decltype(args)>(args)...); };
		OnCreate = [=](TextThread &thread)
		{{std::lock_guard _(threadmutex); Create(thread);} thread.Start(); };
		OnDestroy = [=](TextThread &thread)
		{thread.Stop(); {std::lock_guard _(threadmutex); Destroy(thread);} };
		TextThread::Output = [=](auto &&...args)
		{std::lock_guard _(outputmutex);return Output(std::forward<decltype(args)>(args)...); };

		if (createconsole)
		{
			OnCreate(textThreadsByParams->try_emplace(console, console, HookParam{}, TR[CONSOLE]).first->second);
			consolethread = &textThreadsByParams->at(console);
			Host::AddConsoleOutput(TR[ProjectHomePage]);
		}
		// CreatePipe();
	}
	void StartEx(std::optional<ProcessEventHandler> Connect,
				 std::optional<ProcessEventHandler> Disconnect,
				 std::optional<ThreadEventHandler> Create,
				 std::optional<ThreadEventHandler> Destroy,
				 std::optional<TextThread::OutputCallback> Output,
				 bool consolethread,
				 std::optional<HostInfoHandler> hostinfo,
				 std::optional<HookInsertHandler> hookinsert,
				 std::optional<EmbedCallback> embed)
	{
		Start(Connect.value_or([](auto) {}), Disconnect.value_or([](auto) {}), Create.value_or([](auto &) {}), Destroy.value_or([](auto &) {}), Output.value_or([](auto &, auto &)
																																								{ return false; }),
			  consolethread);
		if (hostinfo)
			OnHostInfo = [=](auto &&...args)
			{std::lock_guard _(outputmutex);hostinfo.value()(std::forward<decltype(args)>(args)...); };
		if (hookinsert)
			HookInsert = [=](auto &&...args)
			{std::lock_guard _(threadmutex);hookinsert.value()(std::forward<decltype(args)>(args)...); };
		if (embed)
			embedcallback = [=](auto &&...args)
			{std::lock_guard _(outputmutex);embed.value()(std::forward<decltype(args)>(args)...); };
	}
	bool CheckProcess(DWORD processId)
	{
		if (processId == GetCurrentProcessId())
			return false;

		WinMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(processId));
		if (GetLastError() == ERROR_ALREADY_EXISTS)
		{
			AddConsoleOutput(TR[ALREADY_INJECTED]);
			return false;
		}
		return true;
	}
	bool CreatePipeAndCheck(DWORD processId)
	{
		CreatePipe(processId);
		return CheckProcess(processId);
	}
	void DetachProcess(DWORD processId)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		if (prs.find(processId) == prs.end())
			return;
		prs.at(processId).Send(HOST_COMMAND_DETACH);
	}
	void InsertPCHooks(DWORD processId, int which)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		if (prs.find(processId) == prs.end())
			return;
		prs.at(processId).Send(InsertPCHooksCmd(which));
	}
	void InsertHook(DWORD processId, HookParam hp)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		if (prs.find(processId) == prs.end())
			return;
		prs.at(processId).Send(InsertHookCmd(hp));
	}

	void RemoveHook(DWORD processId, uint64_t address)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		if (prs.find(processId) == prs.end())
			return;
		prs.at(processId).Send(RemoveHookCmd(address));
	}

	void FindHooks(DWORD processId, SearchParam sp, HookEventHandler HookFound)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		if (prs.find(processId) == prs.end())
			return;
		if (HookFound)
			prs.at(processId).OnHookFound = HookFound;
		prs.at(processId).Send(FindHookCmd(sp));
	}

	TextThread &GetThread(ThreadParam tp)
	{
		return textThreadsByParams->at(tp);
	}

	TextThread *GetThread(int64_t handle)
	{
		for (auto &[tp, thread] : textThreadsByParams.Acquire().contents)
			if (thread.handle == handle)
				return &thread;
		return nullptr;
	}
	CommonSharedMem *GetCommonSharedMem(DWORD processId)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		if (prs.find(processId) == prs.end())
			return 0;
		return prs.at(processId).commonsharedmem;
	}
	void AddConsoleOutput(std::wstring text)
	{
		InfoOutput(HOSTINFO::Console, text);
	}
	void InfoOutput(HOSTINFO type, std::wstring text)
	{
		if (OnHostInfo)
			OnHostInfo(type, std::move(text));

		if (consolethread || (type != HOSTINFO::Console))
		{
			switch (type)
			{
			case HOSTINFO::Warning:
				text = FormatString(L"[%s]", TR[T_WARNING]) + text;
				break;
			case HOSTINFO::EmuGameName:
				text = L"[Game] " + text;
				break;
			}
			if (consolethread)
				consolethread->AddSentence(std::move(text));
			else if (type != HOSTINFO::Console)
				OnHostInfo(HOSTINFO::Console, std::move(text));
		}
	}
	bool CheckIsUsingEmbed(ThreadParam tp)
	{
		auto sm = Host::GetCommonSharedMem(tp.processId);
		if (!sm)
			return false;
		for (int i = 0; i < ARRAYSIZE(sm->embedtps); i++)
		{
			if (sm->embedtps[i].use && (sm->embedtps[i].tp == tp))
				return true;
		}
		return false;
	}
}
