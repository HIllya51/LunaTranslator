#include "qtcommon.h"
#include "network.h"

namespace DevTools
{
	void Initialize();
	void Close();
	bool Connected();
	JSON::Value<wchar_t> SendRequest(const char* method, const std::wstring& params = L"{}");
}
