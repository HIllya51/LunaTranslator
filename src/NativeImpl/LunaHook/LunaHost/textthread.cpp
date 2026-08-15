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

void TextThread::AddSentence(std::wstring &&sentence)
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
			bufferDecoded.append(converted.value());
			if (hp.type & FULL_STRING && (flushDelay == 0 || (converted.value().size() > 1)))
				bufferDecoded.push_back(L'\n');
		}
		else
		{
			Host::AddConsoleOutput(TR[INVALID_CODEPAGE]);
		}
	}
	bufferRaw.append((const char *)data, length);

	UpdateFlushTime();

	if (flushDelay == 0 && hp.type & FULL_STRING)
	{
		AddSentence(std::move(bufferDecoded));
		bufferDecoded.clear();
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

std::wstring TextThread::GetLatestText()
{
	for (auto &&_ : storageDecoded->data)
	{
		return _;
	}
	return L"";
}
std::wstring TextThread::GetHistoryText()
{
	std::wstring text;
	for (auto &&_ : storageDecoded->data)
	{
		if (!text.empty())
			text += L"\n";
		text += _;
	}
	return text;
}
void TextThread::Flush()
{
	std::vector<std::wstring> sentences;
	queuedSentences->swap(sentences);
	for (auto &sentence : sentences)
	{
		sentence.erase(std::remove(sentence.begin(), sentence.end(), 0), sentence.end());
		Output(*this, sentence);
		storageDecoded->push_back(maxHistorySize, std::move(sentence));
	}

	std::scoped_lock lock(bufferMutex);
	if (bufferDecoded.empty())
		return;
	if (bufferDecoded.size() > maxBufferSize || GetTickCount64() - lastPushTime > flushDelay)
	{
		AddSentence(std::move(bufferDecoded));
		bufferDecoded.clear();
	}
}
