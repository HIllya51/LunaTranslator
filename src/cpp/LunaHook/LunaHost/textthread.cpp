#include "textthread.h"
#include "host.h"

// return true if repetition found (see https://github.com/Artikash/Textractor/issues/40)
static bool RemoveRepetition(std::wstring &text)
{
	wchar_t *end = text.data() + text.size();
	for (int length = text.size() / 3; length > 6; --length)
		if (memcmp(end - length * 3, end - length * 2, length * sizeof(wchar_t)) == 0 && memcmp(end - length * 3, end - length * 1, length * sizeof(wchar_t)) == 0)
			return RemoveRepetition(text = std::wstring(end - length, length)), true;
	return false;
}

TextThread::TextThread(ThreadParam tp, HookParam hp, std::optional<std::wstring> name) : handle(threadCounter++),
																						 name(name.value_or(StringToWideString(hp.name))),
																						 tp(tp),
																						 hp(hp)
{
}

void TextThread::Start()
{
	CreateTimerQueueTimer(&timer, NULL, [](void *This, auto)
						  { ((TextThread *)This)->Flush(); }, this, 10, 10, WT_EXECUTELONGFUNCTION);
}

void TextThread::Stop()
{
	timer = NULL;
}

void TextThread::AddSentence(std::wstring sentence)
{
	queuedSentences->emplace_back(std::move(sentence));
}

void TextThread::Push(BYTE *data, int length)
{
	if (length < 0)
		return;
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
	if (length)
	{
		if (auto converted = commonparsestring(data, length, &hp, Host::defaultCodepage))
		{
			buffer.append(converted.value());
			if (hp.type & FULL_STRING && converted.value().size() > 1)
				buffer.push_back(L'\n');
		}
		else
		{
			Host::AddConsoleOutput(TR[INVALID_CODEPAGE]);
		}
	}

	UpdateFlushTime();

	if (filterRepetition)
	{
		if (std::all_of(buffer.begin(), buffer.end(), [&](wchar_t ch)
						{ return repeatingChars.count(ch); }))
			buffer.clear();
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
void TextThread::UpdateFlushTime(bool recursive)
{
	lastPushTime = GetTickCount64();
	if (!recursive)
		return;
	auto &&ths = syncThreads.Acquire().contents;
	if (!ths.count(this))
		return;
	for (auto t : ths)
	{
		if (t == this)
			continue;
		t->UpdateFlushTime(false);
	}
}
void TextThread::Push(const wchar_t *data)
{
	std::scoped_lock lock(bufferMutex);
	// not sure if this should filter repetition
	UpdateFlushTime();
	buffer += data;
}

void TextThread::Flush()
{
	{
		auto storage = this->storage.Acquire();
		if (storage->size() > maxHistorySize)
			storage->erase(0, storage->size() - maxHistorySize); // https://github.com/Artikash/Textractor/issues/127#issuecomment-486882983
	}

	std::vector<std::wstring> sentences;
	queuedSentences->swap(sentences);
	for (auto &sentence : sentences)
	{
		sentence.erase(std::remove(sentence.begin(), sentence.end(), 0), sentence.end());
		Output(*this, sentence);
		storage->append(sentence + L"\n");
		latest->assign(sentence.c_str());
	}

	std::scoped_lock lock(bufferMutex);
	if (buffer.empty())
		return;
	if (buffer.size() > maxBufferSize || GetTickCount64() - lastPushTime > flushDelay)
	{
		AddSentence(std::move(buffer));
		buffer.clear();
	}
}
