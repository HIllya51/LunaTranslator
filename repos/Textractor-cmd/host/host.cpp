#include "host.h"
#include "defs.h"
#include "module.h"
#include "hookcode.h"
#include "../texthook/texthook.h"

extern const wchar_t* ALREADY_INJECTED;
extern const wchar_t* NEED_32_BIT;
extern const wchar_t* NEED_64_BIT;
extern const wchar_t* INJECT_FAILED;
extern const wchar_t* CONSOLE;
extern const wchar_t* CLIPBOARD;

namespace
{
	class ProcessRecord
	{
	public:
		ProcessRecord(DWORD processId, HANDLE pipe) :
			pipe(pipe),
			mappedFile(OpenFileMappingW(FILE_MAP_READ, FALSE, (ITH_SECTION_ + std::to_wstring(processId)).c_str())),
			view(*(const TextHook(*)[MAX_HOOK])MapViewOfFile(mappedFile, FILE_MAP_READ, 0, 0, HOOK_SECTION_SIZE / 2)), // jichi 1/16/2015: Changed to half to hook section size
			viewMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(processId))
		{}

		~ProcessRecord()
		{
			UnmapViewOfFile(view);
		}

		TextHook GetHook(uint64_t addr)
		{
			if (!view) return {};
			std::scoped_lock lock(viewMutex);
			for (auto hook : view) if (hook.address == addr) return hook;
			return {};
		}

		template <typename T>
		void Send(T data)
		{
			static_assert(sizeof(data) < PIPE_BUFFER_SIZE);
			std::thread([=]
			{
				WriteFile(pipe, &data, sizeof(data), DUMMY, nullptr);
			}).detach();
		}

		Host::HookEventHandler OnHookFound = [](HookParam hp, std::wstring text)
		{
			Host::AddConsoleOutput(HookCode::Generate(hp) + L": " + text);
		};

	private:
		HANDLE pipe;
		AutoHandle<> mappedFile;
		const TextHook(&view)[MAX_HOOK];
		WinMutex viewMutex;
	};

	size_t HashThreadParam(ThreadParam tp) { return std::hash<int64_t>()(tp.processId + tp.addr) + std::hash<int64_t>()(tp.ctx + tp.ctx2); }
	Synchronized<std::unordered_map<ThreadParam, TextThread, Functor<HashThreadParam>>> textThreadsByParams;
	Synchronized<std::unordered_map<DWORD, ProcessRecord>> processRecordsByIds;

	Host::ProcessEventHandler OnConnect, OnDisconnect;
	Host::ThreadEventHandler OnCreate, OnDestroy;

	void RemoveThreads(std::function<bool(ThreadParam)> removeIf)
	{
		std::vector<TextThread*> threadsToRemove;
		for (auto& [tp, thread] : textThreadsByParams.Acquire().contents) if (removeIf(tp)) threadsToRemove.push_back(&thread);
		for (auto thread : threadsToRemove)
		{
			OnDestroy(*thread);
			textThreadsByParams->erase(thread->tp);
		}
	}

	void CreatePipe()
	{
		std::thread([]
		{
			struct PipeCloser { void operator()(HANDLE h) { DisconnectNamedPipe(h); CloseHandle(h); } };
			AutoHandle<PipeCloser>
				hookPipe = CreateNamedPipeW(HOOK_PIPE, PIPE_ACCESS_INBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, 0, PIPE_BUFFER_SIZE, MAXDWORD, &allAccess),
				hostPipe = CreateNamedPipeW(HOST_PIPE, PIPE_ACCESS_OUTBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, PIPE_UNLIMITED_INSTANCES, PIPE_BUFFER_SIZE, 0, MAXDWORD, &allAccess);
			static AutoHandle<> pipeAvailableEvent = CreateEventW(&allAccess, FALSE, FALSE, PIPE_AVAILABLE_EVENT);
			SetEvent(pipeAvailableEvent);
			ConnectNamedPipe(hookPipe, nullptr);

			BYTE buffer[PIPE_BUFFER_SIZE] = {};
			DWORD bytesRead, processId;
			ReadFile(hookPipe, &processId, sizeof(processId), &bytesRead, nullptr);
			processRecordsByIds->try_emplace(processId, processId, hostPipe);
			OnConnect(processId);

			CreatePipe();

			while (ReadFile(hookPipe, buffer, PIPE_BUFFER_SIZE, &bytesRead, nullptr))
				switch (*(HostNotificationType*)buffer)
				{
				case HOST_NOTIFICATION_FOUND_HOOK:
				{
					auto info = *(HookFoundNotif*)buffer;
					auto OnHookFound = processRecordsByIds->at(processId).OnHookFound;
					std::wstring wide = info.text;
					if (wide.size() > STRING) OnHookFound(info.hp, std::move(info.text));
					info.hp.type &= ~USING_UNICODE;
					if (auto converted = StringToWideString((char*)info.text, info.hp.codepage))
						if (converted->size() > STRING) OnHookFound(info.hp, std::move(converted.value()));
					if (auto converted = StringToWideString((char*)info.text, info.hp.codepage = CP_UTF8))
						if (converted->size() > STRING) OnHookFound(info.hp, std::move(converted.value()));
				}
				break;
				case HOST_NOTIFICATION_RMVHOOK:
				{
					auto info = *(HookRemovedNotif*)buffer;
					RemoveThreads([&](ThreadParam tp) { return tp.processId == processId && tp.addr == info.address; });
				}
				break;
				case HOST_NOTIFICATION_TEXT:
				{
					auto info = *(ConsoleOutputNotif*)buffer;
					Host::AddConsoleOutput(StringToWideString(info.message));
				}
				break;
				default:
				{
					auto tp = *(ThreadParam*)buffer;
					auto textThreadsByParams = ::textThreadsByParams.Acquire();
					auto thread = textThreadsByParams->find(tp);
					if (thread == textThreadsByParams->end())
					{
						try { thread = textThreadsByParams->try_emplace(tp, tp, processRecordsByIds->at(tp.processId).GetHook(tp.addr).hp).first; }
						catch (std::out_of_range) { continue; } // probably garbage data in pipe, try again
						OnCreate(thread->second);
					}
					thread->second.Push(buffer + sizeof(tp), bytesRead - sizeof(tp));
				}
				break;
				}

			RemoveThreads([&](ThreadParam tp) { return tp.processId == processId; });
			OnDisconnect(processId);
			processRecordsByIds->erase(processId);
		}).detach();
	}
}

namespace Host
{
	void Start(ProcessEventHandler Connect, ProcessEventHandler Disconnect, ThreadEventHandler Create, ThreadEventHandler Destroy, TextThread::OutputCallback Output)
	{
		OnConnect = Connect;
		OnDisconnect = Disconnect;
		OnCreate = [Create](TextThread& thread) { Create(thread); thread.Start(); };
		OnDestroy = [Destroy](TextThread& thread) { thread.Stop(); Destroy(thread); };
		TextThread::Output = Output;

		textThreadsByParams->try_emplace(console, console, HookParam{}, CONSOLE);
		OnCreate(GetThread(console));
		textThreadsByParams->try_emplace(clipboard, clipboard, HookParam{}, CLIPBOARD);
		OnCreate(GetThread(clipboard));

		CreatePipe();

		static AutoHandle<> clipboardUpdate = CreateEventW(nullptr, FALSE, TRUE, NULL);
		SetWindowsHookExW(WH_GETMESSAGE, [](int statusCode, WPARAM wParam, LPARAM lParam)
		{
			if (statusCode == HC_ACTION && wParam == PM_REMOVE && ((MSG*)lParam)->message == WM_CLIPBOARDUPDATE) SetEvent(clipboardUpdate);
			return CallNextHookEx(NULL, statusCode, wParam, lParam);
		}, NULL, GetCurrentThreadId());
		std::thread([]
		{
			while (WaitForSingleObject(clipboardUpdate, INFINITE) == WAIT_OBJECT_0)
			{
				std::optional<std::wstring> clipboardText;
				for (int retry = 0; !clipboardText && retry < 3; ++retry) // retry loop in case something else is using the clipboard
				{
					Sleep(10);
					if (!IsClipboardFormatAvailable(CF_UNICODETEXT)) continue;
					if (!OpenClipboard(NULL)) continue;
					if (AutoHandle<Functor<GlobalUnlock>> clipboard = GetClipboardData(CF_UNICODETEXT)) clipboardText = (wchar_t*)GlobalLock(clipboard);
					CloseClipboard();
				}
				if (clipboardText) GetThread(clipboard).AddSentence(std::move(clipboardText.value()));
			}
			throw;
		}).detach();
	}

	void InjectProcess(DWORD processId)
	{
		std::thread([processId]
		{
			if (processId == GetCurrentProcessId()) return;

			WinMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(processId));
			if (GetLastError() == ERROR_ALREADY_EXISTS) return AddConsoleOutput(ALREADY_INJECTED);

			if (AutoHandle<> process = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processId))
			{
#ifdef _WIN64
				BOOL invalidProcess = FALSE;
				IsWow64Process(process, &invalidProcess);
				if (invalidProcess) return AddConsoleOutput(NEED_32_BIT);
#endif
				static std::wstring location = std::filesystem::path(GetModuleFilename().value()).replace_filename(ITH_DLL);
				if (LPVOID remoteData = VirtualAllocEx(process, nullptr, (location.size() + 1) * sizeof(wchar_t), MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE))
				{
					WriteProcessMemory(process, remoteData, location.c_str(), (location.size() + 1) * sizeof(wchar_t), nullptr);
					if (AutoHandle<> thread = CreateRemoteThread(process, nullptr, 0, (LPTHREAD_START_ROUTINE)LoadLibraryW, remoteData, 0, nullptr)) WaitForSingleObject(thread, INFINITE);
					else if (GetLastError() == ERROR_ACCESS_DENIED) AddConsoleOutput(NEED_64_BIT); // https://stackoverflow.com/questions/16091141/createremotethread-access-denied
					VirtualFreeEx(process, remoteData, 0, MEM_RELEASE);
					return;
				}
			}

			AddConsoleOutput(INJECT_FAILED);
		}).detach();
	}

	void DetachProcess(DWORD processId)
	{
		processRecordsByIds->at(processId).Send(HOST_COMMAND_DETACH);
	}

	void InsertHook(DWORD processId, HookParam hp)
	{
		processRecordsByIds->at(processId).Send(InsertHookCmd(hp));
	}

	void RemoveHook(DWORD processId, uint64_t address)
	{
		processRecordsByIds->at(processId).Send(RemoveHookCmd(address));
	}

	void FindHooks(DWORD processId, SearchParam sp, HookEventHandler HookFound)
	{
		if (HookFound) processRecordsByIds->at(processId).OnHookFound = HookFound;
		processRecordsByIds->at(processId).Send(FindHookCmd(sp));
	}

	TextThread& GetThread(ThreadParam tp)
	{
		return textThreadsByParams->at(tp);
	}

	TextThread* GetThread(int64_t handle)
	{
		for (auto& [tp, thread] : textThreadsByParams.Acquire().contents) if (thread.handle == handle) return &thread;
		return nullptr;	
	}

	void AddConsoleOutput(std::wstring text)
	{
		GetThread(console).AddSentence(std::move(text));
	}
}
