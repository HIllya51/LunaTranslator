#include "textthread.h"
#include "host.h"
#include <uchardet.h>

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

struct uchardetwrapper
{
	// 其实可以用uchardet_reset，但是这样得加锁。这个的开销很小，就这样吧无所谓。
	uchardet_t ud;
	uchardetwrapper() : ud(uchardet_new()) {};
	~uchardetwrapper()
	{
		uchardet_delete(ud);
	}
	DWORD maptocodepag(const std::string &enc)
	{
		if (enc == "UTF-8")
			return CP_UTF8;
		else if (enc == "GB18030")
			return 936;
		else if (enc == "BIG5")
			return 950;
		else if (enc == "SHIFT_JIS")
			return 932;
		else if (enc == "EUC-KR" || enc == "UHC")
			return 949;
		return 0;
	}
	static inline float accept_threshold = 2.0f / 3.0f;
	DWORD detect(const std::string &s)
	{
		if (0 != uchardet_handle_data(ud, s.data(), s.size()))
			return 0;
		uchardet_data_end(ud);
		for (auto i = 0; i < uchardet_get_n_candidates(ud); i++)
		{
			auto conf = uchardet_get_confidence(ud, i);
			auto enc = uchardet_get_encoding(ud, i);
			auto codepage = maptocodepag(enc);
			printf("%f %s %d\n", conf, enc, codepage);
			if (conf >= accept_threshold)
				return codepage;
		}
		return 0;
	}
};
std::optional<DWORD> TextThread::RunDectectCodePage(BYTE *data, int length)
{
	if (hp.codepage)
		return {};
	if (hp.detectedCodepage)
		return {};
	if (!hp.isAscii())
		return {};
	UseForDetectRaw.append((const char *)data, length);
	if (UseForDetectRaw.size() < 32)
	{
		return {};
	}
	if (all_ascii(UseForDetectRaw))
	{
		UseForDetectRaw.clear();
		return {};
	}
	if (isStringUtf8(UseForDetectRaw))
	{
		hp.detectedCodepage = CP_UTF8;
	}
	else
	{
		hp.detectedCodepage = uchardetwrapper().detect(UseForDetectRaw);
		if (!hp.detectedCodepage)
			UseForDetectRaw.clear();
	}
	return hp.detectedCodepage;
}
void TextThread::Push(BYTE *data, int length)
{
	if (length < 0)
		return;
	std::scoped_lock lock(bufferMutex);

	auto hostcodepage = hp.codepage ? hp.codepage : (Host::defaultCodepage ? Host::defaultCodepage : hp.detectedCodepage);
	BYTE doubleByteChar[2];
	if (length == 1) // doublebyte characters must be processed as pairs
	{
		if (hp.isAscii() && !hostcodepage)
			return;

		if (leadByte)
		{
			doubleByteChar[0] = leadByte;
			doubleByteChar[1] = data[0];
			data = doubleByteChar;
			length = 2;
			leadByte = 0;
		}
		else if (IsDBCSLeadByteEx(hp.codepage ? hp.codepage : hostcodepage, data[0]))
		{
			leadByte = data[0];
			length = 0;
		}
	}
	if (length)
	{
		if (hp.isAscii() && !hostcodepage)
		{
			if (all_ascii((const char *)data, length))
				hostcodepage = CP_UTF8;
			else
				return;
		}

		if (auto converted = commonparsestring(data, length, &hp, hostcodepage))
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

	UpdateFlushTime();

	if (flushDelay == 0 && hp.type & FULL_STRING)
	{
		FlushBufferToQueue();
	}
}
void TextThread::FlushBufferToQueue()
{
	if (bufferDecoded.empty())
		return;
	queuedDecodedSentences->emplace_back(std::move(bufferDecoded));
	bufferDecoded.clear();
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
	auto lock = storageDecoded.Acquire();
	if (lock.contents.data.empty())
		return L"";
	return lock.contents.data.back();
}
std::wstring TextThread::GetHistoryText()
{
	std::wstring text;
	auto lock = storageDecoded.Acquire();
	for (const auto &_ : lock.contents.data)
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
	queuedDecodedSentences->swap(sentences);
	for (auto &sentence : sentences)
	{
		sentence.erase(std::remove(sentence.begin(), sentence.end(), 0), sentence.end());
		Output(*this, sentence);
		storageDecoded->push_back(maxHistorySize, std::move(sentence));
	}

	std::scoped_lock lock(bufferMutex);
	if (bufferDecoded.size() > maxBufferSize || GetTickCount64() - lastPushTime > flushDelay)
	{
		FlushBufferToQueue();
	}
}
