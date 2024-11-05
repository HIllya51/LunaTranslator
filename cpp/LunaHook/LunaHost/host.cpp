#include "host.h"
typedef LONG NTSTATUS;
#include "yapi.hpp"
#include "Lang/Lang.h"
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

		Host::HookEventHandler OnHookFound = [](HookParam hp, std::wstring text)
		{
			Host::AddConsoleOutput(std::wstring(hp.hookcode) + L": " + text);
		};

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
	Host::ConsoleHandler OnConsole = 0;
	Host::ConsoleHandler OnWarning = 0;
	Host::HookInsertHandler HookInsert = 0;
	Host::EmbedCallback embedcallback = 0;
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
	BOOL Is64BitProcess(HANDLE ph)
	{
		BOOL f64bitProc = FALSE;
		if (detail::Is64BitOS())
		{
			f64bitProc = !(IsWow64Process(ph, &f64bitProc) && f64bitProc);
		}
		return f64bitProc;
	}
	void CreatePipe(int pid)
	{
		HANDLE
		hookPipe = CreateNamedPipeW((std::wstring(HOOK_PIPE) + std::to_wstring(pid)).c_str(), PIPE_ACCESS_INBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, 0, PIPE_BUFFER_SIZE, MAXDWORD, &allAccess),
		hostPipe = CreateNamedPipeW((std::wstring(HOST_PIPE) + std::to_wstring(pid)).c_str(), PIPE_ACCESS_OUTBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, PIPE_BUFFER_SIZE, 0, MAXDWORD, &allAccess);
		HANDLE pipeAvailableEvent = CreateEventW(&allAccess, FALSE, FALSE, (std::wstring(PIPE_AVAILABLE_EVENT) + std::to_wstring(pid)).c_str());

		Host::AddConsoleOutput((std::wstring(PIPE_AVAILABLE_EVENT) + std::to_wstring(pid)));
		SetEvent(pipeAvailableEvent);
		std::thread([hookPipe, hostPipe, pipeAvailableEvent]
					{
			ConnectNamedPipe(hookPipe, nullptr);
			CloseHandle(pipeAvailableEvent);
			BYTE buffer[PIPE_BUFFER_SIZE] = {};
			DWORD bytesRead, processId;
			ReadFile(hookPipe, &processId, sizeof(processId), &bytesRead, nullptr);
			processRecordsByIds->try_emplace(processId, processId, hostPipe);
			OnConnect(processId);
			Host::AddConsoleOutput(FormatString(PROC_CONN,processId));
			//CreatePipe();

			while (ReadFile(hookPipe, buffer, PIPE_BUFFER_SIZE, &bytesRead, nullptr))
				switch (*(HostNotificationType*)buffer)
				{
				case HOST_NOTIFICATION_FOUND_HOOK:
				{
					auto info = *(HookFoundNotif*)buffer;
					auto OnHookFound = processRecordsByIds->at(processId).OnHookFound; 
					std::wstring wide = info.text;
					if (wide.size() > STRING) {
						wcscpy_s(info.hp.hookcode,HOOKCODE_LEN, HookCode::Generate(info.hp, processId).c_str());
						OnHookFound(info.hp, std::move(info.text));
					}
					info.hp.type &= ~CODEC_UTF16;
					if (auto converted = StringToWideString((char*)info.text, info.hp.codepage))
						if (converted->size() > STRING) 
						{
							wcscpy_s(info.hp.hookcode,HOOKCODE_LEN, HookCode::Generate(info.hp, processId).c_str());
							OnHookFound(info.hp, std::move(converted.value()));
						}
					if (auto converted = StringToWideString((char*)info.text, info.hp.codepage = CP_UTF8))
						if (converted->size() > STRING)
						{
							wcscpy_s(info.hp.hookcode,HOOKCODE_LEN, HookCode::Generate(info.hp, processId).c_str());
							OnHookFound(info.hp, std::move(converted.value()));
						}
				}
				break;
				case HOST_NOTIFICATION_RMVHOOK:
				{
					auto info = *(HookRemovedNotif*)buffer;
					RemoveThreads([&](ThreadParam tp) { return tp.processId == processId && tp.addr == info.address; });
				}
				break;
				case HOST_NOTIFICATION_INSERTING_HOOK:
				{
					if(HookInsert){
						auto info = (HookInsertingNotif*)buffer;
            			HookInsert(processId, info->addr,info->hookcode);
					}
				}
				break;
				case HOST_NOTIFICATION_TEXT:
				{
					auto info = *(ConsoleOutputNotif*)buffer;
					Host::AddConsoleOutput(StringToWideString(info.message));
				}
				break;
				case HOST_NOTIFICATION_WARNING:
				{
					auto info = *(WarningNotif*)buffer;
					Host::Warning(StringToWideString(info.message));
				}
				break;
				default:
				{
					auto data=(TextOutput_T*)buffer;
					auto length= bytesRead - sizeof(TextOutput_T);
					auto tp = data->tp;
					auto hp=data->hp;
					auto _textThreadsByParams=textThreadsByParams.Acquire();
					
					auto thread = _textThreadsByParams->find(tp);
					if (thread == _textThreadsByParams->end())
					{
						try { thread = _textThreadsByParams->try_emplace(tp, tp, hp).first; }
						catch (std::out_of_range) { continue; } // probably garbage data in pipe, try again
						OnCreate(thread->second);
					}
					 
					thread->second.hp.type=data->type;
					thread->second.Push(data->data, length);

					if(embedcallback){
						auto & hp=thread->second.hp;
						if(hp.type&EMBED_ABLE && Host::CheckIsUsingEmbed(thread->second.tp)){
							if (auto t=commonparsestring(data->data,length,&hp,Host::defaultCodepage)){
								auto text=t.value();
								if(text.size()){
									embedcallback(text,tp);
								}
							} 
						}
						
					}
				}
				break;
				}

			RemoveThreads([&](ThreadParam tp) { return tp.processId == processId; });
			OnDisconnect(processId);
			Host::AddConsoleOutput(FormatString(PROC_DISCONN,processId));
			processRecordsByIds->erase(processId); })
			.detach();
	}
}

namespace Host
{
	std::mutex threadmutex;
	std::mutex outputmutex;
	std::mutex procmutex;
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
			OnCreate(textThreadsByParams->try_emplace(console, console, HookParam{}, CONSOLE).first->second);
			Host::AddConsoleOutput(ProjectHomePage);
		}

		// CreatePipe();
	}
	void StartEx(std::optional<ProcessEventHandler> Connect, std::optional<ProcessEventHandler> Disconnect, std::optional<ThreadEventHandler> Create, std::optional<ThreadEventHandler> Destroy, std::optional<TextThread::OutputCallback> Output, std::optional<ConsoleHandler> console, std::optional<HookInsertHandler> hookinsert, std::optional<EmbedCallback> embed, std::optional<ConsoleHandler> warning)
	{
		Start(Connect.value_or([](auto) {}), Disconnect.value_or([](auto) {}), Create.value_or([](auto &) {}), Destroy.value_or([](auto &) {}), Output.value_or([](auto &, auto &)
																																								{ return false; }),
			  !console);
		if (warning)
			OnWarning = warning.value();
		if (console)
			OnConsole = [=](auto &&...args)
			{std::lock_guard _(outputmutex);console.value()(std::forward<decltype(args)>(args)...); };
		if (hookinsert)
			HookInsert = [=](auto &&...args)
			{std::lock_guard _(threadmutex);hookinsert.value()(std::forward<decltype(args)>(args)...); };
		if (embed)
			embedcallback = [=](auto &&...args)
			{std::lock_guard _(outputmutex);embed.value()(std::forward<decltype(args)>(args)...); };
	}
	constexpr auto PROCESS_INJECT_ACCESS = (PROCESS_CREATE_THREAD |
											PROCESS_QUERY_INFORMATION |
											PROCESS_VM_OPERATION |
											PROCESS_VM_WRITE |
											PROCESS_VM_READ);
	bool SafeInject(HANDLE process, const std::wstring &location)
	{
// #ifdef _WIN64
#if 0
			BOOL invalidProcess = FALSE;
			IsWow64Process(process, &invalidProcess);
			if (invalidProcess) return AddConsoleOutput(NEED_32_BIT);
#endif
		bool succ = false;
		if (LPVOID remoteData = VirtualAllocEx(process, nullptr, (location.size() + 1) * sizeof(wchar_t), MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE))
		{
			WriteProcessMemory(process, remoteData, location.c_str(), (location.size() + 1) * sizeof(wchar_t), nullptr);
			if (AutoHandle<> thread = CreateRemoteThread(process, nullptr, 0, (LPTHREAD_START_ROUTINE)LoadLibraryW, remoteData, 0, nullptr))
			{
				WaitForSingleObject(thread, INFINITE);
				succ = true;
			}
			else if (GetLastError() == ERROR_ACCESS_DENIED)
			{
				AddConsoleOutput(NEED_64_BIT); // https://stackoverflow.com/questions/16091141/createremotethread-access-denied
				succ = false;
			}
			VirtualFreeEx(process, remoteData, 0, MEM_RELEASE);
		}
		return succ;
	}
	bool UnSafeInject(HANDLE process, const std::wstring &location)
	{

		DWORD64 injectedDll;
		yapi::YAPICall LoadLibraryW(process, _T("kernel32.dll"), "LoadLibraryW");
		if (x64)
			injectedDll = LoadLibraryW.Dw64()(location.c_str());
		else
			injectedDll = LoadLibraryW(location.c_str());
		if (injectedDll)
			return true;
		return false;
	}
	bool CheckProcess(DWORD processId)
	{
		if (processId == GetCurrentProcessId())
			return false;

		WinMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(processId));
		if (GetLastError() == ERROR_ALREADY_EXISTS)
		{
			AddConsoleOutput(ALREADY_INJECTED);
			return false;
		}
		return true;
	}
	bool InjectDll(DWORD processId, const std::wstring locationX)
	{
		AutoHandle<> process = OpenProcess(PROCESS_INJECT_ACCESS, FALSE, processId);
		if (!process)
			return false;
		bool proc64 = Is64BitProcess(process);
		auto dllname = proc64 ? LUNA_HOOK_DLL_64 : LUNA_HOOK_DLL_32;
		std::wstring location = locationX.size() ? (locationX + L"\\" + dllname) : std::filesystem::path(getModuleFilename().value()).replace_filename(dllname);
		AddConsoleOutput(location);
		if (proc64 == x64)
		{
			return (SafeInject(process, location));
		}
		else
		{
			return (UnSafeInject(process, location));
		}
	}
	bool CreatePipeAndCheck(DWORD processId)
	{
		CreatePipe(processId);
		return CheckProcess(processId);
	}

	void InjectProcess(DWORD processId, const std::wstring locationX)
	{

		auto check = CreatePipeAndCheck(processId);
		if (check == false)
			return;

		std::thread([=]
					{
			if(InjectDll(processId,locationX))return ;
			AddConsoleOutput(INJECT_FAILED); })
			.detach();
	}

	void DetachProcess(DWORD processId)
	{
		auto &prs = processRecordsByIds.Acquire().contents;
		if (prs.find(processId) == prs.end())
			return;
		prs.at(processId).Send(HOST_COMMAND_DETACH);
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
		if (OnConsole)
			OnConsole(std::move(text));
		else
			GetThread(console).AddSentence(std::move(text));
	}
	void Warning(std::wstring text)
	{
		if (OnWarning)
			OnWarning(text);
		AddConsoleOutput(L"[Warning] " + text);
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
