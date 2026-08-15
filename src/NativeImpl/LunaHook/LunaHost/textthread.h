#pragma once

struct StorageDecoded
{
	std::deque<std::wstring> data;
	size_t count = 0;
	void push_back(size_t maxHistorySize, std::wstring &&text)
	{
		while (count > maxHistorySize && (count - data.front().size() > maxHistorySize))
		{
			count -= data.front().size();
			data.pop_back();
		}
		count += text.size();
		data.push_back(std::move(text));
	}
};

class TextThread
{
public:
	using OutputCallback = std::function<void(TextThread &, std::wstring &)>;
	inline static OutputCallback Output;

	inline static int flushDelay = 100;
	inline static int maxBufferSize = 3000;
	inline static int maxHistorySize = 10'000'000;
	inline static Synchronized<std::set<TextThread *>> syncThreads;

	TextThread(ThreadParam tp, HookParam hp, std::optional<std::wstring> name = {});

	void Start();
	void Stop();
	void Push(BYTE *data, int length);

	const int64_t handle;
	const std::wstring name;
	const ThreadParam tp;
	HookParam hp;
	std::wstring GetHistoryText();
	std::wstring GetLatestText();
	std::optional<DWORD> RunDectectCodePage(BYTE *data, int length);

private:
	Synchronized<StorageDecoded> storageDecoded;
	inline static int threadCounter = 0;

	void Flush();
	std::wstring bufferDecoded;
	std::string UseForDetectRaw;
	BYTE leadByte = 0;
	std::mutex bufferMutex;
	DWORD64 lastPushTime = 0;
	Synchronized<std::vector<std::wstring>> queuedDecodedSentences;
	struct TimerDeleter
	{
		void operator()(HANDLE h) { DeleteTimerQueueTimer(NULL, h, INVALID_HANDLE_VALUE); }
	};
	AutoHandle<TimerDeleter> timer = NULL;
	void UpdateFlushTime(bool recursive = true);
	void FlushBufferToQueue();
};
