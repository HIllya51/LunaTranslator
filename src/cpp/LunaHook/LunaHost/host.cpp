#include "host.h"
#define HOOK_SEARCH_LENGTH STRING
// #define HOOK_SEARCH_LENGTH 0
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
	Host::HostInfoHandler OnHostInfo;
	Host::HookInsertHandler HookInsert;
	Host::EmbedCallback embedcallback;
	Host::I18NQueryCallback i18nQueryCallback;
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
	void VersionMatchCheck(HANDLE hookPipe)
	{
		WORD hookversion[4];
		DWORD bytesRead;
		ReadFile(hookPipe, hookversion, sizeof(hookversion), &bytesRead, nullptr);
		if (memcmp(hookversion, LUNA_VERSION, sizeof(hookversion)) != 0)
			Host::InfoOutput(HOSTINFO::Warning, TR[UNMATCHABLEVERSION]);
	}
	void __handlepipethread(DWORD processId, HANDLE hookPipe, HANDLE hostPipe, HANDLE pipeAvailableEvent)
	{
		ConnectNamedPipe(hookPipe, nullptr);
		CloseHandle(pipeAvailableEvent);

		VersionMatchCheck(hookPipe);

		OnConnect(processId);
		processRecordsByIds->try_emplace(processId, processId, hostPipe);
		Host::AddConsoleOutput(FormatString(TR[PROC_CONN], processId));
		BYTE buffer[PIPE_BUFFER_SIZE] = {};
		DWORD bytesRead;
		while (ReadFile(hookPipe, buffer, PIPE_BUFFER_SIZE, &bytesRead, nullptr))
			switch (*(HostNotificationType *)buffer)
			{
			case HOST_NOTIFICATION_I18N_RESP:
			{
				auto info = (HostInfoI18NReq *)buffer;
				auto ret = WideStringToString(i18nQueryCallback(StringToWideString(info->key)).value_or(L""));
				processRecordsByIds->at(processId).Send(I18NResponse(info->enum_, ret));
			}
			break;
			case HOST_NOTIFICATION_FOUND_HOOK:
			{
				auto info = (HookFoundNotif *)buffer;
				auto OnHookFound = processRecordsByIds->at(processId).OnHookFound;
				std::wstring wide = info->text;
				if (wide.size() > HOOK_SEARCH_LENGTH)
				{
					wcscpy_s(info->hp.hookcode, HOOKCODE_LEN, HookCode::Generate(info->hp, processId).c_str());
					OnHookFound(info->hp, std::move(info->text));
				}
				if (!(info->hp.type & CSHARP_STRING))
				{
					info->hp.type &= ~CODEC_UTF16;
					if (auto converted = StringToWideString((char *)info->text, info->hp.codepage))

						if (converted->size() > HOOK_SEARCH_LENGTH)
						{
							wcscpy_s(info->hp.hookcode, HOOKCODE_LEN, HookCode::Generate(info->hp, processId).c_str());
							OnHookFound(info->hp, std::move(converted.value()));
						}
					if (auto converted = StringToWideString((char *)info->text, info->hp.codepage = CP_UTF8))
						if (converted->size() > HOOK_SEARCH_LENGTH)
						{
							wcscpy_s(info->hp.hookcode, HOOKCODE_LEN, HookCode::Generate(info->hp, processId).c_str());
							OnHookFound(info->hp, std::move(converted.value()));
						}
				}
			}
			break;
			case HOST_NOTIFICATION_RMVHOOK:
			{
				auto info = (HookRemovedNotif *)buffer;
				auto sm = Host::GetCommonSharedMem(processId);
				if (sm)
					for (int i = 0; i < ARRAYSIZE(sm->embedtps); i++)
						if (sm->embedtps[i].use && (sm->embedtps[i].tp.addr == info->address) && (sm->embedtps[i].tp.processId == processId))
							ZeroMemory(sm->embedtps + i, sizeof(sm->embedtps[i]));
				RemoveThreads([&](ThreadParam tp)
							  { return tp.processId == processId && tp.addr == info->address; });
			}
			break;
			case HOST_NOTIFICATION_INSERTING_HOOK:
			{
				auto info = (HookInsertingNotif *)buffer;
				HookInsert(processId, info->addr, info->hookcode);
			}
			break;
			case HOST_NOTIFICATION_TEXT:
			{
				auto info = (HostInfoNotif *)buffer;
				Host::InfoOutput(info->type, StringToWideString(info->message));
			}
			break;
			case HOST_NOTIFICATION_TEXT_W:
			{
				auto info = (HostInfoNotifW *)buffer;
				Host::InfoOutput(info->type, info->message);
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

				[&]()
				{
					auto &thp = thread->second.hp;
					if (!(thp.type & EMBED_ABLE && Host::CheckIsUsingEmbed(thread->second.tp)))
						return;
					auto sm = Host::GetCommonSharedMem(tp.processId);
					if (!sm)
						return;
					if (sm->clearText)
						return;
					auto t = commonparsestring(data->data, length, &thp, Host::defaultCodepage);
					if (!t)
						return;
					auto text = t.value();
					if (text.empty())
						return;
					embedcallback(text, tp);
				}();
			}
			break;
			}

		RemoveThreads([&](ThreadParam tp)
					  { return tp.processId == processId; });
		OnDisconnect(processId);
		Host::AddConsoleOutput(FormatString(TR[PROC_DISCONN], processId));
		processRecordsByIds->erase(processId);
	}
}
#define IF_HASVAL_DISPATCH_1(Lock, X, V) \
	if (X)                               \
	{                                    \
		std::lock_guard _(Lock);         \
		X.value()(V);                    \
	}
#define IF_HASVAL_DISPATCH(Lock, X) IF_HASVAL_DISPATCH_1(Lock, X, std::forward<decltype(args)>(args)...)
namespace Host
{
	std::mutex threadmutex;
	std::mutex outputmutex;
	std::mutex procmutex;

	void ResetLanguage()
	{

		for (auto &[_, data] : TR.get_host())
		{
			auto ret = i18nQueryCallback(data.raw());
			if (!ret)
				continue;
			data.set(std::move(ret.value()));
		}
		for (auto &[pid, rcd] : processRecordsByIds.Acquire().contents)
		{
			rcd.Send(ResetLanguageCmd{});
		}
	}
	void Start(std::optional<ProcessEventHandler> Connect,
			   std::optional<ProcessEventHandler> Disconnect,
			   std::optional<ThreadEventHandler> Create,
			   std::optional<ThreadEventHandler> Destroy,
			   std::optional<TextThread::OutputCallback> Output,
			   std::optional<HostInfoHandler> hostinfo,
			   std::optional<HookInsertHandler> hookinsert,
			   std::optional<EmbedCallback> embed,
			   std::optional<I18NQueryCallback> _i18nQueryCallback)
	{
		OnConnect = [=](auto &&...args)
		{ IF_HASVAL_DISPATCH(procmutex, Connect); };
		OnDisconnect = [=](auto &&...args)
		{ IF_HASVAL_DISPATCH(procmutex, Disconnect); };
		OnCreate = [=](TextThread &thread)
		{
			IF_HASVAL_DISPATCH_1(threadmutex, Create, thread);
			thread.Start();
		};
		OnDestroy = [=](TextThread &thread)
		{
			thread.Stop();
			IF_HASVAL_DISPATCH_1(threadmutex, Destroy, thread);
		};
		TextThread::Output = [=](auto &&...args)
		{ IF_HASVAL_DISPATCH(outputmutex, Output); };
		OnHostInfo = [=](auto &&...args)
		{ IF_HASVAL_DISPATCH(outputmutex, hostinfo); };
		HookInsert = [=](auto &&...args)
		{ IF_HASVAL_DISPATCH(threadmutex, hookinsert); };
		embedcallback = [=](auto &&...args)
		{ IF_HASVAL_DISPATCH(outputmutex, embed); };
		i18nQueryCallback = _i18nQueryCallback.value_or([](auto) { return std::nullopt; });
	}
	bool CheckIfNeedInject(DWORD processId)
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
	void ConnectProcess(DWORD processId)
	{
		if (processId == GetCurrentProcessId())
			return;
		HANDLE hookPipe = CreateNamedPipeW((std::wstring(HOOK_PIPE) + std::to_wstring(processId)).c_str(), PIPE_ACCESS_INBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, 0, PIPE_BUFFER_SIZE, MAXDWORD, &allAccess);
		HANDLE hostPipe = CreateNamedPipeW((std::wstring(HOST_PIPE) + std::to_wstring(processId)).c_str(), PIPE_ACCESS_OUTBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, PIPE_BUFFER_SIZE, 0, MAXDWORD, &allAccess);
		HANDLE pipeAvailableEvent = CreateEventW(&allAccess, FALSE, FALSE, (std::wstring(PIPE_AVAILABLE_EVENT) + std::to_wstring(processId)).c_str());
		SetEvent(pipeAvailableEvent);
		std::thread(__handlepipethread, processId, hookPipe, hostPipe, pipeAvailableEvent).detach();
	}
	void DetachProcess(DWORD processId)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		found->second.Send(HOST_COMMAND_DETACH);
	}
	void InsertPCHooks(DWORD processId, int which)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		found->second.Send(InsertPCHooksCmd(which));
	}
	void InsertHook(DWORD processId, HookParam hp)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		found->second.Send(InsertHookCmd(hp));
	}

	void RemoveHook(DWORD processId, uint64_t address)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		found->second.Send(RemoveHookCmd(address));
	}

	void FindHooks(DWORD processId, SearchParam sp, HookEventHandler HookFound, LPCWSTR addresses)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		if (HookFound)
			found->second.OnHookFound = HookFound;
		static int idx = 0;
		if (sp.search_method == 3)
		{
			if (!addresses)
				addresses = L"";
			auto size = wcslen(addresses) * 2;
			auto name = HOOK_SEARCH_SHARED_MEM + std::to_wstring(GetCurrentProcessId()) + std::to_wstring(idx++);
			auto handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, size + 2, (name).c_str());
			auto ptr = MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, size + 2);
			wcscpy((LPWSTR)ptr, addresses);
			wcscpy(sp.sharememname, name.c_str());
			sp.sharememsize = size + 2;
		}
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
		auto found = prs.find(processId);
		if (found == prs.end())
			return nullptr;
		return found->second.commonsharedmem;
	}
	void AddConsoleOutput(std::wstring text)
	{
		InfoOutput(HOSTINFO::Console, text);
	}
	void InfoOutput(HOSTINFO type, std::wstring text)
	{
		OnHostInfo(type, std::move(text));

		if (type != HOSTINFO::Console)
		{
			switch (type)
			{
			case HOSTINFO::Notification:
				return;
			case HOSTINFO::Warning:
				text = FormatString(L"[%s]", TR[T_WARNING]) + text;
				break;
			case HOSTINFO::EmuGameName:
				text = L"[Game] " + text;
				break;
			}
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
