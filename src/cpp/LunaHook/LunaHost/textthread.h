#pragma once

class TextThread
{
public:
	using OutputCallback = std::function<void(TextThread &, std::wstring &)>;
	inline static OutputCallback Output;

	inline static bool filterRepetition = false;
	inline static int flushDelay = 100;
	inline static int maxBufferSize = 3000;
	inline static int maxHistorySize = 10'000'000;
	inline static Synchronized<std::set<TextThread *>> syncThreads;

	TextThread(ThreadParam tp, HookParam hp, std::optional<std::wstring> name = {});

	void Start();
	void Stop();
	void AddSentence(std::wstring sentence);
	void Push(BYTE *data, int length);
	void Push(const wchar_t *data);

	Synchronized<std::wstring> storage;
	Synchronized<std::wstring> latest;
	const int64_t handle;
	const std::wstring name;
	const ThreadParam tp;
	HookParam hp;

private:
	inline static int threadCounter = 0;

	void Flush();

	std::wstring buffer;
	BYTE leadByte = 0;
	std::unordered_set<wchar_t> repeatingChars;
	std::mutex bufferMutex;
	DWORD64 lastPushTime = 0;
	Synchronized<std::vector<std::wstring>> queuedSentences;
	struct TimerDeleter
	{
		void operator()(HANDLE h) { DeleteTimerQueueTimer(NULL, h, INVALID_HANDLE_VALUE); }
	};
	AutoHandle<TimerDeleter> timer = NULL;
	void UpdateFlushTime(bool recursive = true);
};
