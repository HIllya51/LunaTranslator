#include "host.h"
#define HOOK_SEARCH_LENGTH STRING
// #define HOOK_SEARCH_LENGTH 0
using rpc::RpcBlob;
namespace
{
	class ProcessRecord
	{
	public:
		ProcessRecord(DWORD processId, HANDLE pipe) : pipe(pipe),
													  mappedFile2(OpenFileMappingW(FILE_MAP_READ | FILE_MAP_WRITE, FALSE, (EMBED_SHARED_MEM + std::to_wstring(processId)).c_str())),
													  viewMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(processId)),
													  prepareWaiter(CreateEvent(NULL, TRUE, FALSE, NULL))

		{
			commonsharedmem = (CommonSharedMem *)MapViewOfFile(mappedFile2, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, sizeof(CommonSharedMem));
			// 放到构造表里就不行，不知道为何。
		}

		~ProcessRecord()
		{
			UnmapViewOfFile(commonsharedmem);
		}

		template <rpc::Id I, class... A>
		void Send_no_wait(A &&...args)
		{
			std::thread(
				[this, args...]()
				{
					rpc::call<I>(pipe, args...);
				})
				.detach();
		}
		template <rpc::Id I, class... A>
		void Send(A &&...args)
		{
			std::thread(
				[this, args...]()
				{
					WaitForSingleObject(prepareWaiter, INFINITE);
					rpc::call<I>(pipe, args...);
				})
				.detach();
		}

		Host::HookEventHandler OnHookFound = [](auto, auto) {};

		CommonSharedMem *commonsharedmem;
		AutoHandle<> prepareWaiter;

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
	Host::EmuGameInfoCallback OnEmuGameInfo;
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
		GUID get_guid;
		ReadFile(hookPipe, &get_guid, sizeof(get_guid), &bytesRead, nullptr);
		if (!IsEqualGUID(get_guid, compatible_sig))
			Host::InfoOutput(HOSTINFO::Warning, TR[UNMATCHABLEVERSION]);
	}
	void CheckFileHelper(HANDLE hookPipe, HANDLE hostPipe)
	{
		DWORD count;
		int size;
		ReadFile(hookPipe, &size, sizeof(size), &count, nullptr);
		std::wstring currpath;
		currpath.resize(size);
		ReadFile(hookPipe, currpath.data(), 2 * size, &count, nullptr);
		auto handler = [&](auto &&entry)
		{
			auto fname = entry.wstring();
			size = fname.size();
			WriteFile(hostPipe, &size, 4, &count, nullptr);
			WriteFile(hostPipe, fname.c_str(), 2 * size, &count, nullptr);
		};

		for (const auto &entry : std::filesystem::directory_iterator(currpath))
		{
			handler(entry.path().filename());
			if (!std::filesystem::is_directory(entry.path()))
				continue;
			for (const auto &sub_entry : std::filesystem::directory_iterator(entry))
				handler(std::filesystem::relative(sub_entry.path(), currpath));
		}
		size = -1;
		WriteFile(hostPipe, &size, 4, &count, nullptr);
	}
	void registerHostRpcHandlers()
	{
		rpc::on_ctx<rpc::Id::NotifyPreparedOK>([](DWORD pid)
											   { SetEvent(processRecordsByIds->at(pid).prepareWaiter); });

		rpc::on_ctx<rpc::Id::RequestI18N>([](DWORD pid, LANG_STRINGS_HOOK enum_, std::string key)
										  {
			auto ret = WideStringToString(i18nQueryCallback(StringToWideString(key)).value_or(L""));
			processRecordsByIds->at(pid).Send_no_wait<rpc::Id::RespondI18N>(enum_, ret); });

		rpc::on_ctx<rpc::Id::NotifyHookFound>([](DWORD pid, HookParam hp, RpcBlob text)
											  {
			auto OnHookFound = processRecordsByIds->at(pid).OnHookFound;
			auto info_text = (wchar_t *)text.data;
			std::wstring wide = info_text;
			if (wide.size() > HOOK_SEARCH_LENGTH)
			{
				wcscpy_s(hp.hookcode, HOOKCODE_LEN, HookCode::Generate(hp, pid).c_str());
				OnHookFound(hp, std::move(wide));
			}
			if (!(hp.type & CSHARP_STRING))
			{
				hp.type &= ~CODEC_UTF16;
				if (auto converted = StringToWideString((char *)info_text, hp.codepage))
					if (converted->size() > HOOK_SEARCH_LENGTH)
					{
						wcscpy_s(hp.hookcode, HOOKCODE_LEN, HookCode::Generate(hp, pid).c_str());
						OnHookFound(hp, std::move(converted.value()));
					}
				if (auto converted = StringToWideString((char *)info_text, hp.codepage = CP_UTF8))
					if (converted->size() > HOOK_SEARCH_LENGTH)
					{
						wcscpy_s(hp.hookcode, HOOKCODE_LEN, HookCode::Generate(hp, pid).c_str());
						OnHookFound(hp, std::move(converted.value()));
					}
			} });

		rpc::on_ctx<rpc::Id::NotifyHookRemoved>([](DWORD pid, uint64_t address)
												{
			auto sm = Host::GetCommonSharedMem(pid);
			if (!sm)return;
			for (int i = 0; i < ARRAYSIZE(sm->embedtps); i++)
				if (sm->embedtps[i].use && (sm->embedtps[i].tp.addr == address) && (sm->embedtps[i].tp.processId == pid))
					ZeroMemory(sm->embedtps + i, sizeof(sm->embedtps[i]));
		RemoveThreads([&](ThreadParam tp)
						{ return tp.processId == pid && tp.addr == address; }); });

		rpc::on_ctx<rpc::Id::NotifyHookInserting>(HookInsert);

		rpc::on<rpc::Id::NotifyEmuGameInfo>([](std::string id, std::string title, std::string version)
											{ OnEmuGameInfo(StringToWideString(id), StringToWideString(title), StringToWideString(version)); });

		rpc::on<rpc::Id::NotifyText>([](HOSTINFO type, UINT codepage, std::string message)
									 { Host::InfoOutput(type, StringToWideString(message, codepage).value_or(L"")); });

		rpc::on<rpc::Id::NotifyTextW>(Host::InfoOutput);

		rpc::on_ctx<rpc::Id::OutputText>([](DWORD pid, ThreadParam tp, HookParam hp, uint64_t type, RpcBlob data)
										 {
											 auto length = data.size;
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
													 return;
												 } // probably garbage data in pipe, try again
												 OnCreate(thread->second);
											 }

											 thread->second.hp.type = type;
											 thread->second.hp.detectedCodepage = hp.detectedCodepage;
											 if (auto codepage = thread->second.RunDectectCodePage(data.data, length))
												 processRecordsByIds->at(pid).Send<rpc::Id::SetDetectedCodepage>(codepage.value(), hp.address);
											 thread->second.Push(data.data, length);

											 auto &thp = thread->second.hp;
											 if (!(thp.type & EMBED_ABLE && Host::CheckIsUsingEmbed(thread->second.tp)))
												 return;
											 auto sm = Host::GetCommonSharedMem(tp.processId);
											 if (!sm)
												 return;
											 if (sm->clearText)
												 return;
											 auto codepage = Host::defaultCodepage ? Host::defaultCodepage : thp.detectedCodepage;
											 if (thp.isAscii() && !codepage)
												 return;
											 auto t = commonparsestring(data.data, length, &thp, codepage);
											 if (!t)
												 return;
											 auto text = t.value();
											 if (text.empty())
												 return;
											 embedcallback(text, tp); });
	}

	void __handlepipethread(DWORD processId, HANDLE hookPipe, HANDLE hostPipe, HANDLE pipeAvailableEvent)
	{
		ConnectNamedPipe(hookPipe, nullptr);
		CloseHandle(pipeAvailableEvent);

		VersionMatchCheck(hookPipe);
		CheckFileHelper(hookPipe, hostPipe);

		processRecordsByIds->try_emplace(processId, processId, hostPipe);
		OnConnect(processId);
		Host::AddConsoleOutput(FormatString(TR[PROC_CONN], processId));
		if (Host::enablePCHooks)
		{
			processRecordsByIds->at(processId).Send<rpc::Id::InsertPCHooks>(0);
			processRecordsByIds->at(processId).Send<rpc::Id::InsertPCHooks>(1);
		}
		BYTE buffer[PIPE_BUFFER_SIZE] = {};
		DWORD bytesRead;
		while (ReadFile(hookPipe, buffer, PIPE_BUFFER_SIZE, &bytesRead, nullptr))
			rpc::dispatch(buffer, bytesRead, processId);

		RemoveThreads([&](ThreadParam tp)
					  { return tp.processId == processId; });
		OnDisconnect(processId);
		Host::AddConsoleOutput(FormatString(TR[PROC_DISCONN], processId));
		SetEvent(processRecordsByIds->at(processId).prepareWaiter);
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
			rcd.Send<rpc::Id::QueryI18N>();
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
			   std::optional<I18NQueryCallback> _i18nQueryCallback, std::optional<EmuGameInfoCallback> emuGameInfoCallback)
	{
		OnEmuGameInfo = [=](auto &&...args)
		{ IF_HASVAL_DISPATCH(procmutex, emuGameInfoCallback); };
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
		i18nQueryCallback = _i18nQueryCallback.value_or([](auto)
														{ return std::nullopt; });
		registerHostRpcHandlers();
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
		found->second.Send<rpc::Id::Detach>();
	}
	void InsertPCHooks(DWORD processId, int which)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		found->second.Send<rpc::Id::InsertPCHooks>(which);
	}
	void InsertHook(DWORD processId, HookParam hp)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		found->second.Send<rpc::Id::NewHook>(hp);
	}

	void RemoveHook(DWORD processId, uint64_t address)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return;
		found->second.Send<rpc::Id::RemoveHook>(address);
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
			memcpy(ptr, addresses, size + 2);
			wcscpy_s(sp.sharememname, ARRAYSIZE(sp.sharememname), name.c_str());
			sp.sharememsize = size + 2;
		}
		prs.at(processId).Send<rpc::Id::FindHook>(sp);
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
	void BroadCastCodePage()
	{
		for (auto &[pid, rcd] : processRecordsByIds.Acquire().contents)
		{
			auto m = rcd.commonsharedmem;
			if (!m)
				continue;
			m->codepage = Host::defaultCodepage;
		}
	}

	CommonSharedMem *GetCommonSharedMem(DWORD processId)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		auto found = prs.find(processId);
		if (found == prs.end())
			return nullptr;
		return found->second.commonsharedmem;
	}
	void AddConsoleOutput(const std::wstring &text)
	{
		InfoOutput(HOSTINFO::Console, text);
	}
	void InfoOutput(HOSTINFO type, const std::wstring &text)
	{
		OnHostInfo(type, text);

		switch (type)
		{
		case HOSTINFO::Console:
		case HOSTINFO::EmuConnected:
			return;
		case HOSTINFO::Warning:
		case HOSTINFO::EmuWarning:
			OnHostInfo(HOSTINFO::Console, FormatString(L"[%s]", TR[T_WARNING]) + text);
			break;
		default:

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
