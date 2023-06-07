#include "textthread.h"
#include "host.h"

extern const wchar_t* INVALID_CODEPAGE;

// return true if repetition found (see https://github.com/Artikash/Textractor/issues/40)
static bool RemoveRepetition(std::wstring& text)
{
	wchar_t* end = text.data() + text.size();
	for (int length = text.size() / 3; length > 6; --length)
		if (memcmp(end - length * 3, end - length * 2, length * sizeof(wchar_t)) == 0 && memcmp(end - length * 3, end - length * 1, length * sizeof(wchar_t)) == 0)
			return RemoveRepetition(text = std::wstring(end - length, length)), true;
	return false;
}

TextThread::TextThread(ThreadParam tp, HookParam hp, std::optional<std::wstring> name) :
	handle(threadCounter++),
	name(name.value_or(StringToWideString(hp.name))),
	tp(tp),
	hp(hp)
{}

void TextThread::Start()
{
	CreateTimerQueueTimer(&timer, NULL, [](void* This, auto) { ((TextThread*)This)->Flush(); }, this, 10, 10, WT_EXECUTELONGFUNCTION);
}

void TextThread::Stop()
{
	timer = NULL;
}

void TextThread::AddSentence(std::wstring sentence)
{
	queuedSentences->emplace_back(std::move(sentence));
}

void TextThread::Push(BYTE* data, int length)
{
	if (length < 0) return;
	std::scoped_lock lock(bufferMutex);

	BYTE doubleByteChar[2];
	if (length == 1) // doublebyte characters must be processed as pairs
	{
		if (leadByte)
		{
			doubleByteChar[0] = leadByte;
			doubleByteChar[1] = data[0];
			data = doubleByteChar;
			length = 2;
			leadByte = 0;
		}
		else if (IsDBCSLeadByteEx(hp.codepage ? hp.codepage : Host::defaultCodepage, data[0]))
		{
			leadByte = data[0];
			length = 0;
		}
	}

	if (hp.type & HEX_DUMP) for (int i = 0; i < length; i += sizeof(short)) buffer.append(FormatString(L"%04hX ", *(short*)(data + i)));
	else if (hp.type & USING_UNICODE) buffer.append((wchar_t*)data, length / sizeof(wchar_t));
	else if (auto converted = StringToWideString(std::string((char*)data, length), hp.codepage ? hp.codepage : Host::defaultCodepage)) buffer.append(converted.value());
	else Host::AddConsoleOutput(INVALID_CODEPAGE);
	if (hp.type & FULL_STRING) buffer.push_back(L'\n');
	lastPushTime = GetTickCount64();
	
	if (filterRepetition)
	{
		if (std::all_of(buffer.begin(), buffer.end(), [&](wchar_t ch) { return repeatingChars.find(ch) != repeatingChars.end(); })) buffer.clear();
		if (RemoveRepetition(buffer)) // sentence repetition detected, which means the entire sentence has already been received
		{
			repeatingChars = std::unordered_set(buffer.begin(), buffer.end());
			AddSentence(std::move(buffer));
			buffer.clear();
		}
	}

	if (flushDelay == 0 && hp.type & FULL_STRING)
	{
		AddSentence(std::move(buffer));
		buffer.clear();
	}
}

void TextThread::Push(const wchar_t* data)
{
	std::scoped_lock lock(bufferMutex);
	// not sure if this should filter repetition
	lastPushTime = GetTickCount64();
	buffer += data;
}

void TextThread::Flush()
{
	{
		auto storage = this->storage.Acquire();
		if (storage->size() > maxHistorySize) storage->erase(0, storage->size() - maxHistorySize); // https://github.com/Artikash/Textractor/issues/127#issuecomment-486882983
	}

	std::vector<std::wstring> sentences;
	queuedSentences->swap(sentences);
	int totalSize = 0;
	for (auto& sentence : sentences)
	{
		totalSize += sentence.size();
		sentence.erase(std::remove(sentence.begin(), sentence.end(), 0), sentence.end());
		if (Output(*this, sentence)) storage->append(sentence);
	}

	std::scoped_lock lock(bufferMutex);
	if (buffer.empty()) return;
	if (buffer.size() > maxBufferSize || GetTickCount64() - lastPushTime > flushDelay)
	{
		AddSentence(std::move(buffer));
		buffer.clear();
	}
}
