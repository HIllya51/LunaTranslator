#pragma once

#include "types.h"

class TextThread
{
public:
	using OutputCallback = bool(*)(TextThread&, std::wstring&);
	inline static OutputCallback Output;

	inline static bool filterRepetition = false;
	inline static int flushDelay = 100; // flush every 500ms by default
	inline static int maxBufferSize = 3000;
	inline static int maxHistorySize = 10'000'000;

	TextThread(ThreadParam tp, HookParam hp, std::optional<std::wstring> name = {});

	void Start();
	void Stop();
	void AddSentence(std::wstring sentence);
	void Push(BYTE* data, int length);
	void Push(const wchar_t* data);

	Synchronized<std::wstring> storage;
	const int64_t handle;
	const std::wstring name;
	const ThreadParam tp;
	const HookParam hp;

private:
	inline static int threadCounter = 0;

	void Flush();

	std::wstring buffer;
	BYTE leadByte = 0;
	std::unordered_set<wchar_t> repeatingChars;
	std::mutex bufferMutex;
	DWORD64 lastPushTime = 0;
	Synchronized<std::vector<std::wstring>> queuedSentences;
	struct TimerDeleter { void operator()(HANDLE h) { DeleteTimerQueueTimer(NULL, h, INVALID_HANDLE_VALUE); } };
	AutoHandle<TimerDeleter> timer = NULL;
};
